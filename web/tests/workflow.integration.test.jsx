import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { App } from "../src/App.jsx";

describe("ForgetOps case workflow", () => {
  it("requires two explicit approvals and preserves protected outcomes", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByText("7 assets discovered · 6 lineage edges")).toBeInTheDocument();
    expect(screen.getByText("0 raw identifiers in audit")).toBeInTheDocument();
    expect(screen.getByText("1 legal hold")).toBeInTheDocument();
    expect(screen.getByText("1 manual review")).toBeInTheDocument();

    const authorizeExecution = screen.getByRole("button", { name: "Authorize execution" });
    expect(authorizeExecution).toBeDisabled();

    await user.click(
      screen.getByRole("checkbox", {
        name: "Protected outcomes reviewed: legal hold retained; model feature requires human review.",
      }),
    );
    expect(authorizeExecution).toBeEnabled();
    await user.click(authorizeExecution);

    expect(screen.getByRole("button", { name: "Execution in progress" })).toBeDisabled();

    await waitFor(
      () => {
        expect(screen.getByText("Write-back approval")).toBeInTheDocument();
      },
      { timeout: 3500 },
    );

    expect(screen.getByText("5 / 5 mutation receipts")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve DataHub write-back" })).toBeDisabled();
    expect(screen.getAllByText("Retained — legal hold", { exact: false }).length).toBeGreaterThan(
      0,
    );
    expect(
      screen.getAllByText("Manual review — not modified", { exact: false }).length,
    ).toBeGreaterThan(0);

    await user.click(
      screen.getByRole("checkbox", {
        name: "Verification reviewed: 5 cleared, 1 retained, 1 pending human review.",
      }),
    );
    const approveWriteback = screen.getByRole("button", {
      name: "Approve DataHub write-back",
    });
    expect(approveWriteback).toBeEnabled();
    await user.click(approveWriteback);

    expect(screen.getByText("Fresh DataHub read-back verified")).toBeInTheDocument();
    expect(screen.getByText("7 entities read back fresh")).toBeInTheDocument();
    expect(
      screen.getByText("Partial verification is a truthful result, not a hidden failure."),
    ).toBeInTheDocument();
  });

  it("opens the evidence contract without changing workflow state", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "View details" }));
    expect(
      screen.getByRole("dialog", { name: "Write, then verify from a fresh session." }),
    ).toBeInTheDocument();
    expect(screen.getByText("Same URN reused on idempotent retry")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Close evidence details" })).toHaveFocus();

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "View details" })).toHaveFocus();
    expect(screen.getByRole("button", { name: "Authorize execution" })).toBeDisabled();
  });
});
