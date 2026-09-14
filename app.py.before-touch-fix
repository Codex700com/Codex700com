import sqlite3, pathlib, os, random
from manager_code import setup as setup_manager
from flask import render_template, render_template_string, Flask, request, redirect, session, g

app=Flask(__name__)
app.secret_key="codex700_secret_2024"

DB="codex700.db"

def db():
 conn=sqlite3.connect(DB)
 conn.row_factory=sqlite3.Row
 try:
  cols=[r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
  if "refcode" not in cols:
   conn.execute("ALTER TABLE users ADD COLUMN refcode TEXT")
   conn.commit()
 except Exception:
  pass
 return conn

# Create tables if not exist
def init_db():
 c=db()
 c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, password TEXT, invite_code TEXT, balance REAL DEFAULT 0)")
 c.execute("CREATE TABLE IF NOT EXISTS reset_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, name TEXT, message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
 c.execute("""CREATE TABLE IF NOT EXISTS raffle_tickets(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  tickets INTEGER DEFAULT 0,
  created_at INTEGER
 )""")
 c.execute("""CREATE TABLE IF NOT EXISTS raffle_records(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  reward TEXT NOT NULL,
  reward_value INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
 )""")
 c.execute("""CREATE TABLE IF NOT EXISTS raffle_deposit_awards(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  deposit_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  tickets_awarded INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(deposit_id)
 )""")
 c.commit()
 c.close()
init_db()

S='''
<div class="codex-waves">
<span></span><span></span><span></span>
</div>
<link rel="stylesheet" href="/static/css/codex-waves.css">
<!DOCTYPE html><html><head><style>
html{
  scroll-behavior:auto!important;
  -webkit-overflow-scrolling:touch!important;
  overflow-x:hidden!important;
}
body{
  overflow-x:hidden!important;
  overflow-y:auto!important;
  touch-action:pan-y!important;
  -webkit-overflow-scrolling:touch!important;
}
*{
  -webkit-tap-highlight-color:transparent;
}
button,a,input,select,textarea{
  touch-action:manipulation;
}

.carousel-caption{
 position:absolute;
 left:20px;
 right:20px;
 bottom:22px;
 z-index:5;
 padding:12px 14px;
 border-radius:14px;
 background:rgba(0,0,0,.62);
 border:1px solid rgba(0,174,255,.65);
 box-shadow:0 0 14px rgba(0,174,255,.18);
 pointer-events:none;
}
.carousel-title{
 color:#00b7ff;
 font-size:18px;
 font-weight:800;
 letter-spacing:.4px;
}
.carousel-sub{
 margin-top:5px;
 color:#fff;
 font-size:12px;
 line-height:1.4;
}
.hero-slide{
 position:relative!important;
}
</style><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1, user-scalable=no">
<style>
html,body{
  touch-action:pan-x pan-y;
  -ms-touch-action:pan-x pan-y;
  overscroll-behavior-x:none;
}
input,select,textarea,button{
  touch-action:manipulation;
}
</style>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:system-ui,sans-serif;overflow-x:hidden}
.card{position:relative;z-index:2;min-height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column}
a{color:#0a84ff}
</style>
<style>
button,a{ touch-action: manipulation; -webkit-tap-highlight-color: transparent; }
button:active{ transform: scale(0.97); opacity:0.8; transition: transform 0.05s, opacity 0.05s; }
</style>
<script>
// SUPER FAST BUTTONS
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('button').forEach(function(b){
    b.addEventListener('touchstart', function(){}, {passive:true});
    b.addEventListener('click', function(){
      this.style.transform='scale(0.96)';
      var orig=this.innerHTML;
      // instant feedback
      setTimeout(()=>{ this.style.transform='scale(1)'; },80);
    });
  });
  // Make forms submit instantly, no double delay
  document.querySelectorAll('form').forEach(function(f){
    f.addEventListener('submit', function(){
      var btn=f.querySelector('button');
      if(btn){ btn.disabled=false; btn.innerHTML='Processing...'; btn.style.opacity='0.7'; }
    });
  });
});
</script>

'''

WAVE='<div class="wave-bg" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;background:#000;pointer-events:none"><canvas id="waveCanvas" style="width:100%;height:100%;display:block"></canvas></div><script>var c=document.getElementById("waveCanvas");var x=c.getContext("2d");var W,H,d=window.devicePixelRatio||1;function R(){W=c.width=innerWidth*d;H=c.height=innerHeight*d;c.style.width=innerWidth+"px";c.style.height=innerHeight+"px"}R();addEventListener("resize",R);var t=0;function D(){t+=1.5;x.clearRect(0,0,W,H);var rows=22,cols=60,sx=W/cols,sy=H*0.7/rows,oy=H*0.5;for(var y=0;y<rows;y++){for(var X=0;X<cols;X++){var px=X*sx,py=oy+y*sy+Math.sin(X*0.18+t+y*0.25)*34+Math.cos(y*0.18+t*0.7)*18,dist=Math.abs(px-W/2)/(W/2),a=1-dist*0.6;if(a<0)a=0;var sz=(1.3+Math.sin(t*2+X*0.15)*0.3)*(1.1+a*1.6)*d;x.beginPath();x.arc(px,py,sz,0,6.283);x.fillStyle="rgba("+(90+a*40)+","+(190+a*40)+",255,"+(0.35+a*0.6)+")";x.shadowBlur=sz*2.5;x.shadowColor="#60a5fa";x.fill();x.shadowBlur=0;if(X<cols-1){var nx=(X+1)*sx,ny=oy+y*sy+Math.sin((X+1)*0.18+t+y*0.25)*34+Math.cos(y*0.18+t*0.7)*18;x.beginPath();x.moveTo(px,py);x.lineTo(nx,ny);x.strokeStyle="rgba(96,165,250,"+(a*0.18)+")";x.lineWidth=0.9*d;x.stroke()}}}requestAnimationFrame(D)}D();</script>'

@app.route("/")
def index():
 return redirect("/register") if "uid" not in session else redirect("/home")

@app.route("/register",methods=["GET","POST"])
def register():
 captcha=''.join(random.choices('0123456789',k=4))
 m=""
 if request.method=="POST":
  phone=request.form.get("phone","").strip()
  pw=request.form.get("password","")
  cpw=request.form.get("confirm","")
  code=request.form.get("captcha_input","")
  real=request.form.get("real_captcha","")
  invite=request.form.get("invite","")
  def is_strong(p):
   return len(p)>=8 and any(c.isupper() for c in p) and any(c.islower() for c in p) and any(c.isdigit() for c in p) and any(c in "!@#$%^&*()_+-=" for c in p)
  if real and code!=real:
   m="Invalid verification code"
  elif pw!=cpw:
   m="Passwords do not match"
  elif not is_strong(pw):
   m="Please ur password is too weak"
  else:
   c=db()
   ex=c.execute("SELECT id FROM users WHERE phone=?",(phone,)).fetchone()
   if ex:
    m="Phone already registered"
    c.close()
   else:
    import secrets, string
    chars=string.ascii_uppercase+string.digits
    while True:
     my_refcode="".join(secrets.choice(chars) for _ in range(8))
     if not c.execute("SELECT id FROM users WHERE refcode=?",(my_refcode,)).fetchone():
      break
    c.execute("INSERT INTO users (phone,password,refcode) VALUES (?,?,?)",(phone,pw,my_refcode))
    c.commit()
    c.close()
    return S+'<div style="position:relative;z-index:2;min-height:100vh;display:flex;align-items:center;justify-content:center"><div style="background:rgba(0,0,0,0.7);border:1px solid #0a84ff;border-radius:16px;padding:30px;text-align:center"><p style="color:#4ade80">Registration Successful!</p><script>setTimeout(function(){location.href="/login"},100)</script></div></div>'
 colors=["#3b82f6","#f59e0b","#10b981","#a855f7","#ec4899"]
 col_html="".join(['<span style="color:'+random.choice(colors)+';font-weight:900;margin:1px">'+ch+'</span>' for ch in captcha])
 html='<style>.reg-wrap{position:relative;z-index:2;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding-top:10vh;padding-left:18px;padding-right:18px}.welcome{font-size:34px;font-weight:800;color:#fff;margin-bottom:22px}.pill{width:100%;max-width:360px;height:52px;background:rgba(0,0,0,0.55);border:1px solid #555;border-radius:26px;display:flex;align-items:center;padding:0 16px;margin:9px 0;position:relative}.pill input{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:15px;margin-left:10px}.captcha-box{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:#fff;border-radius:8px;padding:6px 14px;font-size:22px;letter-spacing:3px;font-weight:800}.reg-btn{width:100%;max-width:360px;height:50px;background:transparent;border:1.6px solid #0a84ff;border-radius:26px;color:#0a84ff;font-size:19px;font-weight:600;margin-top:18px;cursor:pointer}.err{color:#ff6b6b;font-size:13px;max-width:360px;text-align:center;margin:6px;background:rgba(255,0,0,0.08);padding:8px;border-radius:8px}html{scroll-behavior:auto!important;}body{overflow-x:hidden;touch-action:pan-y;-webkit-overflow-scrolling:touch;}</style><div class="reg-dots" style="position:fixed;inset:0;z-index:0;pointer-events:none;background-image:radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);background-size:18px 18px;background-position:0 0;"></div><div class="reg-wrap"><div class="welcome">Welcome</div><div class="err">'+m+'</div><form method="POST" style="width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center"><input type="hidden" name="real_captcha" value="'+captcha+'"><div class="pill"><input name="phone" placeholder="Phone Number" required></div><div class="pill"><input name="password" type="password" placeholder="Set Password" required></div><div class="pill"><input name="confirm" type="password" placeholder="Confirm Password" required></div><div class="pill"><input name="captcha_input" placeholder="Verification Code" required><div class="captcha-box">'+col_html+'</div></div><div class="pill"><input name="invite" placeholder="Invitation Code"></div><button class="reg-btn">Register</button><div style="margin-top:14px"><a href="/login" style="color:#aaa;text-decoration:none">‹ Login</a></div></form></div>'
 return S+html

@app.route("/login",methods=["GET","POST"])
def login():
 m=""
 if request.method=="POST":
  ph=request.form.get("phone","").strip()
  pw=request.form.get("password","")
  c=db()
  u=c.execute("SELECT * FROM users WHERE phone=? AND password=?",(ph,pw)).fetchone()
  ex=c.execute("SELECT id FROM users WHERE phone=?",(ph,)).fetchone()
  c.close()
  if u:
   session["uid"]=u["id"]
   return S+'<div class="card"><p style="color:#4ade80">Login successful</p><script>setTimeout(function(){location.href="/home"},100)</script></div>'
  else:
   m="Wrong password. Please try again." if ex else "Phone not registered. Please register first."
 html='<style>.login-wrap{position:relative;z-index:2;min-height:100vh;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;padding:10vh 18px 30px;overflow:hidden;background:#020609}.welcome{font-family:Georgia,serif;font-size:45px;font-weight:500;color:#fff;margin-bottom:30px;}.login-wrap .err{color:#ff6b6b;font-size:13px;width:100%;max-width:370px;min-height:18px;text-align:center;margin:0 0 5px}.login-form{width:100%;max-width:370px;display:flex;flex-direction:column;align-items:center}.login-pill{width:100%;height:58px;box-sizing:border-box;background:rgba(0,0,0,.70);border:1px solid rgba(255,255,255,.28);border-radius:30px;display:flex;align-items:center;padding:0 18px;margin:9px 0;}.login-pill:focus-within{border-color:#00aaff;}.login-pill input{flex:1;width:100%;background:transparent;border:none;outline:none;color:#fff;font-size:15px;margin-left:5px}.login-pill input::placeholder{color:#929292}.eye{color:#999;font-size:17px;cursor:pointer;padding:8px}.lang{width:100%;display:flex;justify-content:flex-end;margin:3px 0 7px}.lang select{background:transparent;border:0;outline:0;color:#999;font-size:13px}.lang option{background:#050b12;color:#fff}.login-btn{width:100%;height:54px;background:transparent;border:1.6px solid #078cff;border-radius:28px;color:#078cff;font-size:18px;font-weight:600;margin-top:19px;cursor:pointer;}.login-btn:active{transform:scale(.98);background:rgba(0,140,255,.08)}.bot{width:100%;display:flex;justify-content:space-between;margin-top:18px;font-size:13px}.bot a{color:#aaa;text-decoration:none}.bot a:first-child{color:#078cff}@media(max-width:430px){.login-wrap{padding-top:9vh}.welcome{font-size:43px}}html{scroll-behavior:auto!important;}body{overflow-x:hidden;touch-action:pan-y;-webkit-overflow-scrolling:touch;}</style><div class="login-dots" style="position:fixed;inset:0;z-index:0;pointer-events:none;background-image:radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);background-size:18px 18px;background-position:0 0;"></div><div class="login-wrap"><div class="welcome">Welcome</div><div class="err">'+m+'</div><form method="POST" class="login-form"><div class="login-pill"><input name="phone" placeholder="Phone Number" required></div><div class="login-pill"><input id="loginPassword" name="password" type="password" placeholder="Login Password" required><span class="eye" onclick="togglePassword()">◉</span></div><div class="lang"><select><option>English</option></select></div><button class="login-btn" type="submit">Login</button><div class="bot"><a href="/register">‹ &nbsp;Register</a><a href="/reset">Forgot your password?</a></div></form></div><script>function togglePassword(){var p=document.getElementById("loginPassword");p.type=p.type==="password"?"text":"password";}</script>'
 return S+html

@app.route("/reset",methods=["GET","POST"])
def reset():
 m=""
 if request.method=="POST":
  phone=request.form.get("phone","")
  name=request.form.get("name","")
  msg=request.form.get("msg","")
  c=db()
  c.execute("INSERT INTO reset_requests (phone,name,message) VALUES (?,?,?)",(phone,name,msg))
  c.commit()
  c.close()
  m="Request sent to your manager. Please wait."
 html='<style>.reset-wrap{position:relative;z-index:2;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:40px 18px 20px}.rtitle{font-size:26px;font-weight:800;color:#fff;margin-bottom:6px}.rsub{font-size:11px;color:#888;text-align:center;max-width:340px;margin-bottom:18px}.info{width:100%;max-width:360px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:12px 14px;display:flex;gap:10px;margin-bottom:16px}.info p{color:#888;font-size:11px}.pill{width:100%;max-width:360px;height:50px;background:rgba(0,0,0,0.5);border:1px solid #444;border-radius:12px;display:flex;align-items:center;padding:0 14px;margin:8px 0}.pill input,.pill textarea{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:14px;margin-left:10px}.pill textarea{height:60px;resize:none;padding-top:10px}.send-btn{width:100%;max-width:360px;height:48px;background:transparent;border:1.5px solid #0a84ff;border-radius:12px;color:#0a84ff;font-size:16px;font-weight:600;margin-top:14px;cursor:pointer}.ok{color:#4ade80;font-size:13px;margin:10px 0;max-width:360px;text-align:center}</style><div class="reset-wrap"><div class="rtitle">Reset Password</div><div class="rsub">Only CODEX700 managers can reset a password, after verifying your identity.</div><div class="info"><p>For your safety nobody can reset your password from this page. Send your details below and your manager receives them instantly.</p></div><div class="ok">'+m+'</div><form method="POST" style="width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center"><div class="pill"><input name="phone" placeholder="Registered Phone Number" required></div><div class="pill"><input name="name" placeholder="Your Name (optional)"></div><div class="pill" style="height:80px;align-items:flex-start"><textarea name="msg" required>I forgot my login password. Please help me reset it.</textarea></div><button class="send-btn">Send to my manager</button><div style="width:100%;max-width:360px;margin-top:14px;font-size:13px;color:#aaa"><a href="/login" style="color:#aaa;text-decoration:none">‹ Back to Login</a></div></form></div>'
 return S+WAVE+html

@app.route("/home")
def home():
 if "uid" not in session:
  return redirect("/login")

 return S+"""<style>
.home-page{
 min-height:100vh;
 background:#000;
 color:#fff;
 padding:18px 14px 100px;
 box-sizing:border-box;
 font-family:Georgia,serif;
 position:relative;
 overflow:hidden;
}
.home-page:before{
 content:"";
 position:fixed;
 inset:0;
 pointer-events:none;
 opacity:.28;
 background-image:
  radial-gradient(circle,rgba(0,174,255,.25) 1px,transparent 1.5px);
 background-size:26px 26px;
}
.home-top{
 display:flex;
 justify-content:space-between;
 align-items:center;
 margin:4px 0 28px;
}
.home-logo{
 font-size:30px;
 font-weight:800;
 letter-spacing:1px;
}
.msg-link{
 color:#fff;
 text-decoration:none;
 text-align:center;
 font-size:12px;
}
.msg-icon{
 display:block;
 font-size:34px;
 line-height:30px;
}

 .hero{
 height:210px;
 border:1px solid #008fd4;
 border-radius:28px;
 overflow:hidden;
 position:relative;
 background:#02070b;
 margin-bottom:18px;
 box-shadow:0 0 8px rgba(0,174,255,.18);
 touch-action:pan-y;
}
.hero-track{
 display:flex;
 width:100%;
 height:100%;
 transform:translate3d(0,0,0);
 transition:transform .42s ease;
 will-change:transform;
}
.hero-slide{
 min-width:100%;
 height:100%;
 position:relative;
}
.hero-slide img{
 width:100%;
 height:100%;
 display:block;
 object-fit:cover;
}
.hero-slide:after{
 content:"";
 position:absolute;
 inset:0;
 background:linear-gradient(180deg,transparent 35%,rgba(0,0,0,.55));
 pointer-events:none;
}
.hero-arrow{
 position:absolute;
 top:50%;
 transform:translateY(-50%);
 width:43px;
 height:43px;
 border:1px solid #00aaff;
 border-radius:50%;
 background:rgba(0,0,0,.48);
 color:#fff;
 font-size:27px;
 display:flex;
 align-items:center;
 justify-content:center;
 z-index:4;
 padding:0;
}
.hero-left{left:10px}
.hero-right{right:10px}
.dots{
 position:absolute;
 bottom:9px;
 left:50%;
 transform:translateX(-50%);
 display:flex;
 gap:8px;
 z-index:5;
}
.dot{
 width:9px;
 height:9px;
 background:#aaa;
 border-radius:50%;
}
.dot.active{
 width:32px;
 border-radius:10px;
 background:#00b7ff;
}
.stats{
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:14px;
}
.stat{
 background:#fff;
 color:#111;
 border-radius:24px;
 overflow:hidden;
 text-align:center;
 box-shadow:0 0 15px rgba(0,174,255,.25);
}
.stat-value{
 height:72px;
 display:flex;
 align-items:center;
 justify-content:center;
 font-size:25px;
 font-weight:800;
}
.stat-label{
 min-height:52px;
 display:flex;
 align-items:center;
 justify-content:center;
 background:#08b3ed;
 color:#fff;
 font-size:17px;
}
.team-stats{
 display:grid;
 grid-template-columns:repeat(3,1fr);
 gap:12px;
 margin-top:14px;
}
.team-card{
 background:#fff;
 color:#111;
 border-radius:22px;
 overflow:hidden;
 text-align:center;
 box-shadow:0 0 14px rgba(0,174,255,.22);
}
.team-value{
 height:70px;
 display:flex;
 align-items:center;
 justify-content:center;
 font-size:22px;
 font-weight:800;
}
.team-label{
 min-height:48px;
 display:flex;
 align-items:center;
 justify-content:center;
 background:#08b3ed;
 color:#fff;
 font-size:14px;
 padding:0 4px;
}
.news{
 margin-top:28px;
 border:1px solid rgba(0,174,255,.55);
 border-radius:22px;
 background:rgba(0,8,14,.82);
 padding:18px 16px;
 box-shadow:0 0 20px rgba(0,174,255,.12);
}
.news-title{
 font-size:24px;
 font-weight:800;
 margin-bottom:16px;
}
.news-title span{
 color:#00aaff;
}
.news-item{
 padding:14px 0;
 border-top:1px solid rgba(255,255,255,.08);
 color:#ddd;
 font-size:14px;
 line-height:1.5;
}
.bottom-nav{
 position:fixed;
 z-index:20;
 left:0;
 right:0;
 bottom:0;
 height:76px;
 background:#000;
 border-top:1px solid rgba(0,174,255,.22);
 display:grid;
 grid-template-columns:repeat(6,1fr);
 padding-bottom:env(safe-area-inset-bottom);
}
.nav-item{
 color:#fff;
 text-decoration:none;
 text-align:center;
 font-size:12px;
 display:flex;
 flex-direction:column;
 justify-content:center;
 gap:3px;
}
.nav-icon{
 font-size:27px;
 line-height:28px;
}
.nav-item.active{
 color:#00b7ff;
}
@media(max-width:380px){
 .home-page{padding-left:10px;padding-right:10px}
 .stat-label{font-size:14px}
 .team-label{font-size:12px}
 .home-logo{font-size:26px}
}
</style>

<div class="home-page">
 <div class="home-top">
  <div class="home-logo">CODEX700</div>
  <a class="msg-link" href="/support">
   <span class="msg-icon">♧</span>
   Message
  </a>
 </div>

 <div class="hero">
  <div class="hero-track" id="heroTrack">

   <div class="hero-slide">
    <img src="/static/home_banners/banner1.jpg">
<div class="carousel-caption">
  <div class="carousel-title">CODEX700 TECHNOLOGY</div>
  <div class="carousel-sub">Advanced Computing Infrastructure</div>
</div>
   </div>

   <div class="hero-slide">
    <img src="/static/home_banners/banner2.jpg">
<div class="carousel-caption">
  <div class="carousel-title">DIGITAL INFRASTRUCTURE</div>
  <div class="carousel-sub">Built for the future of computing</div>
</div>
   </div>

   <div class="hero-slide">
    <img src="/static/home_banners/banner3.jpg">
<div class="carousel-caption">
  <div class="carousel-title">HIGH-PERFORMANCE SYSTEMS</div>
  <div class="carousel-sub">Powerful machines. Reliable infrastructure.</div>
</div>
   </div>

   <div class="hero-slide">
    <img src="/static/home_banners/banner4.jpg">
<div class="carousel-caption">
  <div class="carousel-title">DATA CENTER TECHNOLOGY</div>
  <div class="carousel-sub">Modern infrastructure powering digital services</div>
</div>
   </div>

   <div class="hero-slide">
    <img src="/static/home_banners/banner5.jpg">
<div class="carousel-caption">
  <div class="carousel-title">THE CODEX700 VISION</div>
  <div class="carousel-sub">Technology • Innovation • Infrastructure</div>
</div>
   </div>

  </div>

  <button class="hero-arrow hero-left" id="heroPrev" type="button">‹</button>
  <button class="hero-arrow hero-right" id="heroNext" type="button">›</button>

  <div class="dots" id="heroDots">
   <span class="dot active"></span>
   <span class="dot"></span>
   <span class="dot"></span>
   <span class="dot"></span>
   <span class="dot"></span>
  </div>
 </div>
 <div class="stats">
  <div class="stat">
   <div class="stat-value">0.00</div>
   <div class="stat-label">Deposit details</div>
  </div>
  <div class="stat">
   <div class="stat-value">0.00</div>
   <div class="stat-label">Withdraw details</div>
  </div>
  <div class="stat">
   <div class="stat-value">0.00</div>
   <div class="stat-label">AI Income</div>
  </div>
  <div class="stat">
   <div class="stat-value">0.00</div>
   <div class="stat-label">Today's earnings</div>
  </div>
 </div>

 <div class="team-stats">
  <div class="team-card">
   <div class="team-value">0</div>
   <div class="team-label">Invite Count</div>
  </div>
  <div class="team-card">
   <div class="team-value">0</div>
   <div class="team-label">Team Count</div>
  </div>
  <div class="team-card">
   <div class="team-value">0.00</div>
   <div class="team-label">Team income</div>
  </div>
 </div>

 <div class="news">
  <div class="news-title"><span>♧</span> News &amp; Announcements</div>
  <div class="news-item">Welcome to CODEX700.</div>
  <div class="news-item">Check your notifications for the latest platform updates.</div>
 </div>
</div>

<div class="bottom-nav">
 <a class="nav-item" href="/home">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><ellipse cx="20" cy="8" rx="12" ry="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 8v21c0 3 5 6 12 6s12-3 12-6V8M8 18c0 3 5 6 12 6s12-3 12-6M8 28c0 3 5 6 12 6s12-3 12-6" fill="none" stroke="currentColor" stroke-width="3"/></svg></span>
  <span>Home</span>
 </a>
 <a class="nav-item" href="/raffle">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="6" y="7" width="16" height="16" rx="2" fill="currentColor"/><rect x="18" y="17" width="16" height="16" rx="2" fill="currentColor"/><rect x="10" y="11" width="8" height="8" fill="#000"/></svg></span>
  <span>Raffle</span>
 </a>
 <a class="nav-item" href="/support">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="5" y="7" width="27" height="20" rx="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M12 27l-2 7 8-7M12 14h13M12 20h9" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="31" cy="29" r="4" fill="currentColor"/></svg></span>
  <span>chats</span>
 </a>
 <a class="nav-item" href="/invest">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="9" y="8" width="22" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="3"/><path d="M5 14h4M5 20h4M5 26h4M31 14h4M31 20h4M31 26h4M15 4v4M21 4v4M27 4v4M15 32v4M21 32v4M27 32v4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><rect x="14" y="14" width="12" height="12" rx="2" fill="currentColor"/></svg></span>
  <span>AI</span>
 </a>
 <a class="nav-item" href="/income">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><path d="M24 5l-3 30M29 10c-3-3-12-3-15 2-4 7 12 5 11 12-1 7-12 8-16 3M12 14h18M9 28h18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
  <span>Income</span>
 </a>
 <a class="nav-item" href="/my">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><circle cx="20" cy="11" r="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 35c0-8 5-12 12-12s12 4 12 12" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></span>
  <span>My</span>
 </a>
</div>

<script>
(function(){
 var track=document.getElementById("heroTrack");
 var dots=document.querySelectorAll("#heroDots .dot");
 var total=4;
 var index=0;
 var timer=null;
 var startX=0;
 var moving=false;

 function show(n){
  index=(n+total)%total;
  track.style.transform="translate3d(-"+(index*100)+"%,0,0)";
  dots.forEach(function(d,i){
   d.className=i===index?"dot active":"dot";
  });
 }

 function next(){show(index+1)}
 function prev(){show(index-1)}

 document.getElementById("heroNext").onclick=function(){
  next();
  restart();
 };

 document.getElementById("heroPrev").onclick=function(){
  prev();
  restart();
 };

 dots.forEach(function(d,i){
  d.onclick=function(){
   show(i);
   restart();
  };
 });

 track.addEventListener("touchstart",function(e){
  startX=e.touches[0].clientX;
  moving=true;
 },{passive:true});

 track.addEventListener("touchend",function(e){
  if(!moving)return;
  var diff=e.changedTouches[0].clientX-startX;
  moving=false;
  if(Math.abs(diff)>45){
   if(diff<0)next();
   else prev();
   restart();
  }
 },{passive:true});

 function restart(){
  clearInterval(timer);
  timer=setInterval(next,4000);
 }

 show(0);
 restart();
})();
</script>
<script>
(function(){
 var track=document.getElementById("heroTrack");
 var dots=document.querySelectorAll("#heroDots .dot");
 var total=5,index=0,timer;

 function show(n){
  index=(n+total)%total;
  track.style.transform="translate3d(-"+(index*100)+"%,0,0)";
  dots.forEach(function(d,i){
   d.className=i===index?"dot active":"dot";
  });
 }

 function restart(){
  clearInterval(timer);
  timer=setInterval(function(){show(index+1)},4000);
 }

 document.getElementById("heroNext").onclick=function(){
  show(index+1); restart();
 };

 document.getElementById("heroPrev").onclick=function(){
  show(index-1); restart();
 };

 dots.forEach(function(d,i){
  d.onclick=function(){show(i); restart()};
 });

 var x=0;
 track.addEventListener("touchstart",function(e){
  x=e.touches[0].clientX;
 },{passive:true});

 track.addEventListener("touchend",function(e){
  var diff=e.changedTouches[0].clientX-x;
  if(Math.abs(diff)>45){
   show(diff<0?index+1:index-1);
   restart();
  }
 },{passive:true});

 show(0);
 restart();
})();
</script></div>"""

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/my")
def my_page():
    if "uid" not in session:
        return redirect("/login")

    c = db()
    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (session["uid"],)
    ).fetchone()
    c.close()

    phone = u["phone"] if u else ""
    balance = float(u["balance"] or 0) if u and "balance" in u.keys() else 0

    return S + """
<style>
.my-page{
 min-height:100vh;
 box-sizing:border-box;
 padding:18px 12px 110px;
 background:#000;
 color:#fff;
 font-family:Georgia,serif;
 background-image:
 radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);
 background-size:18px 18px;
 background-position:0 0;
}

.my-top{
 display:flex;
 justify-content:space-between;
 align-items:center;
 margin-bottom:14px;
}

.my-welcome{
 font-size:24px;
 font-weight:bold;
 color:#00b9f3;
}

.my-phone{
 margin-top:4px;
 color:#aaa;
 font-size:14px;
}

.vip{
 text-align:center;
}

.vip-circle{
 width:58px;
 height:58px;
 border-radius:50%;
 border:2px solid #00b9f3;
 display:flex;
 align-items:center;
 justify-content:center;
 color:#00b9f3;
 font-size:28px;
 box-shadow:0 0 14px rgba(0,190,255,.35);
}

.vip-label{
 margin-top:5px;
 color:#00b9f3;
 font-weight:bold;
 font-size:13px;
}

.wallet{
 position:relative;
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:10px;
 background:#071018;
 border:1px solid #075a78;
 border-radius:18px;
 padding:18px;
 margin-bottom:14px;
 box-shadow:0 0 12px rgba(0,180,255,.14);
}

.wallet-title{
 color:#aaa;
 font-size:13px;
}

.wallet-value{
 margin-top:5px;
 color:#00b9f3;
 font-size:22px;
 font-weight:bold;
}

.wallet-details{
 display:none;
 grid-column:1/-1;
 grid-template-columns:repeat(2,1fr);
 gap:10px;
 padding-top:12px;
 border-top:1px solid #123;
}

.wallet.open .wallet-details{
 display:grid;
}

.wallet-detail{
 background:#05090c;
 border:1px solid #123;
 border-radius:12px;
 padding:10px;
}

.wallet-detail-title{
 color:#999;
 font-size:11px;
}

.wallet-detail-value{
 color:#fff;
 margin-top:4px;
 font-size:14px;
}

.wallet-arrow{
 position:absolute;
 right:12px;
 bottom:5px;
 color:#00b9f3;
 cursor:pointer;
 font-size:20px;
}

.services{
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:9px;
 margin-bottom:14px;
}

.service{
 text-decoration:none;
 color:#fff;
 text-align:center;
 background:#071018;
 border:1px solid #123;
 border-radius:14px;
 padding:12px 4px;
 font-size:11px;
}

.service .icon{
 color:#00b9f3;
 font-size:23px;
 margin-bottom:5px;
}

.section{
 background:#071018;
 border:1px solid #123;
 border-radius:16px;
 padding:16px;
 margin-bottom:14px;
}

.section-title{
 color:#00b9f3;
 font-size:17px;
 font-weight:bold;
}

.share-value,.salary-value{
 margin-top:8px;
 color:#fff;
 font-size:20px;
 font-weight:bold;
}

.salary{
 display:grid;
 grid-template-columns:1fr 1fr;
 gap:12px;
}

.salary-title{
 color:#aaa;
 font-size:12px;
}

.action{
 width:100%;
 margin-top:14px;
 padding:12px;
 border:1px solid #00b9f3;
 border-radius:12px;
 background:#001923;
 color:#00b9f3;
 font-weight:bold;
}

.reward-table{
 width:100%;
 margin-top:14px;
 border-collapse:collapse;
}

.reward-table th,
.reward-table td{
 border:1px solid #123;
 padding:9px;
 text-align:center;
}

.reward-table th{
 color:#00b9f3;
}

.signout{
 text-align:center;
 margin-top:20px;
}

.signout a{
 color:#ff5b5b;
 text-decoration:none;
}

.bottom{
 position:fixed;
 left:0;
 right:0;
 bottom:0;
 z-index:100;
 height:68px;
 display:grid;
 grid-template-columns:repeat(6,1fr);
 background:#02070a;
 border-top:1px solid #123;
}

.bottom a{
 color:#aaa;
 text-decoration:none;
 text-align:center;
 font-size:10px;
 padding-top:7px;
}

.bottom i{
 display:block;
 font-style:normal;
 font-size:24px;
 line-height:30px;
}

.bottom .active{
 color:#00baff;
}

@media(max-width:380px){
 .services{gap:6px}
 .service{font-size:10px}
 .wallet{padding:15px}
}
</style>

<div class="my-page">

<div class="my-top">
 <div>
  <div class="my-welcome">Welcome to Codex</div>
  <div class="my-phone">"""+str(phone)+"""</div>
 </div>
 <div class="vip">
  <div class="vip-circle">✦</div>
  <div class="vip-label">★ VIP 0</div>
 </div>
</div>

<div class="wallet" id="walletBox">
 <div>
  <div class="wallet-title">Wallet</div>
  <div class="wallet-value">0.00</div>
 </div>
 <div>
  <div class="wallet-title">Balance</div>
  <div class="wallet-value">"""+str(balance)+"""</div>
 </div>

 <div class="wallet-details">
  <div class="wallet-detail"><div class="wallet-detail-title">Deposit</div><div class="wallet-detail-value">0.00</div></div>
  <div class="wallet-detail"><div class="wallet-detail-title">Withdraw</div><div class="wallet-detail-value">0.00</div></div>
  <div class="wallet-detail"><div class="wallet-detail-title">AI Income</div><div class="wallet-detail-value">0.00</div></div>
  <div class="wallet-detail"><div class="wallet-detail-title">Today's earnings</div><div class="wallet-detail-value">0.00</div></div>
  <div class="wallet-detail"><div class="wallet-detail-title">Invite Count</div><div class="wallet-detail-value">0</div></div>
  <div class="wallet-detail"><div class="wallet-detail-title">Team Count</div><div class="wallet-detail-value">0</div></div>
  <div class="wallet-detail"><div class="wallet-detail-title">Team income</div><div class="wallet-detail-value">0.00</div></div>
 </div>

 <div class="wallet-arrow" id="walletArrow">⌄</div>
</div>

<div class="services">
<a class="service" href="/deposit"><div class="icon">▣</div>Deposit</a>
<a class="service" href="/withdraw"><div class="icon">♢</div>Withdraw</a>
<a class="service" href="/card"><div class="icon">▤</div>Card</a>
<a class="service" href="/home"><div class="icon">$</div>Bill</a>
<a class="service" href="/invite"><div class="icon">♙</div>Invite</a>
<a class="service" href="/my-team"><div class="icon">♧</div>My team</a>
<a class="service" href="/home"><div class="icon">☆</div>VIP Task</a>
<a class="service" href="/reward"><div class="icon">🎁</div>Reward</a>
<a class="service" href="/reward"><div class="icon">▱</div>Gift code</a>
<a class="service" href="/raffle"><div class="icon">◇</div>Raffle</a>
<a class="service" href="/home"><div class="icon">↓</div>Download App</a>
<a class="service" href="/manager"><div class="icon">♧</div>Manager</a>
<a class="service" href="/my"><div class="icon">⚙</div>Settings</a>
</div>

<div class="section">
 <div class="section-title">Codex Cryptocurrency Purchase Share</div>
 <div class="share-value">0.00</div>
</div>

<div class="section">
 <div class="salary">
  <div>
   <div class="salary-title">Last month's salary</div>
   <div class="salary-value">0.00</div>
  </div>
  <div>
   <div class="salary-title">This month's salary</div>
   <div class="salary-value">0.00</div>
  </div>
 </div>
 <button class="action" type="button">Get last month's salary</button>
</div>

<div class="section">
 <div class="salary">
  <div>
   <div class="salary-title">Invited last month</div>
   <div class="salary-value">0</div>
  </div>
  <div>
   <div class="salary-title">Invited this month</div>
   <div class="salary-value">0</div>
  </div>
 </div>

 <button class="action" type="button">Get last month's reward</button>

 <table class="reward-table">
  <tr><th>Invite</th><th>Reward</th></tr>
  <tr><td>6</td><td>Z-1</td></tr>
  <tr><td>15</td><td>Z-2</td></tr>
  <tr><td>30</td><td>Z-3</td></tr>
  <tr><td>60</td><td>Z-4</td></tr>
 </table>
</div>

<div class="signout">
 <a href="/logout">➜ &nbsp; Sign out</a>
</div>

</div>

<div class="bottom">
 <a href="/home"><i>⌂</i>Home</a>
 <a href="/raffle"><i>▣</i>Raffle</a>
 <a href="/support"><i>▤</i>chats</a>
 <a href="/invest"><i>▦</i>AI</a>
 <a href="/income"><i>₿</i>Income</a>
 <a class="active" href="/my"><i>♙</i>My</a>
</div>

<script>
(function(){
 const box=document.getElementById("walletBox");
 const arrow=document.getElementById("walletArrow");
 if(!box || !arrow) return;
 arrow.addEventListener("click",function(){
  box.classList.toggle("open");
  arrow.textContent=box.classList.contains("open") ? "⌃" : "⌄";
 });
})();
</script>
"""


@app.route("/my-team")
def my_team_page():
    if "uid" not in session:
        return redirect("/login")

    return S + """
<style>
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#000;color:#fff}
body{font-family:Georgia,"Times New Roman",serif}

.team-page{
 min-height:100vh;
 padding:0 18px 105px;
 background:#000;
 background-image:radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);
 background-size:18px 18px;
}

.team-head{
 height:92px;
 margin:0 -18px 24px;
 position:relative;
 display:flex;
 align-items:center;
 justify-content:center;
 border-bottom:1px solid rgba(0,185,245,.5);
}

.team-title{
 color:#00b9f3;
 font-size:29px;
 font-weight:bold;
 text-shadow:0 0 12px rgba(0,190,255,.45);
}

.team-back{
 position:absolute;
 left:22px;
 top:22px;
 color:#00b9f3;
 text-decoration:none;
 font-size:40px;
 line-height:40px;
}

.team-stats{
 display:grid;
 grid-template-columns:repeat(3,1fr);
 gap:10px;
 margin-bottom:25px;
}

.team-stat{
 min-width:0;
 padding:20px 7px 18px;
 text-align:center;
 background:#071018;
 border:1px solid #075a78;
 border-radius:16px;
 box-shadow:0 0 10px rgba(0,150,210,.15);
}

.team-stat-label{
 color:#9da3aa;
 font-size:14px;
 line-height:1.25;
 min-height:36px;
 display:flex;
 align-items:center;
 justify-content:center;
}

.team-stat-value{
 margin-top:9px;
 color:#00b9f3;
 font-size:24px;
 font-weight:800;
 white-space:nowrap;
}

.team-card{
 position:relative;
 padding:23px 20px;
 margin-bottom:24px;
 background:#071018;
 border:1px solid #075a78;
 border-radius:18px;
 box-shadow:0 0 11px rgba(0,150,210,.15);
}

.team-section-title{
 margin:0 0 20px;
 color:#fff;
 font-size:23px;
 font-weight:bold;
}

.benefit{
 display:flex;
 align-items:center;
 gap:13px;
 padding:14px 0;
 border-top:1px solid #123;
}

.benefit:first-of-type{border-top:0}

.benefit-icon{
 width:38px;
 height:38px;
 flex:none;
 border-radius:50%;
 display:flex;
 align-items:center;
 justify-content:center;
 color:#00b9f3;
 border:1px solid #08769b;
 font-size:20px;
}

.benefit-title{
 color:#fff;
 font-size:16px;
 font-weight:bold;
}

.benefit-desc{
 margin-top:4px;
 color:#8e989f;
 font-size:12px;
 line-height:1.4;
}

.invite-team{
 display:block;
 width:100%;
 height:62px;
 line-height:62px;
 margin:0 0 26px;
 text-align:center;
 text-decoration:none;
 color:#000;
 background:#00b9f3;
 border-radius:15px;
 font-size:18px;
 font-weight:bold;
 box-shadow:0 0 18px rgba(0,185,243,.35);
}

.level-card{
 padding:20px;
 margin-bottom:14px;
 background:#071018;
 border:1px solid #075a78;
 border-radius:17px;
 box-shadow:0 0 10px rgba(0,150,210,.12);
}

.level-top,.level-bottom{
 display:flex;
 align-items:center;
 justify-content:space-between;
 gap:10px;
}

.level-name{
 color:#00b9f3;
 font-size:19px;
 font-weight:bold;
}

.level-count{
 color:#aaa;
 font-size:13px;
}

.level-bottom{
 margin-top:17px;
}

.level-info{
 color:#8e989f;
 font-size:12px;
 line-height:1.6;
}

.commission{
 min-width:65px;
 padding:10px 8px;
 text-align:center;
 border-radius:12px;
 background:#001923;
 border:1px solid #00b9f3;
 color:#00b9f3;
 font-size:20px;
 font-weight:bold;
}

.invite-info{
 margin-top:24px;
}

.invite-code{
 display:flex;
 align-items:center;
 justify-content:space-between;
 gap:10px;
}

.invite-code-label{
 color:#999;
 font-size:12px;
}

.invite-code-value{
 margin-top:5px;
 color:#00b9f3;
 font-weight:bold;
}

.invite-code-button{
 padding:10px 13px;
 border:1px solid #00b9f3;
 border-radius:10px;
 color:#00b9f3;
 text-decoration:none;
 font-size:12px;
}

.team-bottom{
 position:fixed;
 z-index:100;
 left:0;
 right:0;
 bottom:0;
 height:68px;
 display:grid;
 grid-template-columns:repeat(6,1fr);
 background:#02070a;
 border-top:1px solid #123;
}

.team-bottom a{
 color:#fff;
 text-decoration:none;
 text-align:center;
 font-size:10px;
 padding-top:8px;
}

.team-bottom i{
 display:block;
 font-style:normal;
 font-size:27px;
 line-height:30px;
}

.team-bottom .active{color:#00baff}

@media(max-width:380px){
 .team-page{padding-left:13px;padding-right:13px}
 .team-head{margin-left:-13px;margin-right:-13px}
 .team-back{left:17px}
 .team-stat{padding-left:3px;padding-right:3px}
 .team-stat-label{font-size:12px}
 .team-stat-value{font-size:20px}
 .team-card,.level-card{padding-left:17px;padding-right:17px}
}
</style>

<div class="team-page">

 <div class="team-head">
  <a class="team-back" href="/my">‹</a>
  <div class="team-title">My Team</div>
 </div>

 <div class="team-stats">
  <div class="team-stat">
   <div class="team-stat-label">Members</div>
   <div class="team-stat-value">0</div>
  </div>
  <div class="team-stat">
   <div class="team-stat-label">Team deposits</div>
   <div class="team-stat-value">UGX 0</div>
  </div>
  <div class="team-stat">
   <div class="team-stat-label">Earnings</div>
   <div class="team-stat-value">UGX 0</div>
  </div>
 </div>

 <div class="team-card">
  <div class="team-section-title">Why build your team?</div>

  <div class="benefit">
   <div class="benefit-icon">♧</div>
   <div class="benefit-text">
    <div class="benefit-title">Lifetime commission</div>
    <div class="benefit-desc">Earn from eligible deposits made by your team.</div>
   </div>
  </div>

  <div class="benefit">
   <div class="benefit-icon">◆</div>
   <div class="benefit-text">
    <div class="benefit-title">Team development fund</div>
    <div class="benefit-desc">Build a stronger team and increase your rewards.</div>
   </div>
  </div>

  <div class="benefit">
   <div class="benefit-icon">↗</div>
   <div class="benefit-text">
    <div class="benefit-title">Passive growth</div>
    <div class="benefit-desc">Your team can continue growing while you focus on your goals.</div>
   </div>
  </div>

  <div class="benefit">
   <div class="benefit-icon">★</div>
   <div class="benefit-text">
    <div class="benefit-title">Higher VIP rank</div>
    <div class="benefit-desc">Grow your network to unlock higher team levels.</div>
   </div>
  </div>
 </div>

 <a class="invite-team" href="/invite">Invite friends</a>

 <div class="team-section-title" style="margin:0 3px 15px;">
  Team commission levels
 </div>

 <div class="level-card">
  <div class="level-top">
   <div class="level-name">Level 1</div>
   <div class="level-count">0 members</div>
  </div>
  <div class="level-bottom">
   <div class="level-info">Direct members<br>Earn from eligible team activity</div>
   <div class="commission">32%</div>
  </div>
 </div>

 <div class="level-card">
  <div class="level-top">
   <div class="level-name">Level 2</div>
   <div class="level-count">0 members</div>
  </div>
  <div class="level-bottom">
   <div class="level-info">Second-level members<br>Earn from eligible team activity</div>
   <div class="commission">5%</div>
  </div>
 </div>

 <div class="level-card">
  <div class="level-top">
   <div class="level-name">Level 3</div>
   <div class="level-count">0 members</div>
  </div>
  <div class="level-bottom">
   <div class="level-info">Third-level members<br>Earn from eligible team activity</div>
   <div class="commission">1%</div>
  </div>
 </div>

 <div class="team-card invite-info">
  <div class="team-section-title">Your invitation</div>
  <div class="invite-code">
   <div>
    <div class="invite-code-label">Invitation code</div>
    <div class="invite-code-value">Available in Invite</div>
   </div>
   <a class="invite-code-button" href="/invite">Open Invite</a>
  </div>
 </div>

</div>

<div class="team-bottom">
 <a href="/home"><i>⌂</i>Home</a>
 <a href="/raffle"><i>▣</i>Raffle</a>
 <a href="/support"><i>▤</i>Chats</a>
 <a href="/invest"><i>▦</i>AI</a>
 <a href="/income"><i>₿</i>Income</a>
 <a class="active" href="/my"><i>♙</i>My</a>
</div>
"""

setup_manager(app, db, S)


@app.route("/income")
def income_page():
    if "uid" not in session:
        return redirect("/login")

    c=db()
    c.execute("CREATE TABLE IF NOT EXISTS ai_machines(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,name TEXT NOT NULL,started_at TEXT DEFAULT CURRENT_TIMESTAMP,status TEXT DEFAULT 'RUNNING')")
    rows=c.execute("SELECT name,started_at,status FROM ai_machines WHERE uid=? ORDER BY id DESC",(session["uid"],)).fetchall()
    c.close()

    items=""
    for r in rows:
        items += '<div class="machine"><b>▦ '+html.escape(r["name"])+'</b><span>● '+html.escape(r["status"])+'</span><small>Started: '+html.escape(r["started_at"])+'</small></div>'

    if not items:
        items='<div class="empty"><div>No active machines yet.</div><small>Activate a machine on the AI tab to see it here.</small><a href="/invest">Browse AI machines</a></div>'

    page = S + '<style>'
    page += 'body{margin:0;background:#000;background-image:radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);background-size:18px 18px;background-position:0 0;;color:#fff;font-family:Georgia,serif}'
    page += '.inc{min-height:100vh;padding:25px 14px 95px}'
    page += '.title{text-align:center;color:#00baff;font-size:30px;font-weight:bold;margin:10px 0 28px}'
    page += '.machine,.empty{background:#02090e;border:1px solid #078cff;border-radius:22px;padding:22px;margin-bottom:15px}'
    page += '.machine b{display:block;color:#00baff;font-size:21px}'
    page += '.machine span{display:block;color:#20dc75;margin-top:8px}'
    page += '.machine small{display:block;color:#888;margin-top:8px}'
    page += '.empty{text-align:center;padding:55px 18px}'
    page += '.empty div{font-size:22px;color:#ddd;margin-bottom:15px}'
    page += '.empty small{display:block;color:#aaa;margin-bottom:25px}'
    page += '.empty a{display:inline-block;background:#08baf0;color:#fff;text-decoration:none;padding:14px 25px;border-radius:25px;font-weight:bold}'
    page += '.nav{position:fixed;bottom:0;left:0;right:0;height:72px;background:#000;border-top:1px solid #123;display:grid;grid-template-columns:repeat(6,1fr)}'
    page += '.nav a{color:#fff;text-decoration:none;text-align:center;padding-top:9px;font-size:12px}'
    page += '.nav i{display:block;font-style:normal;font-size:25px}'
    page += '.active{color:#00baff!important}'
    page += '</style><div class="inc"><div class="title">Income</div>'+items+'</div>'
    page += '<div class="nav"><a href="/home"><i>⌂</i>Home</a><a href="/raffle"><i>▣</i>Raffle</a><a href="/support"><i>▤</i>Chats</a><a href="/invest"><i>▦</i>AI</a><a class="active" href="/income"><i>₿</i>Income</a><a href="/my"><i>♙</i>My</a></div>'
    return page.replace(
        "<body>",
        '<body>',
        1
    )



@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    if "uid" not in session:
        return redirect("/login")

    con = sqlite3.connect(DB)

    con.execute("""
        CREATE TABLE IF NOT EXISTS deposit_requests(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            method TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_number TEXT NOT NULL,
            transaction_id TEXT,
            amount_sent REAL DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        con.execute("ALTER TABLE deposit_requests ADD COLUMN amount_sent REAL DEFAULT 0")
        con.commit()
    except sqlite3.OperationalError:
        pass

    method = request.args.get("method", "").strip()

    if request.method == "POST":
        method = request.form.get("method", "").strip()
        amount = request.form.get("amount", "").strip()
        payment_number = request.form.get("payment_number", "").strip()
        transaction_id = request.form.get("transaction_id", "").strip()
        amount_sent = request.form.get("amount_sent", "").strip()

        errors = []

        if method not in ("MTN UG", "Airtel UG"):
            errors.append("Please select MTN UG or Airtel UG.")

        try:
            amount_value = float(amount)
            if amount_value <= 0:
                errors.append("Enter a valid amount.")
        except:
            amount_value = 0
            errors.append("Enter a valid amount.")

        try:
            amount_sent_value = float(amount_sent)
            if amount_sent_value <= 0:
                errors.append("Enter the amount you sent.")
        except:
            amount_sent_value = 0
            errors.append("Enter the amount you sent.")

        if not payment_number:
            errors.append("Enter the mobile number you paid from.")

        if not transaction_id:
            errors.append("Enter the transaction ID.")

        if errors:
            con.close()
            return render_template_string("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Deposit</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:#000;background-image:radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);background-size:18px 18px;background-position:0 0;;color:#fff;font-family:Arial,sans-serif}
.wrap{max-width:600px;margin:auto;padding:18px 14px 95px}
.top{display:flex;align-items:center;gap:14px;margin-bottom:18px}
.back{width:45px;height:45px;border:1px solid #00aaff;border-radius:14px;color:#00c8ff;text-decoration:none;font-size:30px;text-align:center;line-height:40px}
.title{font-size:25px;font-weight:900;color:#00bfff}
.wave{height:4px;background:#00aaff;box-shadow:0 0 15px #008cff;border-radius:20px;margin-bottom:20px}
.card{background:#02080e;border:1px solid #008cff;border-radius:20px;padding:18px;margin-bottom:15px;box-shadow:0 0 20px rgba(0,140,255,.15)}
label{display:block;color:#a9c0d0;font-size:13px;margin:14px 0 7px}
input{width:100%;height:52px;background:#020509;color:#fff;border:1px solid #087db8;border-radius:14px;padding:0 14px;font-size:16px;outline:none}
button{width:100%;height:52px;border:0;border-radius:14px;background:#08aeea;color:#fff;font-size:16px;font-weight:900;margin-top:18px}
.error{background:#250708;border:1px solid #ff4b4b;color:#ff9999;padding:13px;border-radius:14px;margin-bottom:15px}
.nav{position:fixed;bottom:0;left:0;right:0;height:76px;background:#000;border-top:1px solid #12394e;display:grid;grid-template-columns:repeat(6,1fr);z-index:20}
.nav a{color:#fff;text-decoration:none;text-align:center;font-size:11px;padding-top:12px}
.nav b{display:block;font-size:25px}
</style>

<style id="codex-nav-fixed-size">
.bottom-nav{
 position:fixed !important;
 left:0 !important;
 right:0 !important;
 bottom:0 !important;
 width:100% !important;
 height:108px !important;
 min-height:108px !important;
 max-height:108px !important;
 display:flex !important;
 flex-direction:row !important;
 box-sizing:border-box !important;
 z-index:99999 !important;
}
.bottom-nav .nav-item{
 flex:1 1 0 !important;
 width:16.666666% !important;
 min-width:0 !important;
 max-width:none !important;
 height:108px !important;
 min-height:108px !important;
 max-height:108px !important;
 display:flex !important;
 flex-direction:column !important;
 align-items:center !important;
 justify-content:center !important;
 box-sizing:border-box !important;
 margin:0 !important;
 padding:8px 0 !important;
}
.bottom-nav .nav-icon{
 width:32px !important;
 height:32px !important;
 min-width:32px !important;
 max-width:32px !important;
 min-height:32px !important;
 max-height:32px !important;
 display:flex !important;
 align-items:center !important;
 justify-content:center !important;
 margin:0 0 5px 0 !important;
}
.bottom-nav .nav-icon svg{
 width:30px !important;
 height:30px !important;
}
</style>
</head>
<body>
<div class="wrap">
<div class="top"><a class="back" href="/deposit">‹</a><div class="title">Deposit</div></div>
<div class="wave"></div>
<div class="error">{{ errors|join(" ") }}</div>
<div class="card">
<form method="POST">
<input type="hidden" name="method" value="{{ method }}">
<label>Deposit amount</label>
<input name="amount" type="number" value="{{ amount }}" required>

<label>Mobile number you paid from</label>
<input name="payment_number" value="{{ payment_number }}" required>

<label>Transaction ID</label>
<input name="transaction_id" value="{{ transaction_id }}" required>

<label>Amount sent</label>
<input name="amount_sent" type="number" value="{{ amount_sent }}" required>

<button type="submit">CONTINUE</button>
</form>
</div>
</div>
<div class="nav">
<a href="/home"><b>⌂</b>Home</a>
<a href="/raffle"><b>▣</b>Raffle</a>
<a href="/support"><b>▤</b>Chats</a>
<a href="/invest"><b>▦</b>AI</a>
<a href="/income"><b>₿</b>Income</a>
<a href="/my"><b>♙</b>My</a>
</div>

<script id="codex-nav-active">
(function(){
 const path=window.location.pathname;
 document.querySelectorAll('.bottom-nav .nav-item').forEach(function(item){
   const href=item.getAttribute('href');
   item.classList.remove('active');

   if(
      (path==='/' && href==='/home') ||
      path===href ||
      (href!=='/home' && path.startsWith(href+'/'))
   ){
      item.classList.add('active');
   }
 });
})();
</script>


<script id="codex-app-navigation">
(function(){
  const routes=["/home","/raffle","/support","/invest","/income","/my"];
  const cache={};
  const loading={};

  function preload(url){
    if(cache[url] || loading[url]) return loading[url];

    loading[url]=fetch(url,{
      credentials:"same-origin",
      cache:"default"
    }).then(function(r){
      if(!r.ok) throw new Error("Navigation failed");
      return r.text();
    }).then(function(html){
      cache[url]=html;
      return html;
    }).catch(function(){
      return null;
    });

    return loading[url];
  }

  // Start preparing every page silently in the background.
  routes.forEach(function(url){
    setTimeout(function(){ preload(url); },100);
  });

  function runScripts(container){
    container.querySelectorAll("script").forEach(function(oldScript){
      if(oldScript.id==="codex-app-navigation") return;

      const script=document.createElement("script");

      Array.from(oldScript.attributes).forEach(function(attr){
        script.setAttribute(attr.name,attr.value);
      });

      script.textContent=oldScript.textContent;
      oldScript.replaceWith(script);
    });
  }

  async function go(url,addHistory){
    if(url===window.location.pathname) return;

    let html=cache[url];

    if(!html){
      html=await preload(url);
    }

    if(!html){
      window.location.href=url;
      return;
    }

    const doc=new DOMParser().parseFromString(html,"text/html");

    // Keep the current browser document alive.
    // Replace only the displayed application content.
    const newBody=doc.body;
    const oldScroll=window.scrollY;

    document.body.innerHTML=newBody.innerHTML;

    // Copy page-specific body attributes.
    Array.from(newBody.attributes).forEach(function(attr){
      document.body.setAttribute(attr.name,attr.value);
    });

    // Re-run page scripts.
    runScripts(document.body);

    if(addHistory){
      history.pushState({codexNav:true}, "", url);
    }

    window.scrollTo(0,0);

    // Reconnect the navigation after the body was replaced.
    install();
  }

  function install(){
    document.querySelectorAll(".bottom-nav a").forEach(function(link){
      if(link.dataset.codexNavInstalled==="1") return;

      link.dataset.codexNavInstalled="1";

      const url=new URL(link.href,window.location.origin).pathname;

      link.addEventListener("click",function(e){
        if(
          url!=="/home" &&
          url!=="/raffle" &&
          url!=="/support" &&
          url!=="/invest" &&
          url!=="/income" &&
          url!=="/my"
        ) return;

        e.preventDefault();
        e.stopPropagation();

        // Begin fetching before anything visibly changes.
        go(url,true);
      });

      link.addEventListener("touchstart",function(){
        preload(url);
      },{passive:true});
    });
  }

  window.addEventListener("popstate",function(){
    go(window.location.pathname,false);
  });

  install();
})();
</script>
</body>
</html>
""", errors=errors, method=method, amount=amount,
amount_sent=amount_sent, payment_number=payment_number,
transaction_id=transaction_id)

        con.execute("""
            INSERT INTO deposit_requests
            (uid, method, amount, payment_number, transaction_id, amount_sent, status)
            VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
        """, (
            session["uid"],
            method,
            amount_value,
            payment_number,
            transaction_id,
            amount_sent_value
        ))

        con.commit()
        con.close()

        return render_template_string("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Deposit Pending</title>
<style>
body{margin:0;background:#000;color:#fff;font-family:Arial;text-align:center}
.box{margin:100px 18px;padding:30px 20px;background:#030a10;border:1px solid #00aaff;border-radius:22px;box-shadow:0 0 25px rgba(0,170,255,.2)}
.ok{font-size:55px;color:#00d084}
h2{color:#00c8ff}
p{color:#a9bdc9;line-height:1.6}
a{display:block;margin-top:25px;background:#08aeea;color:#fff;text-decoration:none;padding:15px;border-radius:14px;font-weight:900}
</style>
</head>
<body>
<div class="box">
<div class="ok">✓</div>
<h2>Deposit Request Pending</h2>
<p>Your deposit request has been submitted and is waiting for review.</p>
<a href="/home">BACK TO HOME</a>
</div>
</body>
</html>
""")

    con.close()

    # SCREEN 1: choose network
    if method not in ("MTN UG", "Airtel UG"):
        return render_template_string("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Deposit</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:#000;color:#fff;font-family:Arial,sans-serif}
.wrap{max-width:600px;margin:auto;padding:20px 14px 95px}
.title{text-align:center;color:#00c8ff;font-size:27px;font-weight:900;margin:10px 0 18px}
.wave{height:4px;background:#00aaff;border-radius:20px;box-shadow:0 0 18px #008cff;margin-bottom:22px}
.card{background:#02080e;border:1px solid #008cff;border-radius:20px;padding:20px;margin-bottom:15px;box-shadow:0 0 22px rgba(0,140,255,.15)}
.card h2{margin:0 0 8px;color:#fff}
.card p{color:#91a9b9;font-size:13px}
.choose{display:block;text-decoration:none;color:#fff;border:1px solid #087db8;background:#03070b;border-radius:17px;padding:20px;margin-top:13px;font-size:18px;font-weight:900}
.choose span{color:#00c8ff;float:right}
.nav{position:fixed;bottom:0;left:0;right:0;height:76px;background:#000;border-top:1px solid #12394e;display:grid;grid-template-columns:repeat(6,1fr);z-index:20}
.nav a{color:#fff;text-decoration:none;text-align:center;font-size:11px;padding-top:12px}
.nav b{display:block;font-size:25px}
</style>
</head>
<body>
<div class="wrap">
<div class="title">Deposit</div>
<div class="wave"></div>
<div class="card">
<h2>Choose Payment Method</h2>
<p>Select the mobile-money network you want to use.</p>

<a class="choose" href="/deposit?method=MTN%20UG">
MTN Money <span>›</span>
</a>

<a class="choose" href="/deposit?method=Airtel%20UG">
Airtel Money <span>›</span>
</a>
</div>
</div>

<div class="nav">
<a href="/home"><b>⌂</b>Home</a>
<a href="/raffle"><b>▣</b>Raffle</a>
<a href="/support"><b>▤</b>Chats</a>
<a href="/invest"><b>▦</b>AI</a>
<a href="/income"><b>₿</b>Income</a>
<a href="/my"><b>♙</b>My</a>
</div>
</body>
</html>
""")

    # SCREEN 2: selected network
    return render_template_string("""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Deposit</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:#000;color:#fff;font-family:Arial,sans-serif}
.wrap{max-width:600px;margin:auto;padding:18px 14px 95px}
.top{display:flex;align-items:center;gap:13px;margin-bottom:15px}
.back{width:45px;height:45px;border:1px solid #008cff;border-radius:14px;color:#00c8ff;text-decoration:none;font-size:30px;text-align:center;line-height:40px}
.title{color:#00c8ff;font-size:25px;font-weight:900}
.wave{height:4px;background:#00aaff;border-radius:20px;box-shadow:0 0 18px #008cff;margin-bottom:18px}
.card{background:#02080e;border:1px solid #008cff;border-radius:20px;padding:18px;margin-bottom:15px;box-shadow:0 0 24px rgba(0,140,255,.15)}
.network{font-size:21px;font-weight:900;margin-bottom:4px}
.amount{color:#a9bdc9;margin-bottom:18px}
.paybox{border:1px solid #087db8;border-radius:17px;background:#010407;padding:15px;margin-bottom:15px}
.paytitle{color:#00c8ff;font-weight:900;font-size:17px;margin-bottom:10px}
.numberbox{height:58px;border:1px solid #12658d;border-radius:14px;display:flex;align-items:center;justify-content:space-between;padding-left:14px}
.empty{color:#506875;font-size:22px}
.copy{background:#08aeea;color:#fff;border:0;border-radius:13px;padding:13px 18px;font-weight:900}
.info{color:#aabcc8;line-height:1.6;font-size:13px}
.info strong{color:#00c8ff}
label{display:block;color:#a9bdc9;font-size:13px;margin:14px 0 7px}
input{width:100%;height:52px;background:#020509;color:#fff;border:1px solid #087db8;border-radius:14px;padding:0 14px;font-size:16px;outline:none}
button.continue{width:100%;height:52px;border:0;border-radius:14px;background:#08aeea;color:#fff;font-size:16px;font-weight:900;margin-top:18px}
.nav{position:fixed;bottom:0;left:0;right:0;height:76px;background:#000;border-top:1px solid #12394e;display:grid;grid-template-columns:repeat(6,1fr);z-index:20}
.nav a{color:#fff;text-decoration:none;text-align:center;font-size:11px;padding-top:12px}
.nav b{display:block;font-size:25px}
</style>
</head>
<body>
<div class="wrap">

<div class="top">
<a class="back" href="/deposit">‹</a>
<div class="title">Deposit</div>
</div>

<div class="wave"></div>

<div class="card">

<div class="network">{{ method.replace(" UG"," Money") }}</div>
<div class="amount">Enter the amount you want to request</div>

<div class="paybox">
<div class="paytitle">Send to number</div>

<div class="numberbox">
<span class="empty"></span>
<button class="copy" type="button" onclick="copyEmpty()">▣ Copy</button>
</div>

<div class="info" style="margin-top:14px">
<strong>Payment details</strong><br>
The recipient number is intentionally not displayed here.
</div>

<div class="info" style="margin-top:12px">
<strong>How to complete your request</strong><br>
1. Complete your payment using your chosen mobile-money service.<br>
2. Return here and enter the number you paid from.<br>
3. Enter your transaction ID.<br>
4. Enter the amount you sent.<br>
5. Tap Continue.
</div>
</div>

<form method="POST">

<input type="hidden" name="method" value="{{ method }}">

<label>Amount</label>
<input type="number" name="amount" min="1" step="1"
placeholder="Enter amount" required>

<label>Mobile number you paid from</label>
<input type="text" name="payment_number"
inputmode="tel" placeholder="Enter your mobile number" required>

<label>Transaction ID</label>
<input type="text" name="transaction_id"
placeholder="Enter transaction ID" required>

<label>Amount sent</label>
<input type="number" name="amount_sent"
min="1" step="1" inputmode="numeric"
placeholder="Enter amount you sent" required>

<button class="continue" type="submit">CONTINUE</button>

</form>
</div>
</div>

<div class="nav">
<a href="/home"><b>⌂</b>Home</a>
<a href="/raffle"><b>▣</b>Raffle</a>
<a href="/support"><b>▤</b>Chats</a>
<a href="/invest"><b>▦</b>AI</a>
<a href="/income"><b>₿</b>Income</a>
<a href="/my"><b>♙</b>My</a>
</div>

<script>
function copyEmpty(){
    navigator.clipboard.writeText("").catch(function(){});
}
</script>

</body>
</html>
""", method=method)


@app.route("/invest", methods=["GET"])
def invest():
    if "uid" not in session:
        return redirect("/login")

    machines = [
        ("K1", "K Series", "AI Computing System", "ACTIVE"),
        ("K2", "K Series", "Advanced AI System", "ACTIVE"),
        ("M1", "M Series", "AI Processing Machine", "ACTIVE"),
        ("M2", "M Series", "High Performance AI", "ACTIVE"),
        ("A1", "A Series", "Advanced Computing", "ACTIVE"),
        ("A2", "A Series", "Neural Computing System", "ACTIVE"),
        ("GS1", "GS Series", "High Performance System", "ACTIVE"),
        ("GS2", "GS Series", "Enterprise Computing", "ACTIVE")
    ]

    html = """


<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">

<title>CODEX700 AI</title>

<style>
*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    -webkit-tap-highlight-color:transparent;
}

html,body{background:#000;background-image:radial-gradient(circle,rgba(0,190,255,.45) 1.2px,transparent 1.8px);background-size:18px 18px;background-position:0 0;
    background:#000;
    color:#fff;
    font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    overflow-x:hidden;
    touch-action:pan-y;
}

body{
    padding-bottom:90px;
}

.ai-page{
    min-height:100vh;
    background:#000;
    padding:18px 12px 100px;
}

.ai-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:18px;
}

.ai-logo{
    font-size:27px;
    font-weight:900;
    letter-spacing:1px;
    color:#fff;
}

.ai-logo span{
    color:#00b7ff;
}

.ai-title{
    text-align:center;
    font-size:22px;
    font-weight:800;
    color:#fff;
    margin:4px 0 5px;
}

.ai-subtitle{
    text-align:center;
    color:#8ea6b5;
    font-size:12px;
    margin-bottom:18px;
}

.series-tabs{
    width:100%;
    display:flex;
    gap:7px;
    overflow-x:auto;
    padding:3px 1px 10px;
    scrollbar-width:none;
}

.series-tabs::-webkit-scrollbar{
    display:none;
}

.series-tab{
    flex:0 0 auto;
    border:1px solid rgba(0,183,255,.45);
    background:#050b10;
    color:#a9c0cd;
    border-radius:20px;
    padding:9px 16px;
    font-size:12px;
    font-weight:700;
    text-decoration:none;
}

.series-tab.active{
    color:#00b7ff;
    border-color:#00b7ff;
    box-shadow:0 0 12px rgba(0,183,255,.18);
}

.machine-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px;
    margin-top:8px;
}

.machine-card{
    position:relative;
    min-width:0;
    overflow:hidden;
    background:
      radial-gradient(circle at 50% 20%,rgba(0,174,255,.12),transparent 45%),
      #05090d;
    border:1px solid rgba(0,183,255,.35);
    border-radius:17px;
    padding:10px;
    box-shadow:0 0 18px rgba(0,140,255,.08);
}

.machine-card:before{
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    background:linear-gradient(
      135deg,
      rgba(0,183,255,.06),
      transparent 45%,
      rgba(0,183,255,.03)
    );
}

.machine-image{
    height:125px;
    border-radius:12px;
    border:1px solid rgba(0,183,255,.20);
    background:
      radial-gradient(circle at center,rgba(0,183,255,.18),transparent 45%),
      linear-gradient(135deg,#020609,#07131b);
    display:flex;
    align-items:center;
    justify-content:center;
    position:relative;
    overflow:hidden;
    margin-bottom:10px;
}

.machine-image:after{
    content:"";
    position:absolute;
    width:75%;
    height:1px;
    background:rgba(0,183,255,.45);
    box-shadow:0 0 12px #00b7ff;
}

.machine-code{
    position:relative;
    z-index:2;
    font-size:31px;
    font-weight:900;
    color:#00b7ff;
    letter-spacing:1px;
    text-shadow:0 0 14px rgba(0,183,255,.7);
}

.machine-series{
    color:#00b7ff;
    font-size:10px;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:.8px;
}

.machine-name{
    margin-top:4px;
    min-height:34px;
    font-size:13px;
    font-weight:800;
    color:#fff;
    line-height:1.25;
}

.machine-status{
    margin-top:7px;
    color:#6f8290;
    font-size:10px;
}

.machine-status span{
    color:#00b7ff;
}

.ai-form{
    margin-top:10px;
}

.ai-btn{
    width:100%;
    height:43px;
    border:1px solid #00aaff;
    border-radius:22px;
    background:#00aaff;
    color:#000;
    font-size:13px;
    font-weight:900;
    cursor:pointer;
    -webkit-appearance:none;
    appearance:none;
    outline:none;
    padding:0;
}

.ai-btn:active,
.ai-btn:focus,
.ai-btn:hover{
    transform:none!important;
    scale:1!important;
}

.bottom-nav{
    position:fixed;
    z-index:100;
    left:0;
    right:0;
    bottom:0;
    height:76px;
    background:#000;
    border-top:1px solid rgba(0,174,255,.22);
    display:grid;
    grid-template-columns:repeat(6,1fr);
    padding-bottom:env(safe-area-inset-bottom);
}

.nav-item{
    color:#fff;
    text-decoration:none;
    text-align:center;
    font-size:12px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    gap:3px;
    min-width:0;
}

.nav-icon{
    font-size:27px;
    line-height:28px;
}

.nav-item.active{
    color:#00b7ff;
}

@media(max-width:380px){
    .ai-page{
        padding-left:10px;
        padding-right:10px;
    }

    .machine-grid{
        gap:9px;
    }

    .machine-image{
        height:112px;
    }

    .machine-code{
        font-size:27px;
    }
}

@media(min-width:700px){
    .machine-grid{
        grid-template-columns:repeat(4,minmax(0,1fr));
    }

    .ai-page{
        max-width:1100px;
        margin:auto;
    }
}
</style>
</head>

<body>

<div class="ai-page">

    <div class="ai-header">
        <div class="ai-logo">CODEX<span>700</span></div>
    </div>

    <div class="ai-title">AI COMPUTING</div>
    <div class="ai-subtitle">
        Explore CODEX700 virtual computing systems
    </div>

    <div class="series-tabs">
        <a class="series-tab active" href="/invest">All</a>
        <a class="series-tab" href="/invest?series=K">K Series</a>
        <a class="series-tab" href="/invest?series=M">M Series</a>
        <a class="series-tab" href="/invest?series=A">A Series</a>
        <a class="series-tab" href="/invest?series=GS">GS Series</a>
    </div>

    <div class="machine-grid">
    {% for code, series, name, status in machines %}
        <div class="machine-card">

            <div class="machine-image">
                <div class="machine-code">{{ code }}</div>
            </div>

            <div class="machine-series">{{ series }}</div>

            <div class="machine-name">
                {{ name }}
            </div>

            <div class="machine-status">
                STATUS:
                <span>{{ status }}</span>
            </div>

            <form class="ai-form"
                  method="POST"
                  action="/ai/activate/Codex_{{ code }}">
                <input
                    class="ai-btn"
                    type="submit"
                    value="ACTIVATE"
                >
            </form>

        </div>
    {% endfor %}
    </div>

</div>

<div class="bottom-nav">
 <a class="nav-item" href="/home">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><ellipse cx="20" cy="8" rx="12" ry="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 8v21c0 3 5 6 12 6s12-3 12-6V8M8 18c0 3 5 6 12 6s12-3 12-6M8 28c0 3 5 6 12 6s12-3 12-6" fill="none" stroke="currentColor" stroke-width="3"/></svg></span>
  <span>Home</span>
 </a>
 <a class="nav-item" href="/raffle">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="6" y="7" width="16" height="16" rx="2" fill="currentColor"/><rect x="18" y="17" width="16" height="16" rx="2" fill="currentColor"/><rect x="10" y="11" width="8" height="8" fill="#000"/></svg></span>
  <span>Raffle</span>
 </a>
 <a class="nav-item" href="/support">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="5" y="7" width="27" height="20" rx="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M12 27l-2 7 8-7M12 14h13M12 20h9" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="31" cy="29" r="4" fill="currentColor"/></svg></span>
  <span>chats</span>
 </a>
 <a class="nav-item" href="/invest">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="9" y="8" width="22" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="3"/><path d="M5 14h4M5 20h4M5 26h4M31 14h4M31 20h4M31 26h4M15 4v4M21 4v4M27 4v4M15 32v4M21 32v4M27 32v4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><rect x="14" y="14" width="12" height="12" rx="2" fill="currentColor"/></svg></span>
  <span>AI</span>
 </a>
 <a class="nav-item" href="/income">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><path d="M24 5l-3 30M29 10c-3-3-12-3-15 2-4 7 12 5 11 12-1 7-12 8-16 3M12 14h18M9 28h18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
  <span>Income</span>
 </a>
 <a class="nav-item" href="/my">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><circle cx="20" cy="11" r="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 35c0-8 5-12 12-12s12 4 12 12" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></span>
  <span>My</span>
 </a>
</div>

</body>
</html>
"""

    return render_template_string(html, machines=machines)

@app.route("/ai/activate/<machine_name>", methods=["POST"])
def activate_ai_machine(machine_name):
    if "uid" not in session:
        return redirect("/login")

    allowed={
        "Codex_M1":"Codex M1",
        "Codex_M2":"Codex M2",
        "Codex_M3":"Codex M3",
        "Codex_M4":"Codex M4",
        "Codex_M5":"Codex M5",
        "Codex_M6":"Codex M6",
        "Codex_M7":"Codex M7"
    }

    name=allowed.get(machine_name)
    if not name:
        return redirect("/invest")

    con=sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS ai_machines(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            name TEXT NOT NULL,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'RUNNING'
        )
    """)

    # Keep this as virtual machine activation only.
    con.execute(
        "INSERT INTO ai_machines(uid,name,status) VALUES(?,?,?)",
        (session["uid"],name,"RUNNING")
    )
    con.commit()
    con.close()

    return redirect("/income")


@app.route("/invite")
def invite_page():
    if "uid" not in session:
        return redirect("/login")

    c = db()
    user = c.execute(
        "SELECT refcode FROM users WHERE id=?",
        (session["uid"],)
    ).fetchone()
    c.close()

    refcode = user["refcode"] if user and user["refcode"] else "CODEX700"
    invite_link = "https://codex700com.onrender.com/register?ref=" + refcode

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Invite Friends</title>

<style>
*{
    box-sizing:border-box;
    -webkit-tap-highlight-color:transparent;
}

html,body{
    margin:0;
    padding:0;
    width:100%;
    min-height:100%;
}

body{
    background:#00050a;
    color:#fff;
    font-family:Georgia,"Times New Roman",serif;
    background-image:
        radial-gradient(circle,#06314a 1.2px,transparent 1.4px);
    background-size:18px 18px;
}

.invite-page{
    width:100%;
    max-width:480px;
    margin:auto;
    padding-bottom:105px;
}

/* HEADER */
.invite-header{
    height:82px;
    display:flex;
    align-items:center;
    justify-content:center;
    position:relative;
    border-bottom:1px solid #08bfff55;
    background:#00050a;
}

.invite-back{
    position:absolute;
    left:28px;
    top:14px;
    width:64px;
    height:64px;
    border:1px solid #00bfff;
    border-radius:18px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#00bfff;
    font-family:Arial,sans-serif;
    font-size:43px;
    text-decoration:none;
    box-shadow:0 0 12px #00bfff33;
}

.invite-title{
    color:#08bfff;
    font-size:28px;
    font-weight:bold;
    letter-spacing:.3px;
    text-shadow:0 0 10px #00bfff66;
}

/* CARDS */
.invite-card{
    margin:24px 28px 0;
    padding:28px;
    border:1px solid #00bfff;
    border-radius:22px;
    background:rgba(0,7,13,.90);
    box-shadow:
        0 0 12px #00bfff22,
        inset 0 0 22px #00bfff0b;
}

.invite-card h2{
    margin:0 0 18px;
    color:#08bfff;
    font-size:22px;
    font-weight:bold;
}

.small-text{
    color:#c7c7c7;
    font-size:17px;
    line-height:1.65;
}

.code-label{
    color:#08bfff;
    text-align:center;
    font-size:16px;
    margin-bottom:10px;
}

.code{
    text-align:center;
    font-family:Arial,sans-serif;
    font-size:30px;
    font-weight:bold;
    letter-spacing:4px;
    margin:8px 0 20px;
}

.link-box{
    width:100%;
    padding:14px;
    border:1px solid #00bfff77;
    border-radius:10px;
    background:#000308;
    color:#d8f7ff;
    font-family:Arial,sans-serif;
    font-size:14px;
    line-height:1.5;
    word-break:break-all;
}

.button-row{
    display:flex;
    gap:14px;
    margin-top:18px;
}

.invite-btn{
    flex:1;
    min-height:58px;
    border:1px solid #00bfff;
    border-radius:12px;
    background:#03b8ee;
    color:#001018;
    font-family:Georgia,"Times New Roman",serif;
    font-size:19px;
    font-weight:bold;
    box-shadow:0 0 12px #00bfff33;
}

.outline-btn{
    background:#00070d;
    color:#fff;
}

/* QR */
.qr-title{
    text-align:center;
    color:#cfcfcf !important;
    font-size:22px !important;
    margin-bottom:12px !important;
}

.qr-description{
    text-align:center;
    color:#bdbdbd;
    font-size:16px;
    line-height:1.5;
}

.qr{
    display:block;
    width:340px;
    height:340px;
    max-width:100%;
    margin:24px auto;
    padding:12px;
    background:#fff;
    border-radius:24px;
}

/* STATS */
.stats{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:20px;
}

.stat{
    overflow:hidden;
    border:1px solid #00bfff;
    border-radius:20px;
    background:#fff;
    text-align:center;
    box-shadow:0 0 14px #00bfff22;
}

.stat-number{
    height:88px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#080d14;
    font-size:29px;
    font-weight:bold;
}

.stat-label{
    min-height:53px;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:8px;
    background:#08bfff;
    color:#fff;
    font-size:17px;
}

/* COMMISSION */
.commission-title{
    color:#08bfff !important;
}

.commission-text{
    color:#d4d4d4;
    font-size:17px;
    line-height:1.65;
}

.commission-text strong{
    color:#fff;
}

/* BOTTOM NAVIGATION */
.bottom-nav{
    position:fixed;
    left:0;
    right:0;
    bottom:0;
    width:100%;
    height:92px;
    z-index:1000;
    display:grid;
    grid-template-columns:repeat(6,1fr);
    background:#000;
    border-top:1px solid #08bfff55;
}

.bottom-nav a{
    min-width:0;
    height:92px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    gap:4px;
    text-decoration:none;
    color:#fff;
    font-family:Georgia,"Times New Roman",serif;
    font-size:15px;
    white-space:nowrap;
}

.bottom-nav .nav-icon{
    height:38px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family:Arial,sans-serif;
    font-size:29px;
    line-height:1;
}

.bottom-nav .active{
    color:#08bfff;
}

.bottom-nav a:active{
    opacity:.75;
}

@media(max-width:360px){
    .bottom-nav a{
        font-size:12px;
    }
    .bottom-nav .nav-icon{
        font-size:25px;
    }
    .invite-card{
        margin-left:20px;
        margin-right:20px;
        padding:22px;
    }
}
</style>
</head>

<body>

<div class="invite-page">

    <div class="invite-header">
        <a class="invite-back" href="/my">‹</a>
        <div class="invite-title">Invite Friends</div>
    </div>

    <div class="invite-card">
        <div class="code-label">Your invitation code</div>

        <div class="code" id="refcode">{{ refcode }}</div>

        <button class="invite-btn"
                onclick="copyText('{{ refcode }}')">
            Copy code
        </button>
    </div>

    <div class="invite-card">
        <h2>Invitation link</h2>

        <div class="link-box" id="inviteLink">
            {{ invite_link }}
        </div>

        <div class="button-row">
            <button class="invite-btn"
                    onclick="copyText('{{ invite_link }}')">
                Copy link
            </button>

            <button class="invite-btn outline-btn"
                    onclick="shareLink()">
                Share
            </button>
        </div>
    </div>

    <div class="invite-card">
        <h2 class="qr-title">Scan to register</h2>

        <div class="qr-description">
            Friends scan this code with their phone camera to open your registration link.
        </div>

        <img class="qr"
             src="https://api.qrserver.com/v1/create-qr-code/?size=340x340&data={{ invite_link|urlencode }}"
             alt="Invitation QR Code">

        <div class="button-row">
            <button class="invite-btn outline-btn"
                    onclick="saveQR()">
                ↓ &nbsp; Save QR
            </button>

            <button class="invite-btn outline-btn"
                    onclick="shareLink()">
                ♧ &nbsp; Share link
            </button>
        </div>
    </div>

    <div class="invite-card">
        <div class="stats">

            <div class="stat">
                <div class="stat-number">0</div>
                <div class="stat-label">Total invites</div>
            </div>

            <div class="stat">
                <div class="stat-number">0.00</div>
                <div class="stat-label">Commission earned</div>
            </div>

        </div>
    </div>

    <div class="invite-card">
        <h2 class="commission-title">Commission</h2>

        <div class="commission-text">
            <strong>Level 1 — 10% of every deposit made by people you invited directly</strong>
            <br><br>
            Level 2 and Level 3 no longer pay commission.
            You must own an active AI machine to receive commission.
        </div>
    </div>

</div>

<!-- SAME SIX MAIN NAV ITEMS -->
<div class="bottom-nav">
 <a class="nav-item" href="/home">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><ellipse cx="20" cy="8" rx="12" ry="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 8v21c0 3 5 6 12 6s12-3 12-6V8M8 18c0 3 5 6 12 6s12-3 12-6M8 28c0 3 5 6 12 6s12-3 12-6" fill="none" stroke="currentColor" stroke-width="3"/></svg></span>
  <span>Home</span>
 </a>
 <a class="nav-item" href="/raffle">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="6" y="7" width="16" height="16" rx="2" fill="currentColor"/><rect x="18" y="17" width="16" height="16" rx="2" fill="currentColor"/><rect x="10" y="11" width="8" height="8" fill="#000"/></svg></span>
  <span>Raffle</span>
 </a>
 <a class="nav-item" href="/support">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="5" y="7" width="27" height="20" rx="5" fill="none" stroke="currentColor" stroke-width="3"/><path d="M12 27l-2 7 8-7M12 14h13M12 20h9" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="31" cy="29" r="4" fill="currentColor"/></svg></span>
  <span>chats</span>
 </a>
 <a class="nav-item" href="/invest">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><rect x="9" y="8" width="22" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="3"/><path d="M5 14h4M5 20h4M5 26h4M31 14h4M31 20h4M31 26h4M15 4v4M21 4v4M27 4v4M15 32v4M21 32v4M27 32v4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><rect x="14" y="14" width="12" height="12" rx="2" fill="currentColor"/></svg></span>
  <span>AI</span>
 </a>
 <a class="nav-item" href="/income">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><path d="M24 5l-3 30M29 10c-3-3-12-3-15 2-4 7 12 5 11 12-1 7-12 8-16 3M12 14h18M9 28h18" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
  <span>Income</span>
 </a>
 <a class="nav-item" href="/my">
  <span class="nav-icon"><svg viewBox="0 0 40 40" width="30" height="30"><circle cx="20" cy="11" r="6" fill="none" stroke="currentColor" stroke-width="3"/><path d="M8 35c0-8 5-12 12-12s12 4 12 12" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></span>
  <span>My</span>
 </a>
</div>

<script>
function copyText(text){
    if(navigator.clipboard){
        navigator.clipboard.writeText(text).then(function(){
            alert("Copied successfully");
        });
    }else{
        var area=document.createElement("textarea");
        area.value=text;
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        area.remove();
        alert("Copied successfully");
    }
}

function shareLink(){
    var link="{{ invite_link }}";

    if(navigator.share){
        navigator.share({
            title:"Join Codex700",
            text:"Join Codex700 using my invitation link.",
            url:link
        });
    }else{
        copyText(link);
    }
}

function saveQR(){
    var img=document.querySelector(".qr");
    var a=document.createElement("a");
    a.href=img.src;
    a.download="codex700-invitation-qr.png";
    document.body.appendChild(a);
    a.click();
    a.remove();
}
</script>

</body>
</html>
""", refcode=refcode, invite_link=invite_link)


@app.route("/raffle")
def raffle_page():
    if "uid" not in session:
        return redirect("/login")

    uid=int(session["uid"])

    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row

    con.execute("""
        CREATE TABLE IF NOT EXISTS raffle_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reward TEXT NOT NULL,
            reward_value INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS raffle_deposit_awards(
            deposit_id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            awarded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()

    row=con.execute("""
        SELECT COALESCE(SUM(tickets),0)
        FROM raffle_tickets
        WHERE CAST(user_id AS INTEGER)=?
        AND tickets>0
    """,(uid,)).fetchone()

    chances=int(row[0] or 0)

    records=con.execute("""
        SELECT reward,reward_value,created_at
        FROM raffle_records
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 20
    """,(uid,)).fetchall()

    history=""

    if records:
        for r in records:
            history+=(
                '<div class="raffle-record">'
                '<div>'
                '<div class="raffle-record-prize">'+str(r["reward"])+'</div>'
                '<div class="raffle-record-date">'+str(r["created_at"])+'</div>'
                '</div>'
                '<div class="raffle-record-win">WON</div>'
                '</div>'
            )
    else:
        history='<div class="raffle-empty">No raffle records yet.</div>'

    con.close()

    tiles=""

    for i in range(9):
        tiles+=(
            '<button class="raffle-tile" type="button" '
            'data-index="'+str(i)+'" onclick="revealRaffle(this)">'
            '<span class="raffle-ai">'
            '<span class="raffle-ring"></span>'
            '<span class="raffle-ai-text">AI</span>'
            '</span>'
            '<span class="raffle-reward"></span>'
            '</button>'
        )

    return S+"""
<style>
html,body{
    background:#000!important;
    color:#fff!important;
}

.raffle-page{
    width:100%;
    min-height:100vh;
    box-sizing:border-box;
    padding:0 28px 145px;
    background:#000;
    color:#fff;
    position:relative;
    overflow:hidden;
}

.raffle-page:before{
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    background-image:
        radial-gradient(circle,rgba(0,190,255,.25) 1px,transparent 1.5px);
    background-size:27px 27px;
    opacity:.38;
}

.raffle-page:after{
    content:"";
    position:absolute;
    left:0;
    right:0;
    top:0;
    height:100%;
    pointer-events:none;
    background:
        radial-gradient(circle at 50% 18%,rgba(0,190,255,.08),transparent 32%),
        radial-gradient(circle at 50% 80%,rgba(0,190,255,.07),transparent 38%);
}

.raffle-header{
    height:100px;
    position:relative;
    z-index:3;
    display:flex;
    align-items:center;
    justify-content:center;
}

.raffle-back{
    position:absolute;
    left:0;
    top:27px;
    width:45px;
    height:42px;
    border-radius:13px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-decoration:none!important;
    color:#fff!important;
    font-size:28px;
    background:#02070a;
    border:1px solid rgba(0,207,255,.75);
    box-shadow:
        0 0 8px rgba(0,190,255,.28),
        inset 0 0 8px rgba(0,190,255,.08);
}

.raffle-title{
    font-size:27px;
    font-weight:700;
    color:#fff;
    text-shadow:0 0 8px rgba(0,200,255,.3);
}

.raffle-subtitle{
    position:relative;
    z-index:3;
    text-align:center;
    margin:-6px 0 20px;
    color:#87909a;
    font-size:10px;
    letter-spacing:2px;
    font-weight:600;
}

.raffle-chance-card{
    position:relative;
    z-index:3;
    padding:19px 18px 18px;
    margin-bottom:20px;
    border-radius:17px;
    background:rgba(0,0,0,.72);
    border:1px solid rgba(0,203,255,.72);
    box-shadow:
        0 0 10px rgba(0,185,255,.18),
        inset 0 0 18px rgba(0,130,180,.035);
}

.raffle-chance-top{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.raffle-chance-label{
    color:#c7cdd2;
    font-size:15px;
    font-weight:500;
}

.raffle-chance-count{
    color:#16c9ff;
    font-size:20px;
    font-weight:700;
    text-shadow:0 0 8px rgba(0,200,255,.45);
}

.raffle-chance-text{
    margin-top:9px;
    color:#8c959d;
    font-size:11px;
    line-height:1.55;
}

.raffle-grid{
    position:relative;
    z-index:3;
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:9px;
    width:100%;
    max-width:390px;
    margin:0 auto;
}

.raffle-tile{
    position:relative;
    aspect-ratio:1/1;
    padding:0;
    border-radius:15px;
    border:1px solid rgba(0,197,255,.65);
    background:
        radial-gradient(circle at 50% 50%,rgba(0,110,155,.12),transparent 48%),
        #010507;
    box-shadow:
        0 0 8px rgba(0,190,255,.17),
        inset 0 0 14px rgba(0,170,220,.04);
    overflow:hidden;
    cursor:pointer;
}

.raffle-tile:before{
    content:"";
    position:absolute;
    inset:5px;
    border-radius:11px;
    border:1px solid rgba(0,143,190,.25);
}

.raffle-ai{
    position:absolute;
    left:50%;
    top:50%;
    width:61%;
    height:61%;
    transform:translate(-50%,-50%);
    border-radius:50%;
    border:1px solid rgba(0,210,255,.65);
    box-shadow:
        0 0 7px rgba(0,200,255,.25),
        inset 0 0 8px rgba(0,200,255,.08);
    display:flex;
    align-items:center;
    justify-content:center;
}

.raffle-ai:before{
    content:"";
    position:absolute;
    width:76%;
    height:76%;
    border-radius:50%;
    border:1px solid rgba(0,205,255,.65);
    border-right-color:rgba(0,120,255,.3);
    transform:rotate(35deg);
}

.raffle-ai:after{
    content:"";
    position:absolute;
    width:108%;
    height:42%;
    border-radius:50%;
    border:1px solid rgba(0,184,255,.6);
    border-top-color:rgba(0,225,255,.85);
    transform:rotate(-34deg);
}

.raffle-ai-text{
    position:relative;
    z-index:3;
    font-size:17px;
    font-weight:800;
    color:#e8fbff;
    text-shadow:0 0 7px rgba(0,220,255,.75);
}

.raffle-reward{
    position:absolute;
    inset:0;
    z-index:5;
    display:none;
    align-items:center;
    justify-content:center;
    text-align:center;
    padding:6px;
    font-size:12px;
    font-weight:800;
    color:#eafcff;
    text-shadow:0 0 8px rgba(0,220,255,.7);
}

.raffle-tile.revealed{
    border-color:#11d3ff;
    box-shadow:
        0 0 14px rgba(0,205,255,.42),
        inset 0 0 15px rgba(0,205,255,.08);
}

.raffle-tile.revealed .raffle-ai{
    display:none;
}

.raffle-tile.revealed .raffle-reward{
    display:flex;
}

.raffle-rewards-title,
.raffle-record-title{
    position:relative;
    z-index:3;
    margin:25px 2px 11px;
    color:#d9dee2;
    font-size:18px;
    font-weight:500;
}

.raffle-rewards{
    position:relative;
    z-index:3;
    padding:14px;
    border-radius:17px;
    background:rgba(0,0,0,.72);
    border:1px solid rgba(0,198,255,.58);
    box-shadow:
        0 0 10px rgba(0,180,255,.14),
        inset 0 0 16px rgba(0,150,210,.035);
}

.reward-list{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:8px;
}

.reward-item{
    min-height:42px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    padding:5px;
    box-sizing:border-box;
    border-radius:10px;
    color:#b9c1c7;
    font-size:10px;
    font-weight:500;
    background:#020608;
    border:1px solid rgba(0,145,190,.34);
}

.reward-item.flash{
    color:#fff;
    border-color:rgba(0,207,255,.72);
    box-shadow:0 0 8px rgba(0,190,255,.18);
}

.raffle-change-note{
    text-align:center;
    margin:11px 0 0;
    color:#69747d;
    font-size:9px;
}

.raffle-big-win{
    position:relative;
    z-index:3;
    margin:15px 0 0;
    padding:14px;
    text-align:center;
    border-radius:16px;
    color:#12c9ff;
    font-size:11px;
    font-weight:600;
    letter-spacing:.5px;
    background:#010506;
    border:1px solid rgba(0,190,255,.48);
    box-shadow:0 0 10px rgba(0,180,255,.12);
}

.raffle-records{
    position:relative;
    z-index:3;
    border-radius:17px;
    padding:4px 14px;
    background:rgba(0,0,0,.72);
    border:1px solid rgba(0,198,255,.52);
    box-shadow:0 0 10px rgba(0,180,255,.12);
}

.raffle-record{
    min-height:55px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    border-bottom:1px solid rgba(0,150,200,.18);
}

.raffle-record:last-child{
    border-bottom:0;
}

.raffle-record-prize{
    color:#d8dde1;
    font-size:13px;
    font-weight:500;
}

.raffle-record-date{
    color:#66727b;
    font-size:9px;
    margin-top:4px;
}

.raffle-record-win{
    color:#10c8ff;
    font-size:9px;
    font-weight:700;
}

.raffle-empty{
    color:#66727b;
    font-size:12px;
    padding:18px 0;
    text-align:center;
}

.raffle-toast{
    position:fixed;
    left:50%;
    bottom:94px;
    transform:translateX(-50%);
    z-index:9999;
    min-width:230px;
    max-width:86%;
    padding:13px 17px;
    border-radius:14px;
    text-align:center;
    background:#02090c;
    border:1px solid #10c8ff;
    box-shadow:0 0 16px rgba(0,190,255,.25);
    color:#e5faff;
    font-size:12px;
    font-weight:600;
    opacity:0;
    pointer-events:none;
    transition:.25s;
}

.raffle-toast.show{
    opacity:1;
}

@media(max-width:390px){
    .raffle-page{
        padding-left:28px;
        padding-right:28px;
    }

    .raffle-grid{
        gap:7px;
    }

    .raffle-ai-text{
        font-size:15px;
    }

    .reward-item{
        font-size:9px;
    }
}
</style>

<div class="raffle-page">
<div class="raffle-header">
<a class="raffle-back" href="/home">‹</a>
<div class="raffle-title">Raffle</div>
</div>

<div class="raffle-subtitle">SPIN • REVEAL • WIN</div>

<div class="raffle-chance-card">
<div class="raffle-chance-top">
<div class="raffle-chance-label">Your chances</div>
<div class="raffle-chance-count"><span id="raffleChances">""" + str(chances) + """</span> / """ + str(chances) + """</div>
</div>
<div class="raffle-chance-text">
Get 1 chance for every successful deposit you make.
</div>
</div>

<div class="raffle-grid" id="raffleGrid">
""" + tiles + """
</div>

<div class="raffle-rewards-title">Possible Rewards</div>
<div class="raffle-rewards">
<div class="reward-list" id="rewardList">
<div class="reward-item">UGX 1,000</div>
<div class="reward-item">UGX 5,000</div>
<div class="reward-item">UGX 10,000</div>
<div class="reward-item">UGX 10,000</div>
<div class="reward-item">Z1 MACHINE</div>
<div class="reward-item">UGX 100,000</div>
<div class="reward-item">UGX 1,000,000</div>
<div class="reward-item">UGX 500</div>
<div class="reward-item">UGX 2,000</div>
</div>
<div class="raffle-change-note">Rewards change every few seconds...</div>
</div>

<div class="raffle-big-win">
✦ BIG WIN ✦<br>Your next reveal could be the one!
</div>

<div class="raffle-record-title">My records</div>
<div class="raffle-records">
""" + history + """
</div>
</div>

<div class="raffle-toast" id="raffleToast"></div>

<script>
const rewards=[
"UGX 1,000","UGX 5,000","UGX 10,000","UGX 10,000",
"Z1 MACHINE","UGX 100,000","UGX 1,000,000","UGX 500","UGX 2,000"
];

let preview=rewards.slice();

function shuffle(a){
 for(let i=a.length-1;i>0;i--){
  const j=Math.floor(Math.random()*(i+1));
  [a[i],a[j]]=[a[j],a[i]];
 }
 return a;
}

function rotateRewards(){
 preview=shuffle(preview);
 document.querySelectorAll(".reward-item").forEach((item,i)=>{
  item.textContent=preview[i];
  item.classList.remove("flash");
  void item.offsetWidth;
  item.classList.add("flash");
 });
}

function showToast(msg){
 const t=document.getElementById("raffleToast");
 t.textContent=msg;
 t.classList.add("show");
 setTimeout(()=>t.classList.remove("show"),2500);
}

async function revealRaffle(tile){
 const box=document.getElementById("raffleChances");
 const chances=parseInt(box.textContent||"0",10);

 if(chances<=0){
  showToast("No raffle chance. Make a successful deposit first.");
  return;
 }

 document.querySelectorAll(".raffle-tile").forEach(x=>x.disabled=true);

 try{
  const r=await fetch("/raffle/reveal",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({tile:parseInt(tile.dataset.index,10)})
  });

  const d=await r.json();

  if(!d.ok){
   showToast(d.message||"Unable to reveal.");
   document.querySelectorAll(".raffle-tile").forEach(x=>x.disabled=false);
   return;
  }

  tile.querySelector(".raffle-reward").textContent=d.reward;
  tile.classList.add("revealed");
  box.textContent=d.chances;
  showToast("Congratulations! You won "+d.reward);
  setTimeout(()=>location.reload(),1800);

 }catch(e){
  showToast("Connection error.");
  document.querySelectorAll(".raffle-tile").forEach(x=>x.disabled=false);
 }
}

rotateRewards();
setInterval(rotateRewards,1000);
</script>
"""

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)



@app.route("/raffle/reveal", methods=["POST"])
def raffle_reveal():
    if "uid" not in session:
        return {"ok":False,"message":"Please log in first."},401

    uid=int(session["uid"])

    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row

    con.execute("""
        CREATE TABLE IF NOT EXISTS raffle_records(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reward TEXT NOT NULL,
            reward_value INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        con.execute("BEGIN IMMEDIATE")

        ticket=con.execute("""
            SELECT id
            FROM raffle_tickets
            WHERE CAST(user_id AS INTEGER)=?
            AND tickets>0
            ORDER BY id ASC
            LIMIT 1
        """,(uid,)).fetchone()

        if not ticket:
            con.rollback()
            return {"ok":False,"message":"No raffle chance available."},400

        con.execute("""
            UPDATE raffle_tickets
            SET tickets=tickets-1
            WHERE id=? AND tickets>0
        """,(ticket["id"],))

        import random

        rewards=[
            ("UGX 1,000",1000,110),
            ("UGX 500",500,30),
            ("UGX 2,000",2000,20),
            ("UGX 5,000",5000,16),
            ("UGX 10,000",10000,8),
            ("UGX 10,000",10000,6),
            ("Z1 Machine",0,6),
            ("UGX 100,000",100000,3),
            ("UGX 1,000,000",1000000,1)
        ]

        reward,value,weight=random.choices(
            rewards,
            weights=[x[2] for x in rewards],
            k=1
        )[0]

        if value>0:
            con.execute(
                "UPDATE users SET balance=COALESCE(balance,0)+? WHERE id=?",
                (value,uid)
            )

            con.execute("""
                INSERT INTO transactions
                (user_id,type,amount,status,date,ref)
                VALUES(?,?,?,'approved',datetime('now'),?)
            """,(uid,"raffle",value,reward))

        elif reward=="Z1 Machine":
            con.execute("""
                INSERT INTO ai_machines(uid,name,status)
                VALUES(?,'Z1 Machine','RUNNING')
            """,(uid,))

        con.execute("""
            INSERT INTO raffle_records(user_id,reward,reward_value)
            VALUES(?,?,?)
        """,(uid,reward,value))

        remaining=con.execute("""
            SELECT COALESCE(SUM(tickets),0)
            FROM raffle_tickets
            WHERE CAST(user_id AS INTEGER)=?
            AND tickets>0
        """,(uid,)).fetchone()[0] or 0

        con.commit()

        return {
            "ok":True,
            "reward":reward,
            "value":value,
            "chances":int(remaining)
        }

    except Exception as e:
        con.rollback()
        print("RAFFLE ERROR:",e)
        return {"ok":False,"message":"Raffle error. Please try again."},500

    finally:
        con.close()

@app.route("/reward", methods=["GET","POST"])
def reward_page():
    if "uid" not in session:
        return redirect("/login")

    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS reward_redemptions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            code TEXT NOT NULL,
            value INTEGER NOT NULL,
            redeemed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(uid,code)
        )
    """)
    con.commit()

    try:
        used = con.execute(
            "SELECT code,value,redeemed_at FROM reward_redemptions WHERE uid=? ORDER BY id DESC",
            (session["uid"],)
        ).fetchall()
    except Exception:
        used = []

    con.close()

    history_html = ""

    for row in used:
        code = row[0]
        value = row[1]
        date = row[2] or ""

        try:
            value_text = "{:,.0f}".format(float(value))
        except Exception:
            value_text = str(value)

        history_html += """
        <div class="gift-history-row">
            <div>
                <div class="gift-code-name">{}</div>
                <div class="gift-date">{}</div>
            </div>
            <div class="gift-value">UGX {}</div>
        </div>
        """.format(code, date, value_text)

    if not history_html:
        history_html = '<div class="gift-empty-history">No gift codes yet.</div>'

    html = r"""
<style>
.gift-page,
.gift-page *{
    box-sizing:border-box!important;
}

.gift-page{
    width:100%!important;
    max-width:720px!important;
    min-height:100vh!important;
    margin:0 auto!important;
    padding:0 28px 105px!important;
    background:
        radial-gradient(circle at 15px 15px,
        rgba(0,190,255,.17) 1px,
        transparent 1.8px)!important;
    background-size:27px 27px!important;
    background-color:#000!important;
    color:#fff!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:16px!important;
    line-height:1.35!important;
    overflow-x:hidden!important;
    -webkit-text-size-adjust:100%!important;
}

.gift-head{
    width:calc(100% + 56px)!important;
    height:88px!important;
    margin:0 -28px 0!important;
    padding:0!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    position:relative!important;
    background:#000!important;
    border-bottom:1px solid rgba(0,190,255,.38)!important;
}

.gift-title{
    margin:0!important;
    padding:0!important;
    color:#00bfff!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:27px!important;
    line-height:1!important;
    font-weight:bold!important;
    text-align:center!important;
    text-shadow:0 0 9px rgba(0,190,255,.35)!important;
}

.gift-back{
    position:absolute!important;
    left:28px!important;
    top:20px!important;
    width:64px!important;
    height:64px!important;
    min-width:64px!important;
    min-height:64px!important;
    padding:0!important;
    margin:0!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    border:1px solid #008fd0!important;
    border-radius:18px!important;
    background:#000!important;
    color:#00bfff!important;
    text-decoration:none!important;
    font-family:Arial,sans-serif!important;
    font-size:43px!important;
    font-weight:300!important;
    line-height:1!important;
    box-shadow:0 0 9px rgba(0,190,255,.18)!important;
}

.gift-card{
    width:100%!important;
    margin:0 0 28px!important;
    padding:27px!important;
    border:1px solid rgba(0,180,240,.62)!important;
    border-radius:23px!important;
    background:
        radial-gradient(circle,
        rgba(0,175,240,.13) 1px,
        transparent 1.65px)!important;
    background-size:27px 27px!important;
    background-color:rgba(0,4,8,.96)!important;
    color:#fff!important;
    box-shadow:0 0 10px rgba(0,175,240,.07)!important;
}

.gift-progress{
    min-height:215px!important;
    padding:25px 28px 27px!important;
}

.gift-progress-top{
    display:flex!important;
    align-items:flex-end!important;
    justify-content:space-between!important;
    margin:0 0 23px!important;
}

.gift-count{
    color:#00bfff!important;
    font-size:47px!important;
    line-height:1!important;
    font-weight:bold!important;
    text-shadow:0 0 10px rgba(0,195,255,.42)!important;
}

.gift-count-total{
    color:#d5d9de!important;
    font-size:21px!important;
    margin-left:4px!important;
}

.gift-month{
    color:#aeb4bb!important;
    font-size:18px!important;
    line-height:1!important;
}

.gift-progress-line{
    width:100%!important;
    height:13px!important;
    border-radius:10px!important;
    background:#06101a!important;
    border:1px solid rgba(0,155,210,.14)!important;
    overflow:hidden!important;
    margin:0 0 23px!important;
}

.gift-progress-fill{
    width:0%!important;
    height:100%!important;
    background:linear-gradient(90deg,#00bfff,#08c9ff)!important;
    border-radius:10px!important;
}

.gift-progress-text{
    margin:0!important;
    color:#c4c7cc!important;
    font-size:18px!important;
    line-height:1.55!important;
}

.gift-progress-text strong{
    color:#00bfff!important;
}

.gift-redeem{
    padding:27px!important;
    min-height:405px!important;
}

.gift-section-title{
    display:flex!important;
    align-items:center!important;
    gap:13px!important;
    margin:0 0 25px!important;
    padding:0!important;
    color:#fff!important;
    font-size:27px!important;
    line-height:1.2!important;
    font-weight:bold!important;
}

.gift-ticket{
    color:#00bfff!important;
    font-size:28px!important;
    line-height:1!important;
}

.gift-input{
    width:100%!important;
    height:84px!important;
    min-height:84px!important;
    padding:0 23px!important;
    margin:0!important;
    border:2px solid #dfe1e5!important;
    border-radius:22px!important;
    outline:none!important;
    background:#070e17!important;
    color:#fff!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:22px!important;
    line-height:1!important;
}

.gift-input::placeholder{
    color:#777d85!important;
    opacity:1!important;
}

.gift-claim{
    width:100%!important;
    height:78px!important;
    min-height:78px!important;
    padding:0!important;
    margin:18px 0 0!important;
    border:0!important;
    border-radius:22px!important;
    background:linear-gradient(
        135deg,
        #08b8ee,
        #08c7f5 55%,
        #12b9ed
    )!important;
    color:#fff!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:24px!important;
    line-height:1!important;
    font-weight:bold!important;
    box-shadow:0 0 14px rgba(0,190,255,.20)!important;
}

.gift-description{
    margin:20px 0 0!important;
    padding:0!important;
    color:#c2c5ca!important;
    font-size:18px!important;
    line-height:1.55!important;
}

.gift-history{
    min-height:150px!important;
    padding:27px!important;
}

.gift-history-title{
    margin:0 0 23px!important;
    padding:0!important;
    color:#fff!important;
    font-size:27px!important;
    line-height:1.2!important;
    font-weight:bold!important;
}

.gift-empty-history{
    color:#c3c6ca!important;
    font-size:21px!important;
    line-height:1.4!important;
}

.gift-history-row{
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:15px!important;
    padding:15px 0!important;
    border-bottom:1px solid rgba(0,180,240,.18)!important;
}

.gift-code-name{
    color:#fff!important;
    font-size:19px!important;
    font-weight:bold!important;
}

.gift-date{
    color:#858b92!important;
    font-size:14px!important;
    margin-top:4px!important;
}

.gift-value{
    color:#00bfff!important;
    font-size:18px!important;
    font-weight:bold!important;
}

@media(max-width:500px){
    .gift-page{
        padding-left:28px!important;
        padding-right:28px!important;
    }

    .gift-head{
        width:calc(100% + 56px)!important;
        margin-left:-28px!important;
        margin-right:-28px!important;
    }

    .gift-card{
        padding:27px!important;
    }

    .gift-progress{
        padding:25px 28px 27px!important;
    }

    .gift-count{
        font-size:47px!important;
    }

    .gift-title{
        font-size:27px!important;
    }

    .gift-section-title,
    .gift-history-title{
        font-size:27px!important;
    }

    .gift-input{
        height:84px!important;
        font-size:22px!important;
    }

    .gift-claim{
        height:78px!important;
        font-size:24px!important;
    }
}
</style>




<style id="gift-final-match">

.gift-page{
    width:100%!important;
    max-width:none!important;
    min-height:100vh!important;
    margin:0!important;
    padding:0 28px 150px!important;
    box-sizing:border-box!important;
    background-color:#000!important;
    background-image:radial-gradient(
        circle,
        rgba(0,120,170,.24) 1px,
        transparent 1.6px
    )!important;
    background-size:34px 34px!important;
    color:#fff!important;
    font-family:Georgia,"Times New Roman",serif!important;
}

/* HEADER */

.gift-head{
    width:calc(100% + 56px)!important;
    height:105px!important;
    margin-left:-28px!important;
    margin-right:-28px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    position:relative!important;
    background:#000!important;
    border-bottom:1px solid rgba(0,150,200,.55)!important;
}

.gift-back{
    position:absolute!important;
    left:28px!important;
    top:20px!important;
    width:64px!important;
    height:64px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    box-sizing:border-box!important;
    border:1px solid #008fc5!important;
    border-radius:17px!important;
    background:#01070c!important;
    color:#00b9f3!important;
    font-family:Arial,sans-serif!important;
    font-size:43px!important;
    font-weight:300!important;
    line-height:1!important;
    text-decoration:none!important;
    box-shadow:0 0 8px rgba(0,174,235,.18)!important;
}

.gift-title{
    margin:0!important;
    padding:0!important;
    color:#00b9f3!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:27px!important;
    font-weight:bold!important;
    line-height:1!important;
}

/* CARDS */

.gift-card{
    position:relative!important;
    width:100%!important;
    box-sizing:border-box!important;
    background:rgba(0,3,8,.93)!important;
    border:1px solid #008fc5!important;
    border-radius:24px!important;
    box-shadow:0 0 8px rgba(0,145,200,.18)!important;
    overflow:hidden!important;
}

.gift-card:before{
    content:""!important;
    position:absolute!important;
    inset:0!important;
    pointer-events:none!important;
    background-image:radial-gradient(
        circle,
        rgba(0,120,165,.25) 1px,
        transparent 1.6px
    )!important;
    background-size:34px 34px!important;
    opacity:.42!important;
}

.gift-card>*{
    position:relative!important;
    z-index:2!important;
}

/* FIRST CARD */

.gift-progress{
    height:216px!important;
    margin-top:0!important;
    padding:24px 28px 20px!important;
}

.gift-progress-top{
    width:100%!important;
    height:47px!important;
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
}

.gift-count{
    color:#00b9f3!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:47px!important;
    font-weight:bold!important;
    line-height:.9!important;
}

.gift-count-total{
    color:#dedee3!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:21px!important;
    font-weight:bold!important;
}

.gift-month{
    color:#999ba2!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:17px!important;
    line-height:1!important;
}

.gift-progress-line{
    width:100%!important;
    height:13px!important;
    margin-top:15px!important;
    border-radius:8px!important;
    background:#07131b!important;
    overflow:hidden!important;
    box-shadow:inset 0 1px 5px rgba(0,0,0,.8)!important;
}

.gift-progress-fill{
    width:0%!important;
    height:100%!important;
    background:#00b9f3!important;
    border-radius:8px!important;
}

.gift-progress-text{
    margin:19px 0 0!important;
    padding:0!important;
    color:#9fa0a7!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:18px!important;
    line-height:1.62!important;
    text-align:left!important;
}

.gift-progress-text strong{
    color:#00b9f3!important;
}

/* SECOND CARD */

.gift-redeem{
    min-height:403px!important;
    margin-top:27px!important;
    padding:32px 28px 28px!important;
}

.gift-section-title{
    width:100%!important;
    display:flex!important;
    align-items:center!important;
    gap:12px!important;
    margin:0 0 26px!important;
    padding:0!important;
    color:#f1f1f3!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:27px!important;
    font-weight:bold!important;
    line-height:1.1!important;
}

.gift-ticket{
    color:#00b9f3!important;
    font-family:Arial,sans-serif!important;
    font-size:28px!important;
    line-height:1!important;
}

.gift-input{
    display:block!important;
    width:100%!important;
    height:84px!important;
    box-sizing:border-box!important;
    margin:0!important;
    padding:0 24px!important;
    border:2px solid #eeeeee!important;
    border-radius:28px!important;
    outline:none!important;
    background:#080f16!important;
    color:#fff!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:22px!important;
}

.gift-input::placeholder{
    color:#8f9097!important;
    opacity:1!important;
}

.gift-claim{
    display:block!important;
    width:100%!important;
    height:78px!important;
    box-sizing:border-box!important;
    margin:19px 0 0!important;
    padding:0!important;
    border:0!important;
    border-radius:28px!important;
    background:#09b9ed!important;
    color:#fff!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:26px!important;
    font-weight:bold!important;
    line-height:78px!important;
    text-align:center!important;
}

.gift-description{
    margin:19px 0 0!important;
    padding:0!important;
    color:#a1a2a8!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:18px!important;
    line-height:1.66!important;
}

/* HISTORY */

.gift-history{
    min-height:151px!important;
    margin-top:27px!important;
    padding:34px 28px 26px!important;
}

.gift-history-title{
    margin:0!important;
    padding:0!important;
    color:#f1f1f3!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:27px!important;
    font-weight:bold!important;
    line-height:1!important;
}

.gift-empty-history{
    margin-top:25px!important;
    color:#b0b0b6!important;
    font-family:Georgia,"Times New Roman",serif!important;
    font-size:22px!important;
}

@media(max-width:390px){
    .gift-page{
        padding-left:18px!important;
        padding-right:18px!important;
    }

    .gift-head{
        margin-left:-18px!important;
        margin-right:-18px!important;
    }

    .gift-back{
        left:18px!important;
    }

    .gift-progress,
    .gift-redeem,
    .gift-history{
        padding-left:20px!important;
        padding-right:20px!important;
    }
}

</style>

<div class="gift-page">

    <div class="gift-head">
        <a class="gift-back" href="/my">‹</a>
        <div class="gift-title">Gift code</div>
    </div>

    <div class="gift-card gift-progress">

        <div class="gift-progress-top">
            <div>
                <span class="gift-count">0</span>
                <span class="gift-count-total">/ 6</span>
            </div>
            <div class="gift-month">2026-09</div>
        </div>

        <div class="gift-progress-line">
            <div class="gift-progress-fill"></div>
        </div>

        <p class="gift-progress-text">
            Invite <strong>6</strong> more members who activate a machine this month
            to earn a gift code from the manager.
        </p>

    </div>

    <div class="gift-card gift-redeem">

        <div class="gift-section-title">
            <span class="gift-ticket">🎟</span>
            <span>Redeem a gift code</span>
        </div>

        <input
            class="gift-input"
            id="code"
            type="text"
            placeholder="Enter gift code"
            autocomplete="off"
        >

        <button
            class="gift-claim"
            type="button"
            onclick="checkGiftCode()"
        >
            Claim extra cash
        </button>

        <p class="gift-description">
            Gift codes are issued by the manager once your monthly invite milestone
            is reached. Each code can be redeemed only once and pays straight into
            your withdrawable balance.
        </p>

    </div>

    <div class="gift-card gift-history">

        <div class="gift-history-title">Gift history</div>

        __GIFT_HISTORY__

    </div>

</div>

<script>
async function checkGiftCode(){
    const input = document.getElementById("code");
    const code = input.value.trim().toUpperCase();

    if(!code){
        alert("Please enter the gift code");
        input.focus();
        return;
    }

    try{
        const r = await fetch("/reward/redeem",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({code:code})
        });

        const d = await r.json();

        alert(d.message);

        if(
            d.message &&
            d.message.toLowerCase().includes("accepted")
        ){
            input.value = "";
            location.reload();
        }

    }catch(e){
        alert("Unable to process the gift code right now.");
    }
}
</script>
"""

    html = html.replace("__GIFT_HISTORY__", history_html)

    return S + html




@app.route("/reward/redeem", methods=["POST"])
def redeem_reward():
    if "uid" not in session:
        return {"message":"Please log in first."},401

    data=request.get_json(silent=True) or {}
    code=str(data.get("code","")).strip().upper()

    rewards={
        "HFCS":40000,
        "CODEX20":20000,
        "WELCOME10":10000,
        "BONUS5":5000,
        "VIP50":50000
    }

    if code not in rewards:
        return {"message":"Invalid reward code."}

    con=sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS reward_redemptions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER NOT NULL,
            code TEXT NOT NULL,
            value INTEGER NOT NULL,
            redeemed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(uid,code)
        )
    """)

    try:
        con.execute(
            "INSERT INTO reward_redemptions(uid,code,value) VALUES(?,?,?)",
            (session["uid"],code,rewards[code])
        )
        con.commit()
        msg=f"Reward code accepted: {rewards[code]:,} promotional points."
    except sqlite3.IntegrityError:
        msg="You have already used this reward code."

    con.close()
    return {"message":msg}

@app.route("/support")
def support_page():
    if "uid" not in session:
        return redirect("/login")
    return S+"""<style>
body{background:#000;color:#fff;font-family:Georgia,serif}
.page{min-height:100vh;padding:20px 15px 100px;box-sizing:border-box}
.head{display:flex;align-items:center;gap:15px;margin-bottom:25px}
.back{color:#00baff;text-decoration:none;font-size:35px}
.title{color:#00baff;font-size:26px;font-weight:bold}
.card{background:#02080d;border:1px solid #078cff;border-radius:22px;padding:20px;margin-bottom:18px}
.manager{display:flex;align-items:center;gap:15px}
.avatar{width:58px;height:58px;border:2px solid #00baff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:27px}
.name{color:#00baff;font-weight:bold}
.status{color:#aaa;font-size:13px;margin-top:5px}
.message{margin-top:20px;padding:16px;border-radius:18px;background:#071522;border:1px solid #078cff;line-height:1.5}
.btn{display:block;text-align:center;padding:15px;border:1px solid #078cff;border-radius:14px;color:#00baff;text-decoration:none;margin-top:15px}
</style>
<div class="page">
<div class="head"><a class="back" href="/my">‹</a><div class="title">Support Center</div></div>
<div class="card manager">
<div class="avatar">♧</div>
<div><div class="name">CODEX700 SUPPORT</div><div class="status">● Support Center</div></div>
</div>
<div class="card">
<div class="message"><b style="color:#00baff">CODEX700 SUPPORT</b><br><br>Welcome to the CODEX700 Support Center. How can we help you today?</div>
<a class="btn" href="/home">Open Support</a>
<a class="btn" href="/my">Back to My Account</a>
</div>
</div>"""


@app.route("/withdraw", methods=["GET", "POST"])
def withdraw_page():
    if "uid" not in session:
        return redirect("/login")

    c = db()
    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (session["uid"],)
    ).fetchone()

    balance = float(u["balance"] or 0) if u and "balance" in u.keys() else 0

    # Check whether the user owns an active AI machine.
    try:
        active_machine = c.execute(
            "SELECT COUNT(*) FROM investments WHERE user_id=? AND active=1",
            (session["uid"],)
        ).fetchone()[0] > 0
    except Exception:
        active_machine = False

    # Withdrawal history.
    try:
        history = c.execute(
            """SELECT * FROM transactions
               WHERE user_id=?
               AND LOWER(COALESCE(type,'')) IN ('withdraw','withdrawal')
               ORDER BY id DESC LIMIT 20""",
            (session["uid"],)
        ).fetchall()
    except Exception:
        history = []

    c.close()

    history_html = ""
    for x in history:
        keys = x.keys()
        amount = x["amount"] if "amount" in keys else 0
        status = x["status"] if "status" in keys else "Pending"
        date = x["date"] if "date" in keys else ""

        try:
            amount_text = "{:,.2f}".format(float(amount))
        except Exception:
            amount_text = str(amount)

        history_html += f"""
        <div class="history-row">
            <div>
                <b>Withdrawal</b>
                <small>{date}</small>
            </div>
            <div class="history-right">
                <b>UGX {amount_text}</b>
                <span class="status">{status}</span>
            </div>
        </div>
        """

    if not history_html:
        history_html = """
        <div class="empty-history">
            <div class="empty-icon">▣</div>
            <div>No withdrawal history available.</div>
            <button type="button" onclick="location.reload()">Refresh</button>
        </div>
        """

    if not active_machine:
        machine_html = """
        <div class="machine-warning">
            <h3>Active AI machine required</h3>
            <p>You must own at least one active AI machine before you can withdraw.</p>
            <a href="/invest">Buy an AI machine</a>
        </div>
        """
        button_disabled = "disabled"
    else:
        machine_html = ""
        button_disabled = ""

    html = f"""
<style>
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;background:#000;color:#fff}}
body{{font-family:Georgia,serif}}

.withdraw-page{{
    min-height:100vh;
    padding:0 14px 105px;
    background:
      radial-gradient(circle at 50% 25%,rgba(0,174,255,.08),transparent 35%),
      #000;
    color:#fff;
    overflow-x:hidden;
}}

.withdraw-head{{
    height:88px;
    margin:0 -14px 28px;
    display:flex;
    align-items:center;
    justify-content:center;
    position:relative;
    border-bottom:1px solid rgba(0,186,255,.45);
    background:#000;
}}

.withdraw-title{{
    color:#00c8ff;
    font-size:27px;
    font-weight:bold;
    text-shadow:0 0 12px rgba(0,190,255,.55);
}}

.back-btn{{
    position:absolute;
    left:28px;
    top:15px;
    width:62px;
    height:62px;
    display:flex;
    align-items:center;
    justify-content:center;
    border:1px solid #00baff;
    border-radius:18px;
    color:#00baff;
    text-decoration:none;
    font-size:43px;
    line-height:1;
    box-shadow:0 0 14px rgba(0,186,255,.18);
}}

.withdraw-card{{
    position:relative;
    background:
      radial-gradient(circle,rgba(0,180,255,.12) 1px,transparent 1.5px),
      rgba(0,5,9,.92);
    background-size:26px 26px;
    border:1px solid rgba(0,186,255,.65);
    border-radius:23px;
    padding:27px;
    margin-bottom:28px;
    box-shadow:
      0 0 12px rgba(0,174,255,.08),
      inset 0 0 22px rgba(0,174,255,.025);
}}

.balance-card{{
    text-align:center;
    padding:30px 20px 34px;
}}

.balance-label{{
    color:#aeb4bd;
    font-size:24px;
    margin-bottom:8px;
}}

.balance-value{{
    color:#00c8ff;
    font-size:47px;
    font-weight:bold;
    text-shadow:0 0 12px rgba(0,200,255,.45);
}}

.section-title{{
    font-size:24px;
    margin:4px 0 24px;
}}

.methods{{
    display:grid;
    grid-template-columns:1fr 1fr 1fr;
    gap:14px;
    margin-bottom:24px;
}}

.method{{
    min-height:60px;
    border:1px solid #008fd0;
    border-radius:18px;
    background:#02070b;
    color:#fff;
    font-family:Georgia,serif;
    font-size:18px;
    cursor:pointer;
}}

.method.active{{
    background:linear-gradient(180deg,#19c8ff,#00a9df);
    color:#fff;
    border-color:#19c8ff;
    box-shadow:0 0 14px rgba(0,190,255,.3);
}}

.field-label{{
    display:block;
    font-size:22px;
    margin:18px 0 10px;
}}

.input{{
    width:100%;
    height:78px;
    padding:0 21px;
    border:1px solid #087cae;
    border-radius:18px;
    outline:none;
    background:#050b11;
    color:#fff;
    font-size:22px;
    font-family:Georgia,serif;
}}

.input::placeholder{{color:#717780}}

.hint{{
    color:#aeb4bd;
    font-size:17px;
    margin-top:9px;
}}

.required{{
    margin:25px 0;
    padding:23px;
    border:1px solid #8d1220;
    border-radius:18px;
    background:rgba(70,0,8,.34);
}}

.required h3{{
    margin:0 0 9px;
    font-size:22px;
    font-weight:normal;
}}

.required p{{
    margin:0 0 10px;
    color:#c5c7ca;
    font-size:17px;
    line-height:1.5;
}}

.required a,.machine-warning a{{
    color:#00c8ff;
    text-decoration:none;
    font-size:18px;
}}

.summary{{
    margin-top:25px;
    padding:22px;
    border:1px solid #087cae;
    border-radius:18px;
}}

.summary-row{{
    display:flex;
    justify-content:space-between;
    gap:15px;
    margin-bottom:14px;
    font-size:21px;
}}

.summary-row:last-child{{margin-bottom:0}}

.summary-row .value{{text-align:right}}
.fee{{color:#ff2945}}
.receive{{font-weight:bold;font-size:23px}}
.receive .value{{color:#00c8ff}}

.summary-note{{
    margin-top:20px;
    color:#b8bcc2;
    line-height:1.55;
    font-size:17px;
}}

.machine-warning{{
    margin-top:22px;
    padding:23px;
    border:1px solid #8d1220;
    border-radius:18px;
    background:rgba(70,0,8,.34);
}}

.machine-warning h3{{
    margin:0 0 8px;
    font-size:22px;
    font-weight:normal;
}}

.machine-warning p{{
    color:#c5c7ca;
    line-height:1.5;
    font-size:17px;
}}

.request-btn{{
    width:100%;
    height:78px;
    margin-top:22px;
    border:0;
    border-radius:18px;
    background:linear-gradient(180deg,#11c8ff,#009bd0);
    color:#fff;
    font-family:Georgia,serif;
    font-size:23px;
    font-weight:bold;
    box-shadow:0 0 18px rgba(0,190,255,.28);
}}

.request-btn:disabled{{
    opacity:.58;
    cursor:not-allowed;
}}

.history-title{{
    font-size:27px;
    margin:0 0 25px;
}}

.tabs{{
    display:flex;
    gap:10px;
    overflow-x:auto;
    padding-bottom:3px;
    scrollbar-width:none;
}}

.tabs::-webkit-scrollbar{{display:none}}

.tab{{
    flex:0 0 auto;
    padding:14px 21px;
    border-radius:25px;
    background:#050b12;
    color:#bfc4ca;
    border:0;
    font-family:Georgia,serif;
    font-size:17px;
}}

.tab.active{{
    background:#0bc4f7;
    color:#fff;
    box-shadow:0 0 13px rgba(0,190,255,.22);
}}

.history-box{{
    margin-top:25px;
    padding:28px 18px;
    min-height:380px;
    border:1px solid rgba(0,186,255,.45);
    border-radius:23px;
    background:
      radial-gradient(circle,rgba(0,180,255,.10) 1px,transparent 1.5px),
      #000;
    background-size:26px 26px;
}}

.history-row{{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:17px 4px;
    border-bottom:1px solid rgba(0,186,255,.18);
}}

.history-row small{{
    display:block;
    color:#888;
    margin-top:5px;
}}

.history-right{{text-align:right}}
.history-right .status{{display:block;color:#00c8ff;margin-top:5px}}

.empty-history{{
    min-height:320px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    text-align:center;
    color:#b9bec5;
    font-size:19px;
}}

.empty-icon{{
    width:78px;
    height:78px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:#07101a;
    color:#d6dce2;
    font-size:37px;
    margin-bottom:25px;
}}

.empty-history button{{
    margin-top:25px;
    border:0;
    border-radius:30px;
    padding:15px 29px;
    background:#08baf0;
    color:#fff;
    font-family:Georgia,serif;
    font-size:18px;
}}

@media(max-width:430px){{
    .withdraw-page{{padding-left:14px;padding-right:14px}}
    .withdraw-card{{padding:25px 27px}}
    .methods{{gap:10px}}
    .method{{font-size:16px;padding:0 4px}}
    .balance-value{{font-size:43px}}
}}
</style>

<div class="withdraw-page">

<div class="withdraw-head">
    <a class="back-btn" href="/my">‹</a>
    <div class="withdraw-title">Withdraw</div>
</div>

<div class="withdraw-card balance-card">
    <div class="balance-label">Available balance</div>
    <div class="balance-value">UGX {balance:,.2f}</div>
</div>

<div class="withdraw-card">

    <div class="section-title">Payout method</div>

    <div class="methods">
        <button type="button" class="method active" onclick="setMethod(this,'MTN UG')">MTN UG</button>
        <button type="button" class="method" onclick="setMethod(this,'Airtel UG')">Airtel UG</button>
        <button type="button" class="method" onclick="setMethod(this,'USDT TRC20')">USDT TRC20</button>
    </div>

    <form method="POST" action="/withdraw" onsubmit="return validateWithdrawal()">

        <input type="hidden" name="method" id="method" value="MTN UG">

        <label class="field-label">Amount (UGX)</label>
        <input
            class="input"
            type="number"
            id="amount"
            name="amount"
            min="5000"
            step="1"
            placeholder="5000"
            value=""
            oninput="calculate()"
            required
        >

        <div class="hint">Minimum withdrawal is 5,000 UGX</div>

        <div class="required">
            <h3>Withdrawal details required</h3>
            <p>Save your phone number and the name registered on that number on your card before withdrawing.</p>
            <a href="/account">Save my card details</a>
        </div>

        <label class="field-label">Destination phone number</label>
        <input
            class="input"
            type="text"
            value="Saved on your card"
            readonly
        >
        <div class="hint">Taken from your saved card. Change it on the Card page.</div>

        <div class="summary">
            <div class="summary-row">
                <span>Amount (UGX)</span>
                <span class="value" id="gross">0.00</span>
            </div>

            <div class="summary-row">
                <span>Withdrawal fee (10%)</span>
                <span class="value fee" id="fee">-0.00</span>
            </div>

            <div class="summary-row receive">
                <span>You receive</span>
                <span class="value" id="receive">0.00</span>
            </div>

            <div class="summary-note">
                The full amount is deducted from your balance as soon as you request.<br><br>
                You must have at least one active AI machine to withdraw.
            </div>
        </div>

        {machine_html}

        <button class="request-btn" type="submit" {button_disabled}>
            Request withdrawal
        </button>

    </form>
</div>

<div class="history-title">Transaction history</div>

<div class="tabs">
    <button class="tab">All</button>
    <button class="tab">Deposit</button>
    <button class="tab active">Withdraw</button>
    <button class="tab">Earnings</button>
    <button class="tab">Commission</button>
</div>

<div class="history-box">
    {history_html}
</div>

</div>

<script>
function setMethod(btn,name){{
    document.querySelectorAll('.method').forEach(function(x){{
        x.classList.remove('active');
    }});
    btn.classList.add('active');
    document.getElementById('method').value=name;
}}

function calculate(){{
    var amount=parseFloat(document.getElementById('amount').value)||0;
    var fee=amount*0.10;
    var receive=amount-fee;

    document.getElementById('gross').textContent=
        amount.toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}});

    document.getElementById('fee').textContent='-'+
        fee.toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}});

    document.getElementById('receive').textContent=
        receive.toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}});
}}

function validateWithdrawal(){{
    var amount=parseFloat(document.getElementById('amount').value)||0;

    if(amount < 5000){{
        alert('Minimum withdrawal is 5,000 UGX.');
        return false;
    }}

    if(amount > {balance}){{
        alert('Insufficient balance.');
        return false;
    }}

    return true;
}}

calculate();
</script>
"""

    return S + html
