import os
os.makedirs('static', exist_ok=True)

wave_html = """
<style>
.wave-bg-global{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;background:#000000;overflow:hidden}
.wave-bg-global canvas{display:block;width:100%;height:100%}
</style>
<div class="wave-bg-global"><canvas id="waveCanvasGlobal"></canvas></div>
<script>
(function(){
if(document.getElementById('waveCanvasGlobal').dataset.done) return;
const cvs=document.getElementById('waveCanvasGlobal');
cvs.dataset.done=1;
const ctx=cvs.getContext('2d');
let w,h,dpr;
function resize(){
 dpr=window.devicePixelRatio||1;
 w=cvs.clientWidth; h=cvs.clientHeight;
 cvs.width=w*dpr; cvs.height=h*dpr;
 ctx.scale(dpr,dpr);
}
resize();
window.addEventListener('resize',resize);
let t=0;
function draw(){
 t+=0.015;
 ctx.clearRect(0,0,w,h);
 const cols=28, rows=22;
 const gapX=w/cols, gapY=h/rows;
 for(let y=0;y<rows;y++){
  for(let x=0;x<cols;x++){
   const px=x*gapX + gapX/2;
   const py=y*gapY + gapY/2;
   // wave formula like your image
   const waveX = Math.sin(y*0.35 + t*1.2) * 25;
   const waveY = Math.cos(x*0.3 + t*0.8) * 12;
   const dist = Math.sqrt(Math.pow((x-cols/2)/cols,2)+Math.pow((y-rows/2)/rows,2));
   const alpha = 0.95 - dist*0.9;
   if(alpha<=0) continue;
   const size = 1.8 + Math.sin(t + x*0.2)*0.8;
   ctx.fillStyle=`rgba(120,200,255,${alpha})`;
   ctx.shadowBlur=8;
   ctx.shadowColor='#00c6ff';
   ctx.beginPath();
   ctx.arc(px+waveX, py+waveY, size, 0, Math.PI*2);
   ctx.fill();
   ctx.shadowBlur=0;
  }
 }
 requestAnimationFrame(draw);
}
draw();
})();
</script>
"""

# Insert into app.py - inject after <div class="my-page"> etc and also make pages transparent
with open('app.py','r') as f:
    code=f.read()

# backup
with open('app.py.before_waves','w') as f:
    f.write(code)

# Make all main containers have position:relative and z-index:1 and transparent bg
# We inject wave_html into every page that has <div class="my-page"> or similar

# For pages inside app.py - inject right before closing of body-like structures
# Simple: prepend wave to every html string that contains '<style>'

if wave_html.strip() not in code:
    # inject wave after <div class="my-page"> opening for my page
    code = code.replace('<div class="my-page">', wave_html + '<div class="my-page" style="position:relative;z-index:1;background:transparent">')
    # inject for income page - find its start
    code = code.replace('@app.route("/income")', wave_html + '\n@app.route("/income")')
    # also inject into templates folder files
    print("Injected into app.py")

with open('app.py','w') as f:
    f.write(code)

# Inject into all templates html
import glob
for tpl in glob.glob('templates/*.html'):
    with open(tpl,'r') as f:
        c=f.read()
    if 'waveCanvasGlobal' not in c:
        # add at very top of body
        if '<body' in c:
            c=c.replace('<body', wave_html + '<body')
        else:
            c=wave_html + c
        # make body bg transparent
        c=c.replace('background:#000','background:transparent')
        with open(tpl,'w') as f:
            f.write(c)
        print(f"patched {tpl}")

print("WAVES ADDED EVERYWHERE - restart app.py")
