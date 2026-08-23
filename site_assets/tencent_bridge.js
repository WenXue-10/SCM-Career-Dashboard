/* 文雪求职小窝 · 快捷操作中转站（腾讯云函数 SCF · Web 函数）
 * 运行环境：Nodejs 18.15（自带 fetch）
 * 环境变量：GITHUB_TOKEN（GitHub 令牌）、APP_KEY（站点钥匙 XNTbRx7spQJHDGWfKjchz8iSL2OIwoFY） */
'use strict';
const REPO = "WenXue-10/SCM-Career-Dashboard";
const BRANCH = "main";
const ALLOWED_STATUS = { ready:"📮 待投递", sent:"✉️ 已投递", interview:"📞 面试中", dead:"❌ 已挂", backup:"🗂️ 备选", done:"✅ 已背调" };
const CORS = { "Access-Control-Allow-Origin":"*", "Access-Control-Allow-Methods":"POST, OPTIONS", "Access-Control-Allow-Headers":"Content-Type" };
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
function resp(status, obj){ return { statusCode: status, headers: CORS, body: JSON.stringify(obj) }; }

exports.main_handler = async (event, context) => {
  const method = (event.httpMethod || (event.requestContext && event.requestContext.http && event.requestContext.http.method) || "").toUpperCase();
  if (method === "OPTIONS") return resp(200, { ok: true });
  if (method !== "POST") return resp(405, { ok:false, error:"method" });
  let body;
  try {
    let raw = event.body;
    if (typeof raw !== "string") raw = JSON.stringify(raw || {});
    body = JSON.parse(raw);
  } catch (e) { return resp(400, { ok:false, error:"bad json" }); }
  const APP_KEY = process.env.APP_KEY, GITHUB_TOKEN = process.env.GITHUB_TOKEN;
  if (!APP_KEY || body.key !== APP_KEY) return resp(403, { ok:false, error:"forbidden" });
  const file = String(body.file || ""), status = String(body.status || "");
  if (!file.startsWith("01_岗位搜集与背调/公司调研/") || !file.endsWith(".md") || file.includes("..")) return resp(400, { ok:false, error:"bad file" });
  if (!ALLOWED_STATUS[status]) return resp(400, { ok:false, error:"bad status" });
  const newValue = ALLOWED_STATUS[status];
  const H = { Authorization:"token " + GITHUB_TOKEN, "User-Agent":"scm-site", Accept:"application/vnd.github+json" };
  const enc = encodeURIComponent(file);
  const getRes = await fetch("https://api.github.com/repos/" + REPO + "/contents/" + enc + "?ref=" + BRANCH, { headers: H });
  if (!getRes.ok) return resp(502, { ok:false, error:"read fail " + getRes.status });
  const meta = await getRes.json();
  const content = decodeB64(meta.content);
  const updated = updateFM(content, newValue);
  if (!updated) return resp(422, { ok:false, error:"frontmatter not found" });
  if (updated === content) return resp(200, { ok:true, noChange:true, status:newValue });
  const putRes = await fetch("https://api.github.com/repos/" + REPO + "/contents/" + enc, {
    method: "PUT",
    headers: Object.assign({}, H, { "Content-Type":"application/json" }),
    body: JSON.stringify({ message:"快捷操作：" + file.split("/").slice(-2,-1)[0] + " 状态 → " + newValue, content: encodeB64(updated), sha: meta.sha, branch: BRANCH })
  });
  if (!putRes.ok) return resp(502, { ok:false, error:"write fail " + putRes.status });
  return resp(200, { ok:true, status:newValue });
};