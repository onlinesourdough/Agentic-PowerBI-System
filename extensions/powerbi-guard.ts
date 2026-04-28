import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import path from "node:path";

function packageRoot() {
  return path.resolve(__dirname, "..");
}

function shouldValidateFile(filePath: unknown) {
  if (typeof filePath !== "string") return false;
  const p = filePath.replace(/\\/g, "/");
  return (
    p.endsWith(".tmdl") ||
    p.endsWith(".pbir") ||
    (p.endsWith(".json") && (p.includes(".Report/") || p.includes(".SemanticModel/")))
  );
}

export default function (pi: ExtensionAPI) {
  const validateScript = path.join(packageRoot(), "scripts", "validate-pbip.mjs");
  const doctorScript = path.join(packageRoot(), "scripts", "doctor.mjs");

  pi.registerCommand("powerbi-doctor", {
    description: "Check recommended local Power BI / Fabric / PBIP toolchain",
    handler: async (_args, ctx) => {
      const result = await pi.exec("node", [doctorScript], { timeout: 30_000, signal: ctx.signal });
      const text = `${result.stdout || ""}${result.stderr || ""}`.trim();
      if (ctx.hasUI) ctx.ui.notify(result.code === 0 ? "Power BI doctor completed" : "Power BI doctor found missing required tools", result.code === 0 ? "info" : "warning");
      pi.sendMessage({ customType: "powerbi-doctor", content: text || "No output", display: true, details: { code: result.code } }, { deliverAs: "nextTurn" });
    },
  });

  pi.registerCommand("powerbi-validate", {
    description: "Validate PBIP/PBIR/TMDL structure in the current project or given path",
    handler: async (args, ctx) => {
      const target = args?.trim() || ".";
      const result = await pi.exec("node", [validateScript, target], { timeout: 60_000, signal: ctx.signal });
      const text = `${result.stdout || ""}${result.stderr || ""}`.trim();
      const level = result.code === 0 ? "info" : result.code === 1 ? "warning" : "error";
      if (ctx.hasUI) ctx.ui.notify(`Power BI validation finished (${result.code})`, level);
      pi.sendMessage({ customType: "powerbi-validation", content: text || "No output", display: true, details: { code: result.code, target } }, { deliverAs: "nextTurn" });
    },
  });

  pi.on("tool_result", async (event, ctx) => {
    if (event.toolName !== "write" && event.toolName !== "edit") return undefined;
    const filePath = (event.input as { path?: unknown }).path;
    if (!shouldValidateFile(filePath)) return undefined;

    const result = await pi.exec("node", [validateScript, "--changed", String(filePath)], {
      timeout: 30_000,
      signal: ctx.signal,
    });

    if (result.code === 0) return undefined;
    const text = `${result.stdout || ""}${result.stderr || ""}`.trim();
    return {
      isError: result.code === 2,
      content: [
        {
          type: "text",
          text: `Power BI guard validation ${result.code === 2 ? "failed" : "warning"} for ${filePath}\n\n${text}`,
        },
      ],
      details: { code: result.code, filePath },
    };
  });
}
