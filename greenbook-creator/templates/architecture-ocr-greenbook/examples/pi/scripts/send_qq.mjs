// Send pi example cards via shared _lib/send_qq.mjs.
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
// examples/pi/scripts/send_qq.mjs → templates/_lib/send_qq.mjs (5 levels up: scripts → pi → examples → architecture-ocr-greenbook → templates)
const LIB    = resolve(__dirname, "..", "..", "..", "..", "_lib", "send_qq.mjs");
const CONFIG = resolve(__dirname, "..", "config.json");

execFileSync("node", [LIB, "--config", CONFIG, ...process.argv.slice(2)], { stdio: "inherit" });