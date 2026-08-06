import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import path from "node:path";

function root() {
  return path.resolve(__dirname, "..");
}

function needsPowerBiValidation(filePath: unknown) {
  if (typeof filePath !== "string") return false;
  const p = filePath.replace(/\\/g, "/");
  return p.endsWith(".tmdl") || p.endsWith(".pbir") || (p.endsWith(".json") && p.includes(".Report/"));
}

export default function (pi: ExtensionAPI) {
  const doctorScript = path.join(root(), "scripts", "doctor.mjs");
  const validateScript = path.join(root(), "scripts", "validate-pbip.mjs");

  pi.registerCommand("powerbi-doctor", {
    description: "Check optional local Power BI tooling",
    handler: async (_args, ctx) => {
      const result = await pi.exec("node", [doctorScript], { timeout: 30_000 });
      const output = `${result.stdout || ""}${result.stderr || ""}`.trim() || "No output";
      if (ctx.hasUI) ctx.ui.notify("Power BI doctor finished", result.code === 0 ? "info" : "warning");
      pi.sendMessage({ customType: "powerbi-doctor", content: output, display: true, details: { code: result.code } });
    },
  });

  pi.registerCommand("powerbi-validate", {
    description: "Validate PBIP/PBIR/TMDL files in this project",
    handler: async (args, ctx) => {
      const target = args?.trim() || ".";
      const result = await pi.exec("node", [validateScript, target], { timeout: 60_000 });
      const output = `${result.stdout || ""}${result.stderr || ""}`.trim() || "No output";
      const level = result.code === 0 ? "info" : result.code === 1 ? "warning" : "error";
      if (ctx.hasUI) ctx.ui.notify("Power BI validation finished", level);
      pi.sendMessage({ customType: "powerbi-validation", content: output, display: true, details: { code: result.code, target } });
    },
  });

  pi.on("tool_result", async (event) => {
    if (event.toolName !== "write" && event.toolName !== "edit") return undefined;
    const filePath = (event.input as { path?: unknown }).path;
    if (!needsPowerBiValidation(filePath)) return undefined;

    const result = await pi.exec("node", [validateScript, "--changed", String(filePath)], { timeout: 30_000 });
    if (result.code === 0) return undefined;

    const output = `${result.stdout || ""}${result.stderr || ""}`.trim();
    return {
      isError: result.code === 2,
      content: [
        {
          type: "text",
          text: `Power BI validation ${result.code === 2 ? "failed" : "warning"} for ${filePath}\n\n${output}`,
        },
      ],
      details: { code: result.code, filePath },
    };
  });
}
