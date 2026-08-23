/* ===== 文雪求职小窝 · 前端逻辑（数据由生成器自动注入） ===== */
var D = window.SITE_DATA || {};
var JOBS = D.jobs || [], COMPS = D.companies || [], TL = D.timeline || [];
var RESUMES = D.resumes || {general:[], custom:[]}, KBS = D.kb || [];
var IMGS = D.images || {bg:{}, av:{}};
/* 快捷操作中转站（Cloudflare Worker），接入后由助手填写 */
var BRIDGE = { url: "", key: "" };
var STATUS_LABEL = {ready:"📮 待投递", sent:"✉️ 已投递", interview:"📞 面试中", dead:"❌ 已挂", backup:"🗂️ 备选", done:"✅ 已背调"};

/* ---------- 工具 ---------- */
function scoreClass(s){ if(s==="—"||s===""||s==null) return "gray"; s=parseFloat(s); if(isNaN(s)) return "gray"; if(s>=80) return "green"; if(s>=70) return "blue"; if(s>=60) return "amber"; return "red"; }
function statusClass(s){ return {done:"done",warn:"warn",backup:"backup",new:"new",interview:"interview",dead:"dead"}[s]||"backup"; }
function esc(s){ return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
function setModal(html){ document.getElementById("modalBody").innerHTML = html; document.getElementById("modal").classList.add("show"); }
function closeModal(){ document.getElementById("modal").classList.remove("show"); }
var toastTimer=null;
function toast(msg){ var t=document.getElementById("toast"); t.textContent=msg; t.classList.add("show"); clearTimeout(toastTimer); toastTimer=setTimeout(function(){t.classList.remove("show");},2200); }

/* ---------- 首页 ---------- */
function renderHome(){
  var st = D.stats||{};
  document.getElementById("statJobs").textContent = st.jobs||0;
  document.getElementById("statRec").textContent = st.rec||0;
  document.getElementById("statInt").textContent = st.interview||0;
  document.getElementById("statOff").textContent = st.offer||0;
  var todo = D.todo||[];
  var todoHtml = todo.length ? todo.map(function(t){ return '<li><input type="checkbox"><span>'+esc(t)+'</span></li>'; }).join("") : '<li style="color:var(--muted)">今天没有待办，轻松一下 🐾</li>';
  document.getElementById("todoList").innerHTML = todoHtml;
  var last = TL.slice(0,2);
  var tlHtml = last.length ? last.map(function(t){
    return '<div class="tl-item"><span class="tl-date">'+esc(t.date.slice(5))+'</span>'+esc((t.items&&t.items[0])||t.title)+'</div>';
  }).join("") : '<div class="tl-item" style="color:var(--muted)">还没有日报记录</div>';
  document.getElementById("homeTl").innerHTML = tlHtml;
}

/* ---------- 岗位看板 ---------- */
var curFilter="all", curQuery="";
function renderJobs(){
  var STATUS_FILTERS = ["done","ready","sent","interview","offer","backup","dead","warn"];
  var list = JOBS.filter(function(j){
    if(curFilter==="rec" && !(parseFloat(j.score)>=70)) return false;
    if(STATUS_FILTERS.indexOf(curFilter)>=0 && j.status!==curFilter) return false;
    if(curQuery){ var q=curQuery.toLowerCase(); if((j.company+j.pos+j.city).toLowerCase().indexOf(q)<0) return false; }
    return true;
  });
  var html = "";
  list.forEach(function(j){
    html += '<div class="job-card" onclick="openJob('+JOBS.indexOf(j)+')">'
      + '<div class="job-top"><div class="job-title"><span class="company">'+esc(j.company)+'</span><span class="pos">'+esc(j.pos)+'</span></div>'
      + '<span class="badge '+scoreClass(j.score)+'">'+esc(j.score)+'</span></div>'
      + '<div class="job-meta">📍 '+esc(j.city)+' &nbsp;·&nbsp; 💰 '+esc(j.salary)+' &nbsp;·&nbsp; 🗓 截止 '+esc(j.deadline)+'</div>'
      + '<div class="job-tags"><span class="status '+statusClass(j.status)+'">'+esc(j.statusTxt)+'</span><span class="level">匹配等级 '+esc(j.level)+'</span>'
      + '<span class="link-btn">🔗 原始链接</span></div></div>';
  });
  document.getElementById("jobList").innerHTML = html || '<div class="card" style="text-align:center;color:var(--muted)">🐾 没有符合条件的岗位哦～</div>';
}
function fileLinks(j, i){
  var out = "";
  if(j.report){
    if(j.report.pdf) out += '<a href="'+j.report.pdf+'" target="_blank">📄 背调报告 PDF</a>';
    else if(j.report.html) out += '<a onclick="openJobNote('+i+',\'report\')">📄 查看背调报告</a>';
  }
  if(j.resume){
    if(j.resume.pdf) out += '<a href="'+j.resume.pdf+'" target="_blank">📄 定制简历 PDF</a>';
    if(j.resume.doc) out += '<a href="'+j.resume.doc+'">📄 定制简历 Word</a>';
  }
  if(j.jd){
    if(j.jd.pdf) out += '<a href="'+j.jd.pdf+'" target="_blank">🗃️ JD 原文 PDF</a>';
    else if(j.jd.pdfs) j.jd.pdfs.forEach(function(u,k){ out += '<a href="'+u+'" target="_blank">🗃️ JD PDF '+(k+1)+'</a>'; });
    else if(j.jd.html) out += '<a onclick="openJobNote('+i+',\'jd\')">🗃️ 查看 JD 原文</a>';
  }
  return out || '<span style="color:var(--muted)">暂无关联文件</span>';
}
function openJob(i){
  var j = JOBS[i];
  var rows = (j.detail||[]).map(function(d){ return "<tr><td>"+esc(d[0])+"</td><td>"+esc(d[2])+" / "+esc(d[1])+"</td></tr>"; }).join("");
  setModal(
    '<h2>'+esc(j.company)+' · '+esc(j.pos)+'</h2>'
    + '<div class="m-sub">📍 '+esc(j.city)+' ｜ 💰 '+esc(j.salary)+' ｜ 🗓 截止 '+esc(j.deadline)+'</div>'
    + '<div class="job-tags"><span class="status '+statusClass(j.status)+'">'+esc(j.statusTxt)+'</span><span class="level">匹配等级 '+esc(j.level)+'</span></div>'
    + '<div class="m-sec">📄 JD 摘要</div><p style="font-size:13.5px;color:var(--muted)">'+esc(j.summary)+'</p>'
    + '<div class="m-sec">📊 匹配度评分明细</div>'
    + '<table class="m-table"><tbody>'+rows+'<tr style="background:var(--pink-soft)"><td><b>总分</b></td><td><b>'+esc(j.score)+' / 100</b></td></tr></tbody></table>'
    + '<div class="m-sec">🧩 关联资料</div><div class="m-links">'+fileLinks(j, i)
    + (j.link?'<a href="'+j.link+'" target="_blank">🔗 投递/原始链接</a>':'')
    + '</div>'
    + '<div class="m-sec">⚡ 快捷操作</div>'
    + '<div class="m-links" style="margin-bottom:4px">'
    + '<a onclick="quickAction('+i+',\'ready\')">📮 待投递</a>'
    + '<a onclick="quickAction('+i+',\'sent\')">✉️ 已投递</a>'
    + '<a onclick="quickAction('+i+',\'interview\')">📞 面试中</a>'
    + '<a onclick="quickAction('+i+',\'dead\')">❌ 已挂</a>'
    + '</div>'
    + '<p style="font-size:11.5px;color:var(--muted)">点一下即可更新知识库状态，自动同步到电脑和网站</p>'
    + (j.note?'<div class="m-sec">📝 备注</div><p style="font-size:13px;color:var(--muted)">'+esc(j.note)+'</p>':''));
}
function quickAction(i, status){
  var j = JOBS[i];
  if(!j.file){ toast("这个岗位暂不支持快捷操作"); return; }
  var label = STATUS_LABEL[status] || "";
  function okUpdate(){
    toast("✅ 已更新为「" + label + "」，自动同步中～");
    j.statusTxt = label;
    j.status = status;
    renderJobs();
  }
  function fallback(){
    var editUrl = "https://github.com/WenXue-10/SCM-Career-Dashboard/edit/main/" + encodeURIComponent(j.file);
    var msg = "更新岗位状态：" + j.company + "-" + j.pos + " → " + label;
    try { if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(msg); } } catch(e){}
    setModal('<h2>⚡ 快捷更新「' + label + '」</h2>'
      + '<p style="font-size:13.5px;color:var(--muted);margin-top:8px">中转站当前不可达（国内网络限制）。给你两个手动办法（都很快）：</p>'
      + '<div class="m-links" style="margin-top:12px"><a href="' + editUrl + '" target="_blank">✏️ 用 GitHub 直接改状态</a></div>'
      + '<p style="font-size:12.5px;color:var(--muted);margin-top:12px">已复制一句话：<b>' + esc(msg) + '</b>。也可以到电脑上的 Codex 里粘贴这句话，我 1 分钟帮你改好。</p>');
  }
  if(!BRIDGE.url || !BRIDGE.key){ fallback(); return; }
  fetch(BRIDGE.url, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ key: BRIDGE.key, file: j.file, status: status })
  }).then(function(r){ return r.json(); }).then(function(res){
    if(res.ok){ okUpdate(); } else { toast("❌ 更新失败：" + (res.error || "未知错误")); }
  }).catch(function(){ fallback(); });
}
function openJobNote(i, which){
  var j = JOBS[i];
  var h = (which==="report") ? (j.report?j.report.html:"") : (j.jd?j.jd.html:"");
  var t = (which==="report") ? "背调报告" : "JD 原文";
  setModal('<h2>'+esc(j.company)+' · '+esc(t)+'</h2><div class="note-body" style="margin-top:12px">'+(h||'<p>暂无内容</p>')+'</div>');
}

/* ---------- 公司池 ---------- */
function renderCompanies(){
  var html = COMPS.map(function(g){
    var cards = g.groups.map(function(c){
      return '<div class="cmp-card" onclick="openCmp('+COMPS.indexOf(g)+','+g.groups.indexOf(c)+')">'
        + '<div class="cn">'+esc(c.cat)+'</div><div class="why">'+esc(c.name)+'</div>'
        + (c.why?'<div class="why" style="margin-top:6px">💡 '+esc(c.why)+'</div>':'')
        + '<div class="more">点开看理由 →</div></div>';
    }).join("");
    return '<div class="cmp-sec"><h3>'+esc(g.title)+'</h3><div class="cmp-grid">'+cards+'</div></div>';
  }).join("");
  document.getElementById("cmpList").innerHTML = html;
}
function openCmp(gi, ci){
  var g = COMPS[gi], c = g.groups[ci];
  var items = [];
  c.name.split(/[、，,]/).forEach(function(n){ n=n.trim(); if(n) items.push(n); });
  var rows = items.map(function(n,i){
    return '<div class="note-item" onclick="openCmpDetail('+gi+','+ci+','+i+')"><span class="ni-ic">🏢</span>'+esc(n)+'<span class="ni-more">详情 →</span></div>';
  }).join("");
  setModal('<h2>'+esc(g.title)+' · '+esc(c.cat)+'</h2>'
    + '<div class="m-sub">'+esc(c.why||"")+'</div>'
    + '<div class="m-sec">🏢 公司清单（点开看详情）</div>'+rows);
}
function openCmpDetail(gi, ci, i){
  var c = COMPS[gi].groups[ci];
  var items = c.name.split(/[、，,]/).map(function(n){ return n.trim(); }).filter(Boolean);
  var nm = items[i] || c.name;
  setModal('<h2>🏢 '+esc(nm)+'</h2>'
    + '<div class="m-sec">📌 所属类别</div><p style="font-size:13.5px">'+esc(COMPS[gi].title)+' · '+esc(c.cat)+'</p>'
    + '<div class="m-sec">💡 入选理由</div><p style="font-size:13.5px;color:var(--muted)">'+esc(c.why||"（暂无详细理由）")+'</p>'
    + '<div class="m-sec">📋 说明</div><p style="font-size:12.5px;color:var(--muted)">该公司的详细背调报告，会在该岗位被收录并执行 Skill 2 后自动生成并出现在这里。</p>');
}

/* ---------- 日报 ---------- */
function renderTimeline(){
  var html = TL.map(function(t){
    var items = (t.items||[]).map(function(x){ return '<li>'+esc(x)+'</li>'; }).join("");
    return '<div class="tl-card"><div class="tl-head"><span class="tl-title">'+esc(t.title)+'</span><span class="tl-badge">'+esc(t.date)+'</span></div><ul class="tl-body">'+items+'</ul></div>';
  }).join("");
  document.getElementById("tlList").innerHTML = html || '<div class="card" style="text-align:center;color:var(--muted)">🐾 还没有日报记录</div>';
}

/* ---------- 简历库 ---------- */
var RESUME_LIST = [];
function resumeCard(r){
  return '<div class="resume-card" onclick="openResume('+r._i+')">'
    + '<div class="resume-top"><div class="resume-ic">📄</div><div><div class="rn">'+esc(r.name)+'</div><div class="rd">'+esc(r.desc)+'</div></div></div>'
    + '<div class="resume-actions">'
    + (r.pdf?'<a class="pill g" href="'+r.pdf+'" download onclick="event.stopPropagation()">⬇ 下载 PDF</a>':'')
    + (r.doc?'<a class="pill o" href="'+r.doc+'" download onclick="event.stopPropagation()">📄 下载 Word</a>':'')
    + '<span class="pill o" onclick="event.stopPropagation();openResume('+r._i+')">👀 预览</span>'
    + '</div></div>';
}
function renderResumes(){
  RESUME_LIST = [];
  var general = [];
  (RESUMES.general||[]).forEach(function(r){ r._i = RESUME_LIST.length; RESUME_LIST.push(r); general.push(resumeCard(r)); });
  var custom = [];
  (RESUMES.custom||[]).forEach(function(cg){
    var cards = cg.items.map(function(r){ r._i = RESUME_LIST.length; RESUME_LIST.push(r); return resumeCard(r); }).join("");
    custom.push('<div class="company-group"><div class="cg-name">💙 '+esc(cg.company)+'</div><div class="resume-list">'+cards+'</div></div>');
  });
  document.getElementById("resumeGeneral").innerHTML = general.join("");
  document.getElementById("resumeCustom").innerHTML = custom.join("");
}
function openResume(i){
  var r = RESUME_LIST[i]; if(!r) return;
  var links = "";
  if(r.pdf) links += '<a href="'+r.pdf+'" target="_blank">⬇️ 下载 PDF</a><a href="'+r.pdf+'" target="_blank">👀 在线预览</a>';
  if(r.doc) links += '<a href="'+r.doc+'" target="_blank">📄 下载 Word 版</a>';
  setModal('<h2>📄 '+esc(r.name)+'</h2><div class="m-sub">手机可直接下载或预览 PDF，投递时发给 HR 即可</div>'
    + (r.pdf?'<div class="pdf-ph">🖨️<br>点击下方「在线预览」查看 PDF 内容</div>':'<div class="pdf-ph">🖨️<br>该简历暂无 PDF 版（生成器会自动补齐）</div>')
    + '<div class="m-links">'+links+'</div>');
}

/* ---------- 知识库 ---------- */
var KB_FLAT = [];
function flattenKb(){
  KB_FLAT = [];
  KBS.forEach(function(k){
    (k.groups||[{title:"", notes:k.notes||[]}]).forEach(function(g){
      (g.notes||[]).forEach(function(n){
        if(n.children){ n.children.forEach(function(c){ KB_FLAT.push(c); }); }
        else KB_FLAT.push(n);
      });
    });
  });
}
function kbNoteItem(n){
  var idx = KB_FLAT.indexOf(n);
  return '<div class="note-item" onclick="openKbNote('+idx+')"><span class="ni-ic">'+esc(n.icon)+'</span>'+esc(n.title)+'<span class="ni-more">打开 →</span></div>';
}
function renderKb(){
  document.getElementById("kbGrid").innerHTML = KBS.map(function(k,i){
    var cnt = 0;
    (k.groups||[{title:"", notes:k.notes||[]}]).forEach(function(g){
      (g.notes||[]).forEach(function(n){ cnt += n.children ? n.children.length : 1; });
    });
    return '<div class="kb-card '+k.cls+'" onclick="openKb('+i+')"><div class="ic">'+k.icon+'</div><div class="kn">'+esc(k.name)+'</div><div class="kd">'+esc(k.desc)+'</div><span class="ncount">'+cnt+' 项</span></div>';
  }).join("");
}
function openKb(i){
  var k = KBS[i];
  var html = "";
  (k.groups||[{title:"", notes:k.notes||[]}]).forEach(function(g){
    if(g.title) html += '<div class="kb-section">'+esc(g.title)+'</div>';
    var items = (g.notes||[]).map(function(n){
      if(n.children){
        return '<div class="kb-folder"><div class="kf-name">'+n.icon+' '+esc(n.title)+'</div>'
          + n.children.map(function(c){ return kbNoteItem(c); }).join("") + '</div>';
      }
      return kbNoteItem(n);
    }).join("");
    html += items || '<div style="color:var(--muted);font-size:13px;margin:4px 0">（空）🐾</div>';
  });
  setModal('<h2>'+k.icon+' '+esc(k.name)+'</h2><div class="m-sub">'+esc(k.desc)+' · 点击查看</div>'+(html||'<div class="m-sub">这个文件夹还没有内容 🐾</div>'));
}
function openKbNote(idx){
  var n = KB_FLAT[idx];
  if(!n) return;
  setModal('<h2>'+n.icon+' '+esc(n.title)+'</h2><div style="margin-top:12px" class="note-body">'+(n.html||'<p>暂无内容</p>')+'</div>');
}

/* ---------- 全局搜索 ---------- */
function plainText(html){
  var d = document.createElement("div"); d.innerHTML = html || ""; return (d.textContent||"").replace(/\s+/g," ").trim();
}
var GSEARCH_IDX = null, gsList = [];
function buildSearchIndex(){
  var idx = [];
  JOBS.forEach(function(j){
    idx.push({type:"岗位", icon:"🐾", title: j.company+" · "+j.pos, sub: (j.city+" ｜ "+j.statusTxt+" ｜ 分"+j.score),
      keys: (j.company+j.pos+j.city).toLowerCase(),
      open: function(){ closeModal(); go("jobs"); openJob(JOBS.indexOf(j)); }});
  });
  var allRes = (RESUMES.general||[]).slice();
  (RESUMES.custom||[]).forEach(function(cg){ allRes = allRes.concat(cg.items); });
  allRes.forEach(function(r){
    idx.push({type:"简历", icon:"📄", title: r.name, sub: r.desc||"", keys: (r.name+(r.desc||"")).toLowerCase(),
      open: function(){ closeModal(); go("resume"); }});
  });
  COMPS.forEach(function(g){ g.groups.forEach(function(c){
    (c.name||"").split(/[、，,]/).forEach(function(nm){ nm=nm.trim(); if(!nm) return;
      idx.push({type:"公司", icon:"🐈", title: nm, sub: g.title+" ｜ "+c.cat, keys: (nm+g.title+c.cat).toLowerCase(),
        open: function(){ closeModal(); go("companies"); }});
    });
  });});
  KBS.forEach(function(k){
    (k.groups||[{title:"", notes:k.notes||[]}]).forEach(function(g){
      (g.notes||[]).forEach(function(n){
        (n.children||[n]).forEach(function(nn){
          var txt = plainText(nn.html);
          idx.push({type:"笔记", icon:nn.icon||"📄", title: nn.title, sub: txt.slice(0,60), keys: (nn.title+" "+txt).toLowerCase(),
            open: function(){ closeModal(); go("knowledge"); }});
        });
      });
    });
  });
  return idx;
}
function openGlobalSearch(){
  if(!GSEARCH_IDX) GSEARCH_IDX = buildSearchIndex();
  setModal('<h2>🔍 全局搜索</h2><div class="m-sub">搜岗位 / 笔记 / 公司 / 简历，全部知识库内容</div>'
    + '<div class="search" style="margin-bottom:12px"><span>🔍</span><input id="gsInput" placeholder="输入关键词，如：供应链 / 济南 / 比亚迪…" autofocus></div>'
    + '<div id="gsResults"></div>');
  var inp = document.getElementById("gsInput");
  function doSearch(){
    var q = (inp.value||"").toLowerCase();
    gsList = q ? GSEARCH_IDX.filter(function(x){ return x.keys.indexOf(q) >= 0; }) : [];
    var html = gsList.slice(0,30).map(function(x,i){
      return '<div class="note-item" onclick="gsOpen('+i+')"><span class="ni-ic">'+x.icon+'</span><div style="flex:1;min-width:0"><div style="font-weight:800;font-size:13.5px">'+esc(x.title)+'</div><div style="font-size:11.5px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(x.sub)+'</div></div><span style="font-size:11px;color:var(--pink-deep);background:var(--pink-soft);padding:2px 8px;border-radius:20px;flex-shrink:0">'+x.type+'</span></div>';
    }).join("");
    document.getElementById("gsResults").innerHTML = q ? (html || '<div style="text-align:center;color:var(--muted);padding:20px">🐾 没有找到相关结果</div>') : '<div style="text-align:center;color:var(--muted);padding:20px">输入关键词开始搜索～</div>';
  }
  inp.addEventListener("input", doSearch);
  inp.addEventListener("keydown", function(e){ if(e.key==="Enter") doSearch(); });
  setTimeout(function(){ inp.focus(); }, 100);
  doSearch();
}
function gsOpen(i){
  var x = gsList[i];
  if(x && x.open) x.open();
}

/* ---------- 头像 & 背景 ---------- */
var BG_IMGS = IMGS.bg||{}, AV_IMGS = IMGS.av||{};
var savedBg = Object.keys(BG_IMGS)[0]||"img4", savedAv = Object.keys(AV_IMGS)[0]||"img1";
try{ savedBg = localStorage.getItem("scm_bg") || Object.keys(BG_IMGS)[0] || "img4"; savedAv = localStorage.getItem("scm_av") || Object.keys(AV_IMGS)[0] || "img1"; }catch(e){}
function applyBg(){ document.documentElement.style.setProperty("--bg-img", "url('"+BG_IMGS[savedBg]+"')"); }
function applyAv(){ var a=document.getElementById("avatarImg"); if(a) a.src = AV_IMGS[savedAv]; }
function pickHtml(type, imgs, cur){
  var h = '<div class="pick-grid">';
  Object.keys(imgs).forEach(function(k){
    h += '<div class="pick-item '+(type==="Av"?"av":"")+(k===cur?" active":"")+'" onclick="set'+type+'(\''+k+'\')">'
       + '<img src="'+imgs[k]+'" alt=""><div class="pn">'+(k==="img1"?"图1":k==="img2"?"图2":k==="img3"?"图3":"图4")+'</div></div>';
  });
  return h + '</div>';
}
function openPersonalize(){
  setModal('<h2>🐱 换个风格</h2><div class="m-sub">点下面的图片，实时换背景和头像，你的选择会被记住</div>'
    + '<div class="pick-sec"><div class="m-sec">🖼️ 背景图</div><div class="pick-hint">选一张做整站背景（会自动加柔光保证文字清晰）</div>'+pickHtml("Bg", BG_IMGS, savedBg)+'</div>'
    + '<div class="pick-sec"><div class="m-sec">😺 小头像</div><div class="pick-hint">右上角头像，点它随时能换</div>'+pickHtml("Av", AV_IMGS, savedAv)+'</div>');
}
function setBg(k){ savedBg=k; try{localStorage.setItem("scm_bg",k);}catch(e){} applyBg(); openPersonalize(); }
function setAv(k){ savedAv=k; try{localStorage.setItem("scm_av",k);}catch(e){} applyAv(); openPersonalize(); }

/* ---------- 页面切换 ---------- */
var TITLES = {home:"🐱 作战看板", jobs:"🐾 岗位看板", companies:"🐈 目标公司池", timeline:"😺 每日日报", resume:"📄 简历库", knowledge:"📚 知识库"};
function go(view){
  document.querySelectorAll(".view").forEach(function(v){ v.classList.remove("active"); });
  document.getElementById("view-"+view).classList.add("active");
  document.querySelectorAll(".nav-item,.bn-item").forEach(function(n){ n.classList.toggle("active", n.getAttribute("data-go")===view); });
  document.getElementById("pageTitle").textContent = TITLES[view];
  window.scrollTo({top:0});
}
document.addEventListener("click", function(e){
  var t = e.target.closest("[data-go]");
  if(t){ go(t.getAttribute("data-go")); }
});
document.querySelectorAll(".chip").forEach(function(c){
  c.addEventListener("click", function(){
    document.querySelectorAll(".chip").forEach(function(x){ x.classList.remove("active"); });
    c.classList.add("active");
    curFilter = c.getAttribute("data-f");
    renderJobs();
  });
});
document.getElementById("search").addEventListener("input", function(e){ curQuery=e.target.value; renderJobs(); });
document.addEventListener("keydown", function(e){ if(e.key==="Escape") closeModal(); });

/* ---------- 漂浮小元素 ---------- */
(function(){
  var emojis=["🐱","🐾","🐈","🧶","🐟","😺","🌸"];
  function spawn(){
    var s=document.createElement("span");
    s.textContent=emojis[Math.floor(Math.random()*emojis.length)];
    s.style.left=(Math.random()*96)+"vw";
    s.style.fontSize=(12+Math.random()*15)+"px";
    s.style.animationDuration=(7+Math.random()*7)+"s";
    document.getElementById("floats").appendChild(s);
    setTimeout(function(){s.remove()},16000);
  }
  spawn();spawn();
  setInterval(spawn,1500);
})();

/* ---------- 初始化 ---------- */
(function(){
  var upd = document.getElementById("syncText");
  if(upd && D.updated) upd.textContent = "自动同步 · " + D.updated;
  flattenKb(); renderHome(); renderJobs(); renderCompanies(); renderTimeline(); renderResumes(); renderKb();
  applyBg(); applyAv();
})();