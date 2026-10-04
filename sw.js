const CACHE='chax-training-v30';
self.addEventListener('install',e=>e.waitUntil((async()=>{
  const c=await caches.open(CACHE);
  const statics=['./','./index.html','./styles.css?v=30','./app.js?v=30','./data.js','./manifest.webmanifest','./images/app-icon.svg','./images/app-icon-192.png','./images/app-icon-512.png'];
  const cacheOne=async path=>{const url=new URL(path,self.registration.scope).href;const response=await fetch(new Request(url,{cache:'reload'}));if(!response.ok)throw new Error(`Precache failed: ${path} (${response.status})`);await c.put(url,response)};
  for(let i=0;i<statics.length;i+=4)await Promise.all(statics.slice(i,i+4).map(cacheOne));
  const d=await fetch(new URL('./data.js',self.registration.scope),{cache:'reload'}).then(r=>{if(!r.ok)throw new Error('Exercise data could not be fetched');return r.text()});
  const paths=[...new Set([...d.matchAll(/"(images\/[^"]+\.jpg)"/g)].map(m=>'./'+m[1]))];
  for(let i=0;i<paths.length;i+=8)await Promise.all(paths.slice(i,i+8).map(cacheOne));
  const imageCount=(await c.keys()).filter(r=>new URL(r.url).pathname.includes('/images/')&&r.url.endsWith('.jpg')).length;
  if(imageCount!==paths.length)throw new Error(`Expected ${paths.length} cached photos, got ${imageCount}`);
  await self.skipWaiting();
})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const k of await caches.keys())if(k!==CACHE)await caches.delete(k);await self.clients.claim()})()));
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const url=new URL(e.request.url),shell=e.request.mode==='navigate'||/\/(?:index\.html|styles\.css|app\.js|data\.js|manifest\.webmanifest)$/.test(url.pathname);
  if(shell){
    e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r}).catch(async()=>await caches.match(e.request)||await caches.match('./index.html')));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy))}return r}).catch(()=>e.request.destination==='image'?new Response('',{status:503}):caches.match('./index.html'))));
});
