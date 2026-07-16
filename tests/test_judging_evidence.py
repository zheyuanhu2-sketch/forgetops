from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_verifier() -> ModuleType:
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_judging_evidence.py"
    spec = importlib.util.spec_from_file_location("verify_judging_evidence", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_judging_evidence_bundle_is_internally_consistent() -> None:
    checks = load_verifier().verify()

    assert len(checks) == 6
    assert any("fresh-session read-back" in check for check in checks)
