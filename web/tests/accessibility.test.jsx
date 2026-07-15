import axe from "axe-core";
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "../src/App.jsx";

describe("ForgetOps accessibility baseline", () => {
  it("has no serious or critical automated semantic violations", async () => {
    const { container } = render(<App />);
    const result = await axe.run(container, {
      rules: {
        "color-contrast": { enabled: false },
      },
    });
    const blockingViolations = result.violations.filter(
      (violation) => violation.impact === "serious" || violation.impact === "critical",
    );

    expect(blockingViolations).toEqual([]);
  });
});
