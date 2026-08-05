// Send qm-greenbook cards via shared _lib/send_qq.mjs
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const LIB    = resolve(__dirname, "..", "..", "_lib", "send_qq.mjs");
const CONFIG = resolve(__dirname, "..", "config.json");

execFileSync(
  "node",
  [LIB, "--config", CONFIG, ...process.argv.slice(2)],
  { stdio: "inherit" }
);