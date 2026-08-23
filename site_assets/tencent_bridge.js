/* 文雪求职小窝 · 快捷操作中转站（腾讯云 SCF Web 函数）
 * 把本代码粘到 src/app.js（不要动 scf_bootstrap）
 * 环境变量：GITHUB_TOKEN、APP_KEY */
'use strict';
const http = require("http");
const REPO = "WenXue-10/SCM-Career-Dashboard";
const BRANCH = "main";
const ALLOWED_STATUS = { ready:"📮 待投递", sent:"✉️ 已投递", interview:"📞 面试中", dead:"❌ 已挂", backup:"🗂️ 备选", done:"✅ 已背调" };
const CORS = { "Access-Control-Allow-Origin":"*", "Access-Control-Allow-Methods":"POST, OPTIONS", "Access-Control-Allow-Headers":"Content-Type", "Content-Type":"application/json" };
function decodeB64(s){ return Buffer.from(s, "base64").toString("utf8"); }
function encodeB64(s){ return Buffer.from(s, "utf8").toString("base64"); }
function updateFM(content, val){
  const m = /^---\s*\n([\s\S]*?)\n---/.exec(content);
  if (!m) return null;
  const fm = m[1];
  const n = fm.replace(/^(当前状态\s*:\s*).*$/m, "$1" + val);
  if (n === fm) return null;
  return content.slice(0, m.index) + "---\n" + n + "\n---" + content.slice(m.index + m[0].length);
}
function send(res, code, obj){ res.writeHead(code, CORS); res.end(JSON.stringify(obj)); }
async function handle(req, res){
  if (req.method === "OPTIONS") { send(res, 200, { ok:true }); return; }
  if (req.method !== "POST") { send(res, 405, { ok:false, error:"method" }); return; }
  let raw = "";
  for await (const chunk of req) raw += chunk;
  let body;
  try { body = JSON.parse(raw || "{}"); } catch (e) { send(res, 400, { ok:false, error:"bad json" }); return; }
  const APP_KEY = process.env.APP_KEY, GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  if (!APP_KEY || body.key !== APP_KEY) { send(res, 403, { ok:false, error:"forbidden" }); return; }
  const file = String(body.file || ""), status = String(body.status || "");
  if (!file.startsWith("01_岗位搜集与背调/公司调研/") || !file.endsWith(".md") || file.includes("..")) { send(res, 400, { ok:false, error:"bad file" }); return; }
  if (!ALLOWED_STATUS[status]) { send(res, 400, { ok:false, error:"bad status" }); return; }
  const newValue = ALLOWED_STATUS[status];
  const H = { Authorization:"token " + GITHUB_TOKEN, "User-Agent":"scm-site", Accept:"application/vnd.github+json" };
  const enc = encodeURIComponent(file);
  try {
    const getRes = await fetch("https://api.github.com/repos/" + REPO + "/contents/" + enc + "?ref=" + BRANCH, { headers: H });
    if (!getRes.ok) { send(res, 502, { ok:false, error:"read fail " + getRes.status }); return; }
    const meta = await getRes.json();
    const content = decodeB64(meta.content);
    const updated = updateFM(content, newValue);
    if (!updated) { send(res, 422, { ok:false, error:"frontmatter not found" }); return; }
    if (updated === content) { send(res, 200, { ok:true, noChange:true, status:newValue }); return; }
    const putRes = await fetch("https://api.github.com/repos/" + REPO + "/contents/" + enc, {
      method: "PUT",
      headers: Object.assign({}, H, { "Content-Type":"application/json" }),
      body: JSON.stringify({ message:"快捷操作：" + file.split("/").slice(-2,-1)[0] + " 状态 → " + newValue, content: encodeB64(updated), sha: meta.sha, branch: BRANCH })
    });
    if (!putRes.ok) { send(res, 502, { ok:false, error:"write fail " + putRes.status }); return; }
    send(res, 200, { ok:true, status:newValue });
  } catch (e) { send(res, 500, { ok:false, error:"server error" }); }
}
http.createServer(handle).listen(9000);
console.log("scm-bridge listening on 9000");