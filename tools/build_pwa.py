import os, shutil, json, hashlib
from PIL import Image
W='/home/claude/gym/work'; OUT='/home/claude/pwa/chess-gym'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT+'/icons')
s=open(W+'/index.html').read()
first,rest=s.split('\n',1); suf='\n\n</body></html>'
if rest.endswith(suf): rest=rest[:-len(suf)]
head_add='''<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/app-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="Chess Gym">
<meta name="theme-color" content="#0b0f15">
'''
assert rest.count('</head>')==1
rest=rest.replace('</head>', head_add+'</head>')
# viewport-fit for the notch
rest=rest.replace('content="width=device-width, initial-scale=1"','content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover"')
sw_reg='<script>if("serviceWorker" in navigator&&(location.protocol==="https:"||location.hostname==="localhost"))addEventListener("load",()=>navigator.serviceWorker.register("sw.js"));</script>\n'
rest=rest.rstrip('\n'); assert rest.endswith('</html>')
rest=rest[:-len('</body>\n</html>')] + sw_reg + '</body>\n</html>\n' if rest.endswith('</body>\n</html>') else rest
open(OUT+'/index.html','w').write(rest)
files=['chess.js','pieces.css','puzzles.json','themes.json','themes2.json','openings.json','deviations.json','drills.json','study.json','favicon.png']
for f in files: shutil.copy(W+'/'+f, OUT+'/'+f)
# full-bleed square icons (iOS rounds the corners itself; transparent corners show up as a black border)
for n in (180,192,512): shutil.copy(f'/home/claude/pwa/ios-{n}.png', f'{OUT}/icons/app-{n}.png')
json.dump({"name":"Chess Gym","short_name":"Chess Gym","start_url":"./","scope":"./","display":"standalone","background_color":"#0b0f15","theme_color":"#0b0f15","orientation":"portrait",
  "icons":[{"src":"icons/app-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/app-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]}, open(OUT+'/manifest.webmanifest','w'), indent=1)
allf=['./','index.html','manifest.webmanifest']+files+['icons/app-180.png','icons/app-192.png','icons/app-512.png']
h=hashlib.sha1(b''.join(open(OUT+'/'+f,'rb').read() for f in allf if f!='./')).hexdigest()[:10]
open(OUT+'/sw.js','w').write(f'''// Chess Gym offline cache. Version changes whenever any app file changes, so an update is picked up on the next launch.
const V = 'gym-{h}', FILES = {json.dumps(allf)};
self.addEventListener('install', (e) => {{ e.waitUntil(caches.open(V).then((c) => c.addAll(FILES)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', (e) => {{ e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== V).map((k) => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener('fetch', (e) => {{
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return; // GitHub sync and links go straight to the network
  // app files: network first (so updates arrive), cache when offline
  e.respondWith(fetch(e.request).then((r) => {{ if (r.ok) {{ const c = r.clone(); caches.open(V).then((cc) => cc.put(e.request, c)); }} return r; }}).catch(() => caches.match(e.request, {{ ignoreSearch: true }}).then((r) => r || caches.match('index.html'))));
}});
''')
open(OUT+'/.nojekyll','w').write('')
shutil.copy('/home/claude/pwa/SETUP.md', OUT+'/SETUP.md')
print('built', h, sorted(os.listdir(OUT)))
