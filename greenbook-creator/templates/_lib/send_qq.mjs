// Send greenbook cards to QQ bot C2C user via openclaw-qqbot API.
// Uses underlying API because CLI's messageId is empty when sendMedia succeeds
// (see MEMORY: "openclaw CLI messageId 空 = 没真发" — 2026-07-25).
//
// Usage:
//   send_qq.mjs --config /path/to/config.json
//   send_qq.mjs --config ./config.json --only 8        # resend a single card
//   send_qq.mjs --config ./config.json --img-dir out    # override image dir
//
// config.json schema:
//   {
//     "openid":      "QQ bot recipient openid",
//     "img_dir":     "images" (default, relative to config.json),
//     "cover_text":  "Lead text sent before the carousel",
//     "captions":    ["01/08 ...", "02/08 ...", ...]   // len must match card_N.png count
//   }

import { getAccessToken, sendC2CImageMessage, sendC2CMessage } from "/usr/lib/node_modules/openclaw-qqbot/dist/src/api.js";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const args = { only: null, imgDir: null, config: null };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--config") args.config = argv[++i];
    else if (a === "--img-dir") args.imgDir = argv[++i];
    else if (a === "--only") {
      const v = parseInt(argv[++i], 10);
      if (!Number.isInteger(v) || v < 1) throw new Error("--only must be a positive integer");
      args.only = v;
    }
    else throw new Error(`unknown arg: ${a}`);
  }
  if (!args.config) throw new Error("--config required (path to config.json)");
  return args;
}

function loadConfig(configPath) {
  const cfg = JSON.parse(fs.readFileSync(configPath, "utf8"));
  for (const k of ["openid", "cover_text", "captions"]) {
    if (cfg[k] === undefined) throw new Error(`config.${k} required`);
  }
  if (!Array.isArray(cfg.captions)) throw new Error("config.captions must be an array");
  return cfg;
}

function loadQqCredentials() {
  const authPath = "/home/ubuntu/.openclaw/openclaw.json";
  const auth = JSON.parse(fs.readFileSync(authPath, "utf8"));
  const qq = auth.channels?.qqbot;
  if (!qq?.appId || !qq?.clientSecret) {
    throw new Error("Missing qqbot credentials in " + authPath);
  }
  return qq;
}

async function sendOne(token, openid, imgPath, caption) {
  console.log(`  image: ${imgPath}`);
  const buf = fs.readFileSync(imgPath);
  const dataUrl = `data:image/png;base64,${buf.toString("base64")}`;
  const r = await sendC2CImageMessage(token, openid, dataUrl);
  console.log(`    image id: ${r?.id || "(none)"}`);
  await new Promise(res => setTimeout(res, 1200));
  const rt = await sendC2CMessage(token, openid, caption);
  console.log(`    caption id: ${rt?.id || "(none)"}`);
  await new Promise(res => setTimeout(res, 2000));
}

async function main() {
  const args = parseArgs(process.argv);
  const cfgPath = path.resolve(args.config);
  const cfg = loadConfig(cfgPath);
  const qq = loadQqCredentials();

  const imgDir = args.imgDir
    ? path.resolve(args.imgDir)
    : path.resolve(path.dirname(cfgPath), cfg.img_dir || "images");

  if (!fs.existsSync(imgDir)) throw new Error(`img_dir not found: ${imgDir}`);

  console.log("Getting QQ bot access token...");
  const token = await getAccessToken(qq.appId, qq.clientSecret);
  console.log("Token acquired");
  console.log(`  openid: ${cfg.openid}`);
  console.log(`  img_dir: ${imgDir}`);
  console.log(`  cards: ${cfg.captions.length}`);

  const indices = args.only !== null
    ? [args.only - 1]
    : Array.from({ length: cfg.captions.length }, (_, i) => i);

  // Cover text (skipped on --only)
  if (args.only === null) {
    console.log("\n[cover] sending lead text...");
    const r0 = await sendC2CMessage(token, cfg.openid, cfg.cover_text);
    console.log(`  cover id: ${r0?.id || "(none)"}`);
    await new Promise(res => setTimeout(res, 2500));
  } else {
    console.log(`\n(--only ${args.only}: skipping cover text)`);
  }

  for (const i of indices) {
    const n = i + 1;
    const imgPath = path.join(imgDir, `card_${n}.png`);
    if (!fs.existsSync(imgPath)) {
      throw new Error(`missing image for card ${n}: ${imgPath}`);
    }
    console.log(`\n[${n}/${cfg.captions.length}]`);
    await sendOne(token, cfg.openid, imgPath, cfg.captions[i]);
  }

  console.log(`\n✅ Done (${indices.length} card${indices.length > 1 ? "s" : ""} sent)`);
}

main().catch(e => {
  console.error("Fatal:", e.message || e);
  process.exit(1);
});