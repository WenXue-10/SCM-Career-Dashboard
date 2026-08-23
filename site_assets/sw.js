/* 文雪求职小窝 · Service Worker */
const CACHE = "scm-site-v1";
self.addEventListener("install", (e) => { self.skipWaiting(); });
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return; // 跨域不缓存
  // 页面(导航)：网络优先，保证实时更新；断网时回退缓存
  if (req.mode === "navigate" || url.pathname.endsWith("index.html")) {
    e.respondWith(
      fetch(req).then((res) => { put(req, res.clone()); return res; })
        .catch(() => caches.match(req))
    );
    return;
  }
  // 静态资源/文件：缓存优先，后台更新
  e.respondWith(
    caches.match(req).then((hit) => {
      const net = fetch(req).then((res) => { put(req, res.clone()); return res; }).catch(() => null);
      return hit || net;
    })
  );
});
function put(req, res) {
  try { caches.open(CACHE).then((c) => c.put(req, res)); } catch (e) {}
}