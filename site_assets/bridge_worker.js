/* 文雪求职小窝 · 快捷操作中转站（Cloudflare Worker 经典格式）
 * 秘密变量：GITHUB_TOKEN（GitHub 令牌）、APP_KEY（站点钥匙） */
const REPO = "WenXue-10/SCM-Career-Dashboard";
const BRANCH = "main";
const ALLOWED_STATUS = { ready:"📮 待投递", sent:"✉️ 已投递", interview:"📞 面试中", dead:"❌ 已挂", backup:"🗂️ 备选", done:"✅ 已背调" };
const CORS = { "Access-Control-Allow-Origin":"*", "Access-Control-Allow-Methods":"POST, OPTIONS", "Access-Control-Allow-Headers":"Content-Type" };
const JSON_HDR = { "Access-Control-Allow-Origin":"*", "Content-Type":"application/json" };
function decodeB64(s){ const b=atob(s); const u=Uint8Array.from(b,c=>c.charCodeAt(0)); return new TextDecoder().decode(u); }
function encodeB64(s){ const u=new TextEncoder().encode(s); let b=""; u.forEach(x=>{b+=String.fromCharCode(x);}); return btoa(b); }
function ok(d){ return new Response(JSON.stringify(Object.assign({ok:true},d)),{status:200,headers:JSON_HDR}); }
function fail(m,c){ return new Response(JSON.stringify({ok:false,error:m}),{status:c||400,headers:JSON_HDR}); }
function updateFM(content,val){ const m=/^---\s*\n([\s\S]*?)\n---/.exec(content); if(!m)return null; const fm=m[1]; const n=fm.replace(/^(当前状态\s*:\s*).*$/m,"$1"+val); if(n===fm)return null; return content.slice(0,m.index)+"---\n"+n+"\n---"+content.slice(m.index+m[0].length); }
async function handle(request){
  if (request.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (request.method !== "POST") return fail("method", 405);
  let body; try { body = await request.json(); } catch(e){ return fail("bad json"); }
  if (typeof APP_KEY === "undefined" || body.key !== APP_KEY) return fail("forbidden", 403);
  const file = String(body.file||""), status = String(body.status||"");
  if (!file.startsWith("01_岗位搜集与背调/公司调研/") || !file.endsWith(".md") || file.includes("..")) return fail("bad file");
  if (!ALLOWED_STATUS[status]) return fail("bad status");
  const newValue = ALLOWED_STATUS[status];
  const H = { Authorization:"token "+GITHUB_TOKEN, "User-Agent":"scm-site", Accept:"application/vnd.github+json" };
  const enc = encodeURIComponent(file);
  const getRes = await fetch("https://api.github.com/repos/"+REPO+"/contents/"+enc+"?ref="+BRANCH, { headers: H });
  if (!getRes.ok) return fail("read fail "+getRes.status, 502);
  const meta = await getRes.json();
  const content = decodeB64(meta.content);
  const updated = updateFM(content, newValue);
  if (!updated) return fail("frontmatter not found", 422);
  if (updated === content) return ok({ noChange: true, status: newValue });
  const putRes = await fetch("https://api.github.com/repos/"+REPO+"/contents/"+enc, {
    method: "PUT", headers: Object.assign({}, H, {"Content-Type":"application/json"}),
    body: JSON.stringify({ message:"快捷操作："+file.split("/").slice(-2,-1)[0]+" 状态 → "+newValue, content: encodeB64(updated), sha: meta.sha, branch: BRANCH })
  });
  if (!putRes.ok) return fail("write fail "+putRes.status, 502);
  return ok({ status: newValue });
}
addEventListener("fetch", function(event){ event.respondWith(handle(event.request)); });