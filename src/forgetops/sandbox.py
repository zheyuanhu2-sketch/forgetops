"""Transactional DuckDB sandbox execution with approval and audit evidence."""

from __future__ import annotations

import re
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import TypeAlias

import duckdb
from pydantic import Field, model_validator

from forgetops.models import (
    ErasurePlan,
    ErasureRequest,
    HandlingRule,
    PlannedAction,
    StrictModel,
)

Scalar: TypeAlias = str | int | float | bool | None
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
LEDGER_TABLE = "forgetops_execution_log"


class SandboxExecutionError(RuntimeError):
    """Raised when an approved sandbox run cannot complete atomically."""


class SubjectReferenceMismatch(PermissionError):
    """Raised when the in-memory subject does not match the approved plan."""


class ExecutionStatus(StrEnum):
    DRY_RUN = "dry_run"
    VERIFIED = "verified"
    PARTIAL_VERIFIED = "partial_verified"


class ActionOutcome(StrEnum):
    WOULD_EXECUTE = "would_execute"
    DELETED = "deleted"
    ANONYMIZED = "anonymized"
    REFRESHED = "refreshed"
    RETAINED = "retained"
    REVIEW_PENDING = "review_pending"


class SandboxTable(StrictModel):
    asset_urn: str = Field(pattern=r"^urn:li:")
    relation: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    subject_key: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    rows: list[dict[str, Scalar]] = Field(min_length=1)

    @model_validator(mode="after")
    def rows_share_a_safe_schema(self) -> SandboxTable:
        columns = set(self.rows[0])
        if self.subject_key not in columns:
            raise ValueError("subject_key must be present in sandbox rows")
        if any(not IDENTIFIER_PATTERN.fullmatch(column) for column in columns):
            raise ValueError("sandbox column names must be safe SQL identifiers")
        if any(set(row) != columns for row in self.rows):
            raise ValueError("all sandbox rows must share the same columns")
        return self


class SandboxScenario(StrictModel):
    scenario_id: str = Field(min_length=3)
    tables: list[SandboxTable] = Field(min_length=1)

    @model_validator(mode="after")
    def targets_are_unique(self) -> SandboxScenario:
        urns = [table.asset_urn for table in self.tables]
        relations = [table.relation for table in self.tables]
        if len(set(urns)) != len(urns):
            raise ValueError("sandbox asset URNs must be unique")
        if len(set(relations)) != len(relations):
            raise ValueError("sandbox relations must be unique")
        return self


class BootstrapReceipt(StrictModel):
    scenario_id: str
    applied: bool
    database_path: str
    table_count: int = Field(ge=0)
    row_count: int = Field(ge=0)


class ActionExecution(StrictModel):
    sequence: int = Field(ge=1)
    asset_urn: str
    action: HandlingRule
    outcome: ActionOutcome
    before_matches: int = Field(ge=0)
    after_matches: int = Field(ge=0)
    verified: bool
    evidence: list[str] = Field(min_length=1)


class ExecutionReceipt(StrictModel):
    request_id: str
    subject_ref: str = Field(pattern=r"^sha256:[0-9a-f]{16}$")
    plan_ref: str = Field(pattern=r"^sha256:[0-9a-f]{16}$")
    idempotency_key: str = Field(min_length=3, max_length=160)
    status: ExecutionStatus
    approved: bool
    replayed: bool = False
    completed_at: datetime
    scenario_id: str
    actions: list[ActionExecution] = Field(min_length=1)
    verified_actions: int = Field(ge=0)
    exception_actions: int = Field(ge=0)


def load_scenario(path: Path) -> SandboxScenario:
    return SandboxScenario.model_validate_json(path.read_text(encoding="utf-8"))


def bootstrap_sandbox(
    scenario: SandboxScenario,
    database_path: Path,
    *,
    approved: bool = False,
    overwrite: bool = False,
) -> BootstrapReceipt:
    """Create the synthetic warehouse only after explicit approval."""

    receipt = BootstrapReceipt(
        scenario_id=scenario.scenario_id,
        applied=False,
        database_path=str(database_path),
        table_count=len(scenario.tables),
        row_count=sum(len(table.rows) for table in scenario.tables),
    )
    if not approved:
        return receipt
    if database_path.exists() and not overwrite:
        raise SandboxExecutionError(
            f"sandbox database already exists: {database_path}; use overwrite=True explicitly"
        )

    database_path.parent.mkdir(parents=True, exist_ok=True)
    if database_path.exists():
        database_path.unlink()
    connection = duckdb.connect(str(database_path))
    try:
        connection.execute("BEGIN TRANSACTION")
        _create_ledger(connection)
        for table in scenario.tables:
            columns = sorted(table.rows[0])
            definition = ", ".join(f"{_quote(column)} VARCHAR" for column in columns)
            connection.execute(f"CREATE TABLE {_quote(table.relation)} ({definition})")
            placeholders = ", ".join("?" for _ in columns)
            insert_sql = (
                f"INSERT INTO {_quote(table.relation)} "
                f"({', '.join(_quote(column) for column in columns)}) VALUES ({placeholders})"
            )
            connection.executemany(
                insert_sql,
                [[_to_database_value(row[column]) for column in columns] for row in table.rows],
            )
        connection.execute("COMMIT")
    except Exception:
        try:
            connection.execute("ROLLBACK")
        finally:
            connection.close()
            database_path.unlink(missing_ok=True)
        raise
    else:
        connection.close()

    return receipt.model_copy(update={"applied": True})


class SandboxExecutor:
    """Apply an erasure plan atomically to an allowlisted synthetic warehouse."""

    def __init__(self, now: Callable[[], datetime] | None = None) -> None:
        self._now = now or (lambda: datetime.now(UTC))

    def execute(
        self,
        plan: ErasurePlan,
        scenario: SandboxScenario,
        database_path: Path,
        *,
        subject_id: str,
        idempotency_key: str,
        approved: bool = False,
    ) -> ExecutionReceipt:
        if len(idempotency_key.strip()) < 3:
            raise ValueError("idempotency_key must contain at least three characters")
        subject_ref = ErasureRequest.from_subject_id(
            request_id=plan.request.request_id,
            subject_id=subject_id,
        ).subject_ref
        plan_ref = _plan_reference(plan)
        if subject_ref != plan.request.subject_ref:
            raise SubjectReferenceMismatch("subject identifier does not match the approved plan")
        if not database_path.exists():
            raise SandboxExecutionError(f"sandbox database does not exist: {database_path}")

        targets = {table.asset_urn: table for table in scenario.tables}
        connection = duckdb.connect(str(database_path), read_only=not approved)
        try:
            if approved:
                replay = self._load_replay(
                    connection,
                    idempotency_key=idempotency_key,
                    request_id=plan.request.request_id,
                    subject_ref=subject_ref,
                    plan_ref=plan_ref,
                    scenario_id=scenario.scenario_id,
                )
                if replay is not None:
                    return replay
                connection.execute("BEGIN TRANSACTION")

            actions = [
                self._execute_action(
                    connection,
                    action=action,
                    target=targets.get(action.asset_urn),
                    subject_id=subject_id,
                    subject_ref=subject_ref,
                    approved=approved,
                )
                for action in plan.actions
            ]
            exceptions = sum(
                action.outcome in {ActionOutcome.RETAINED, ActionOutcome.REVIEW_PENDING}
                for action in actions
            )
            status = (
                ExecutionStatus.DRY_RUN
                if not approved
                else ExecutionStatus.PARTIAL_VERIFIED
                if exceptions
                else ExecutionStatus.VERIFIED
            )
            receipt = ExecutionReceipt(
                request_id=plan.request.request_id,
                subject_ref=subject_ref,
                plan_ref=plan_ref,
                idempotency_key=idempotency_key,
                status=status,
                approved=approved,
                completed_at=self._now(),
                scenario_id=scenario.scenario_id,
                actions=actions,
                verified_actions=sum(action.verified for action in actions),
                exception_actions=exceptions,
            )
            if approved:
                connection.execute(
                    f"INSERT INTO {LEDGER_TABLE} VALUES (?, ?, ?, ?, ?)",
                    [
                        idempotency_key,
                        plan.request.request_id,
                        subject_ref,
                        receipt.model_dump_json(),
                        receipt.completed_at,
                    ],
                )
                connection.execute("COMMIT")
            return receipt
        except Exception as error:
            if approved:
                with suppress(duckdb.Error):
                    connection.execute("ROLLBACK")
            if isinstance(error, (SandboxExecutionError, SubjectReferenceMismatch, ValueError)):
                raise
            raise SandboxExecutionError(f"sandbox execution rolled back: {error}") from error
        finally:
            connection.close()

    def _execute_action(
        self,
        connection: duckdb.DuckDBPyConnection,
        *,
        action: PlannedAction,
        target: SandboxTable | None,
        subject_id: str,
        subject_ref: str,
        approved: bool,
    ) -> ActionExecution:
        if action.action is HandlingRule.REFRESH:
            return ActionExecution(
                sequence=action.sequence,
                asset_urn=action.asset_urn,
                action=action.action,
                outcome=ActionOutcome.WOULD_EXECUTE if not approved else ActionOutcome.REFRESHED,
                before_matches=0,
                after_matches=0,
                verified=approved,
                evidence=["Synthetic dashboard cache refresh is isolated from source rows."],
            )
        if target is None:
            raise SandboxExecutionError(f"no sandbox target configured for {action.asset_urn}")

        before = _subject_count(connection, target, subject_id)
        if action.blocked or action.action is HandlingRule.RETAIN:
            return ActionExecution(
                sequence=action.sequence,
                asset_urn=action.asset_urn,
                action=action.action,
                outcome=ActionOutcome.RETAINED,
                before_matches=before,
                after_matches=before,
                verified=True,
                evidence=["No mutation executed; DataHub legal-hold policy remains authoritative."],
            )
        if action.action is HandlingRule.REVIEW:
            return ActionExecution(
                sequence=action.sequence,
                asset_urn=action.asset_urn,
                action=action.action,
                outcome=ActionOutcome.REVIEW_PENDING,
                before_matches=before,
                after_matches=before,
                verified=True,
                evidence=["No mutation executed; downstream model review remains open."],
            )
        if not approved:
            return ActionExecution(
                sequence=action.sequence,
                asset_urn=action.asset_urn,
                action=action.action,
                outcome=ActionOutcome.WOULD_EXECUTE,
                before_matches=before,
                after_matches=before,
                verified=False,
                evidence=["Dry run only; explicit approval is required before mutation."],
            )

        columns = _relation_columns(connection, target.relation)
        missing_fields = sorted(set(action.fields) - columns)
        if missing_fields:
            raise SandboxExecutionError(
                f"sandbox relation {target.relation} is missing planned fields: {missing_fields}"
            )

        if action.action is HandlingRule.DELETE:
            connection.execute(
                f"DELETE FROM {_quote(target.relation)} WHERE {_quote(target.subject_key)} = ?",
                [subject_id],
            )
            outcome = ActionOutcome.DELETED
        elif action.action is HandlingRule.ANONYMIZE:
            pseudonym = f"anon_{sha256(subject_ref.encode()).hexdigest()[:16]}"
            assignments: list[str] = []
            parameters: list[str] = []
            for field in sorted(set(action.fields)):
                assignments.append(f"{_quote(field)} = ?")
                parameters.append(pseudonym if field == target.subject_key else "[REDACTED]")
            parameters.append(subject_id)
            connection.execute(
                f"UPDATE {_quote(target.relation)} SET {', '.join(assignments)} "
                f"WHERE {_quote(target.subject_key)} = ?",
                parameters,
            )
            outcome = ActionOutcome.ANONYMIZED
        else:
            raise SandboxExecutionError(f"unsupported sandbox action: {action.action.value}")

        after = _subject_count(connection, target, subject_id)
        if after != 0:
            raise SandboxExecutionError(
                f"post-action verification failed for {target.relation}: "
                f"{after} subject rows remain"
            )
        return ActionExecution(
            sequence=action.sequence,
            asset_urn=action.asset_urn,
            action=action.action,
            outcome=outcome,
            before_matches=before,
            after_matches=after,
            verified=True,
            evidence=[
                f"Parameterized DuckDB mutation completed for {before} matching synthetic row(s).",
                "Post-action query found zero rows for the raw subject identifier.",
            ],
        )

    @staticmethod
    def _load_replay(
        connection: duckdb.DuckDBPyConnection,
        *,
        idempotency_key: str,
        request_id: str,
        subject_ref: str,
        plan_ref: str,
        scenario_id: str,
    ) -> ExecutionReceipt | None:
        row = connection.execute(
            f"SELECT request_id, subject_ref, receipt_json FROM {LEDGER_TABLE} "
            "WHERE idempotency_key = ?",
            [idempotency_key],
        ).fetchone()
        if row is None:
            return None
        if row[0] != request_id or row[1] != subject_ref:
            raise SandboxExecutionError("idempotency key is already bound to another request")
        receipt = ExecutionReceipt.model_validate_json(str(row[2]))
        if receipt.plan_ref != plan_ref or receipt.scenario_id != scenario_id:
            raise SandboxExecutionError(
                "idempotency key is already bound to another plan or scenario"
            )
        return receipt.model_copy(update={"replayed": True})


def write_execution_receipt(receipt: ExecutionReceipt, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(receipt.model_dump_json(indent=2), encoding="utf-8")


def render_execution_markdown(receipt: ExecutionReceipt) -> str:
    lines = [
        f"# ForgetOps execution evidence — {receipt.request_id}",
        "",
        f"- Status: **{receipt.status.value}**",
        f"- Approved: **{str(receipt.approved).lower()}**",
        f"- Replayed: **{str(receipt.replayed).lower()}**",
        f"- Subject reference: `{receipt.subject_ref}`",
        f"- Plan reference: `{receipt.plan_ref}`",
        f"- Idempotency key: `{receipt.idempotency_key}`",
        f"- Scenario: `{receipt.scenario_id}`",
        "",
        "## Action verification",
        "",
        "| # | Action | Outcome | Before | After | Verified |",
        "|---:|---|---|---:|---:|:---:|",
    ]
    for action in receipt.actions:
        lines.append(
            f"| {action.sequence} | `{action.action.value}` | `{action.outcome.value}` | "
            f"{action.before_matches} | {action.after_matches} | "
            f"{'yes' if action.verified else 'no'} |"
        )
    lines.extend(["", "## Evidence", ""])
    for action in receipt.actions:
        lines.append(f"### {action.sequence}. `{action.asset_urn}`")
        lines.extend(f"- {item}" for item in action.evidence)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _create_ledger(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        f"CREATE TABLE {LEDGER_TABLE} ("
        "idempotency_key VARCHAR PRIMARY KEY, "
        "request_id VARCHAR NOT NULL, "
        "subject_ref VARCHAR NOT NULL, "
        "receipt_json VARCHAR NOT NULL, "
        "completed_at TIMESTAMPTZ NOT NULL)"
    )


def _plan_reference(plan: ErasurePlan) -> str:
    digest = sha256(plan.model_dump_json().encode("utf-8")).hexdigest()[:16]
    return f"sha256:{digest}"


def _subject_count(
    connection: duckdb.DuckDBPyConnection,
    target: SandboxTable,
    subject_id: str,
) -> int:
    row = connection.execute(
        f"SELECT COUNT(*) FROM {_quote(target.relation)} WHERE {_quote(target.subject_key)} = ?",
        [subject_id],
    ).fetchone()
    if row is None:
        raise SandboxExecutionError(f"unable to count subject rows in {target.relation}")
    return int(row[0])


def _relation_columns(connection: duckdb.DuckDBPyConnection, relation: str) -> set[str]:
    rows = connection.execute(f"DESCRIBE {_quote(relation)}").fetchall()
    return {str(row[0]) for row in rows}


def _quote(identifier: str) -> str:
    if not IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"unsafe SQL identifier: {identifier}")
    return f'"{identifier}"'


def _to_database_value(value: Scalar) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
