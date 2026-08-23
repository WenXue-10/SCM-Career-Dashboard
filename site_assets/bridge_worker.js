/* 文雪求职小窝 · 快捷操作中转站（Cloudflare Worker）
 * 部署方法：
 * 1. Cloudflare 控制台 → Workers 与 Pages → 创建 Worker
 * 2. 粘贴本代码 → 部署
 * 3. 设置 → 变量 → 添加两个加密变量(Secret)：
 *    GITHUB_TOKEN = 你的 GitHub 令牌
 *    APP_KEY      = 一个随机字符串（告诉文雪，她会配到网站里）
 * 4. 部署后把 Worker 的访问地址发给文雪
 * 安全说明：令牌只存在 Cloudflare 的秘密存储里，绝不会出现在网站上。
 */
const REPO = "WenXue-10/SCM-Career-Dashboard";
const BRANCH = "main";
const ALLOWED_STATUS = {
  ready: "📮 待投递",
  sent: "✉️ 已投递",
  interview: "📞 面试中",
  dead: "❌ 已挂",
  backup: "🗂️ 备选",
  done: "✅ 已背调"
};
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
};
const JSON_HDR = { ...CORS, "Content-Type": "application/json" };

function decodeB64(str) {
  const bin = atob(str);
  const bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}
function encodeB64(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  bytes.forEach((b) => { bin += String.fromCharCode(b); });
  return btoa(bin);
}
function ok(data) { return new Response(JSON.stringify({ ok: true, ...data }), { status: 200, headers: JSON_HDR }); }
function fail(msg, code) { return new Response(JSON.stringify({ ok: false, error: msg }), { status: code || 400, headers: JSON_HDR }); }

function updateFrontmatter(content, newValue) {
  const m = /^---\s*\n([\s\S]*?)\n---/.exec(content);
  if (!m) return null;
  const fm = m[1];
  const nfm = fm.replace(/^(当前状态\s*:\s*).*$/m, "$1" + newValue);
  if (nfm === fm) return null;
  return content.slice(0, m.index) + "---\n" + nfm + "\n---" + content.slice(m.index + m[0].length);
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response("ok", { headers: CORS });
    if (request.method !== "POST") return fail("method", 405);
    let body;
    try { body = await request.json(); } catch (e) { return fail("bad json"); }
    if (!env.APP_KEY || body.key !== env.APP_KEY) return fail("forbidden", 403);
    const file = String(body.file || "");
    const status = String(body.status || "");
    // 只允许改「公司调研」下的评分笔记
    if (!file.startsWith("01_岗位搜集与背调/公司调研/") || !file.endsWith(".md") || file.includes("..")) return fail("bad file");
    if (!ALLOWED_STATUS[status]) return fail("bad status");
    const newValue = ALLOWED_STATUS[status];
    const apiHeaders = { Authorization: "token " + env.GITHUB_TOKEN, "User-Agent": "scm-site", Accept: "application/vnd.github+json" };
    // 读文件
    const enc = encodeURIComponent(file);
    const getRes = await fetch(`https://api.github.com/repos/${REPO}/contents/${enc}?ref=${BRANCH}`, { headers: apiHeaders });
    if (!getRes.ok) return fail("read fail " + getRes.status, 502);
    const meta = await getRes.json();
    const content = decodeB64(meta.content);
    const updated = updateFrontmatter(content, newValue);
    if (!updated) return fail("frontmatter not found", 422);
    if (updated === content) return ok({ noChange: true, status: newValue });
    // 写文件（GitHub API commit）
    const putRes = await fetch(`https://api.github.com/repos/${REPO}/contents/${enc}`, {
      method: "PUT",
      headers: { ...apiHeaders, "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `快捷操作：${file.split("/").slice(-2, -1)[0]} 状态 → ${newValue}`,
        content: encodeB64(updated),
        sha: meta.sha,
        branch: BRANCH
      })
    });
    if (!putRes.ok) return fail("write fail " + putRes.status, 502);
    return ok({ status: newValue });
  }
};