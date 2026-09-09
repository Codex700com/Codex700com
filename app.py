import sqlite3, pathlib, os, random
from manager_code import setup as setup_manager
from flask import Flask, request, redirect, session, g

app=Flask(__name__)
app.secret_key="codex700_secret_2024"

DB="codex700.db"

def db():
 conn=sqlite3.connect(DB)
 conn.row_factory=sqlite3.Row
 return conn

# Create tables if not exist
def init_db():
 c=db()
 c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, password TEXT, invite_code TEXT, balance REAL DEFAULT 0)")
 c.execute("CREATE TABLE IF NOT EXISTS reset_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, name TEXT, message TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
 c.commit()
 c.close()
init_db()

S='''
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
    try:
     c.execute("INSERT INTO users (phone,password,invite_code) VALUES (?,?,?)",(phone,pw,invite))
    except:
     c.execute("INSERT INTO users (phone,password) VALUES (?,?)",(phone,pw))
    c.commit()
    c.close()
    return S+'<div style="position:relative;z-index:2;min-height:100vh;display:flex;align-items:center;justify-content:center"><div style="background:rgba(0,0,0,0.7);border:1px solid #0a84ff;border-radius:16px;padding:30px;text-align:center"><p style="color:#4ade80">Registration Successful!</p><script>setTimeout(function(){location.href="/login"},100)</script></div></div>'
 colors=["#3b82f6","#f59e0b","#10b981","#a855f7","#ec4899"]
 col_html="".join(['<span style="color:'+random.choice(colors)+';font-weight:900;margin:1px">'+ch+'</span>' for ch in captcha])
 html='<style>.reg-wrap{position:relative;z-index:2;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding-top:10vh;padding-left:18px;padding-right:18px}.welcome{font-size:34px;font-weight:800;color:#fff;margin-bottom:22px}.pill{width:100%;max-width:360px;height:52px;background:rgba(0,0,0,0.55);border:1px solid #555;border-radius:26px;display:flex;align-items:center;padding:0 16px;margin:9px 0;position:relative}.pill input{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:15px;margin-left:10px}.captcha-box{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:#fff;border-radius:8px;padding:6px 14px;font-size:22px;letter-spacing:3px;font-weight:800}.reg-btn{width:100%;max-width:360px;height:50px;background:transparent;border:1.6px solid #0a84ff;border-radius:26px;color:#0a84ff;font-size:19px;font-weight:600;margin-top:18px;cursor:pointer}.err{color:#ff6b6b;font-size:13px;max-width:360px;text-align:center;margin:6px;background:rgba(255,0,0,0.08);padding:8px;border-radius:8px}html{scroll-behavior:auto!important;}body{overflow-x:hidden;touch-action:pan-y;-webkit-overflow-scrolling:touch;}</style><div class="reg-wrap"><div class="welcome">Welcome</div><div class="err">'+m+'</div><form method="POST" style="width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center"><input type="hidden" name="real_captcha" value="'+captcha+'"><div class="pill"><input name="phone" placeholder="Phone Number" required></div><div class="pill"><input name="password" type="password" placeholder="Set Password" required></div><div class="pill"><input name="confirm" type="password" placeholder="Confirm Password" required></div><div class="pill"><input name="captcha_input" placeholder="Verification Code" required><div class="captcha-box">'+col_html+'</div></div><div class="pill"><input name="invite" placeholder="Invitation Code"></div><button class="reg-btn">Register</button><div style="margin-top:14px"><a href="/login" style="color:#aaa;text-decoration:none">‹ Login</a></div></form></div>'
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
 html='<style>.login-wrap{position:relative;z-index:2;min-height:100vh;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;padding:10vh 18px 30px;overflow:hidden;background:#020609}.welcome{font-family:Georgia,serif;font-size:45px;font-weight:500;color:#fff;margin-bottom:30px;}.login-wrap .err{color:#ff6b6b;font-size:13px;width:100%;max-width:370px;min-height:18px;text-align:center;margin:0 0 5px}.login-form{width:100%;max-width:370px;display:flex;flex-direction:column;align-items:center}.login-pill{width:100%;height:58px;box-sizing:border-box;background:rgba(0,0,0,.70);border:1px solid rgba(255,255,255,.28);border-radius:30px;display:flex;align-items:center;padding:0 18px;margin:9px 0;}.login-pill:focus-within{border-color:#00aaff;}.login-pill input{flex:1;width:100%;background:transparent;border:none;outline:none;color:#fff;font-size:15px;margin-left:5px}.login-pill input::placeholder{color:#929292}.eye{color:#999;font-size:17px;cursor:pointer;padding:8px}.lang{width:100%;display:flex;justify-content:flex-end;margin:3px 0 7px}.lang select{background:transparent;border:0;outline:0;color:#999;font-size:13px}.lang option{background:#050b12;color:#fff}.login-btn{width:100%;height:54px;background:transparent;border:1.6px solid #078cff;border-radius:28px;color:#078cff;font-size:18px;font-weight:600;margin-top:19px;cursor:pointer;}.login-btn:active{transform:scale(.98);background:rgba(0,140,255,.08)}.bot{width:100%;display:flex;justify-content:space-between;margin-top:18px;font-size:13px}.bot a{color:#aaa;text-decoration:none}.bot a:first-child{color:#078cff}@media(max-width:430px){.login-wrap{padding-top:9vh}.welcome{font-size:43px}}html{scroll-behavior:auto!important;}body{overflow-x:hidden;touch-action:pan-y;-webkit-overflow-scrolling:touch;}</style><div class="login-wrap"><div class="welcome">Welcome</div><div class="err">'+m+'</div><form method="POST" class="login-form"><div class="login-pill"><input name="phone" placeholder="Phone Number" required></div><div class="login-pill"><input id="loginPassword" name="password" type="password" placeholder="Login Password" required><span class="eye" onclick="togglePassword()">◉</span></div><div class="lang"><select><option>English</option></select></div><button class="login-btn" type="submit">Login</button><div class="bot"><a href="/register">‹ &nbsp;Register</a><a href="/reset">Forgot your password?</a></div></form></div><script>function togglePassword(){var p=document.getElementById("loginPassword");p.type=p.type==="password"?"text":"password";}</script>'
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
  <a class="msg-link" href="/messages">
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
 <a class="nav-item active" href="/home"><span class="nav-icon">⌂</span>Home</a>
 <a class="nav-item" href="/raffle"><span class="nav-icon">▣</span>Raffle</a>
 <a class="nav-item" href="/messages"><span class="nav-icon">▤</span>Chats</a>
 <a class="nav-item" href="/invest"><span class="nav-icon">▦</span>AI</a>
 <a class="nav-item" href="/income"><span class="nav-icon">₿</span>Income</a>
 <a class="nav-item" href="/my"><span class="nav-icon">♙</span>My</a>

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

@app.route("/my")
def my_page():
 if "uid" not in session:
  return redirect("/login")

 c=db()
 u=c.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone()
 c.close()

 phone = u["phone"] if u else ""
 balance = u["balance"] if u and "balance" in u.keys() else 0

 return S+"""<style>
.my-page{min-height:100vh;background:#000;color:#fff;padding:20px 14px 105px;box-sizing:border-box;font-family:Georgia,serif}
.my-top{display:flex;justify-content:space-between;align-items:flex-start;margin:5px 8px 28px}
.my-welcome{color:#00baff;font-size:27px}
.my-phone{font-size:18px;margin-top:13px}
.vip{text-align:center}
.vip-circle{width:72px;height:72px;border:3px solid #08baff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:34px}
.vip-label{margin-top:8px;border:1px solid #08baff;border-radius:20px;padding:6px 18px;color:#00baff;font-size:13px}

.wallet-details{
 display:grid;
 grid-template-columns:1fr 1fr;
 max-height:0;
 overflow:hidden;
 opacity:0;
 transition:max-height:.4s ease,opacity:.3s ease,margin-top:.3s ease;
}
.wallet.open .wallet-details{
 max-height:260px;
 opacity:1;
 margin-top:24px;
}
.wallet-detail{
 text-align:center;
 padding:8px 4px;
}
.wallet-detail-title{
 color:#aaa;
 font-size:17px;
 margin-bottom:10px;
}
.wallet-detail-value{
 color:#fff;
 font-size:20px;
 font-weight:bold;
}
.wallet-arrow{
 grid-column:1/3;
 color:#00baff;
 font-size:36px;
 line-height:30px;
 margin-top:14px;
 cursor:pointer;
 text-align:center;
 user-select:none;
}
.wallet{border:1px solid #078cff;border-radius:25px;padding:32px 12px;margin-bottom:28px;background:#02080d;display:grid;grid-template-columns:1fr 1fr;text-align:center}
.wallet-title{color:#aaa;font-size:22px;margin-bottom:15px}
.wallet-value{font-size:32px;font-weight:bold}
.down{grid-column:1/3;color:#00baff;font-size:36px;margin-top:15px}
.services{border:1px solid #078cff;border-radius:24px;padding:25px 8px;background:#02080d;display:grid;grid-template-columns:repeat(4,1fr);gap:25px 5px}
.service{text-align:center;color:#fff;text-decoration:none;font-size:14px}
.icon{width:56px;height:56px;margin:auto auto 8px;border-radius:17px;background:#08b9ee;display:flex;align-items:center;justify-content:center;font-size:27px}
.bottom{position:fixed;z-index:50;left:0;right:0;bottom:0;height:76px;background:#000;border-top:1px solid #123;display:grid;grid-template-columns:repeat(6,1fr)}
.bottom a{color:#fff;text-decoration:none;text-align:center;font-size:12px;padding-top:10px}
.bottom i{display:block;font-style:normal;font-size:27px}
.bottom .active{color:#00baff}
@media(max-width:380px){.my-page{padding-left:8px;padding-right:8px}.icon{width:52px;height:52px}.service{font-size:12px}}
</style>
<div class="my-page">
<div class="my-top">
<div>
<div class="my-welcome">Welcome to CODEX700</div>
<div class="my-phone">"""+str(phone)+"""</div>
</div>
<div class="vip">
<div class="vip-circle">✦</div>
<div class="vip-label">★ VIP 0</div>
</div>
</div>

<div class="wallet" id="walletBox">
<div><div class="wallet-title">Wallet</div><div class="wallet-value">0.00</div></div>
<div><div class="wallet-title">Balance</div><div class="wallet-value">"""+str(balance)+"""</div></div>

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

<div class="services">
<a class="service" href="/home"><div class="icon">▣</div>Deposit</a>
<a class="service" href="/withdraw"><div class="icon">♢</div>Withdraw</a>
<a class="service" href="/home"><div class="icon">▤</div>Card</a>
<a class="service" href="/home"><div class="icon">$</div>Bill</a>
<a class="service" href="/home"><div class="icon">♙</div>Invite</a>
<a class="service" href="/home"><div class="icon">♧</div>My team</a>
<a class="service" href="/home"><div class="icon">☆</div>VIP Task</a>
<a class="service" href="/reward"><div class="icon">🎁</div>Reward</a>
<a class="service" href="/home"><div class="icon">▱</div>Gift code</a>
<a class="service" href="/home"><div class="icon">◇</div>Raffle</a>
<a class="service" href="/home"><div class="icon">↓</div>Download App</a>
<a class="service" href="/manager"><div class="icon">♧</div>Manager</a>
<a class="service" href="/my"><div class="icon">⚙</div>Settings</a>
</div>
</div>

<div class="bottom">
<a href="/home"><i>⌂</i>Home</a>
<a href="/home"><i>▣</i>Raffle</a>
<a href="/home"><i>▤</i>Chats</a>
<a href="/home"><i>▦</i>AI</a>
<a href="/income"><i>₿</i>Income</a>
<a class="active" href="/my"><i>♙</i>My</a>
</div>"""

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
    page += 'body{margin:0;background:#000;color:#fff;font-family:Georgia,serif}'
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
    page += '<div class="nav"><a href="/home"><i>⌂</i>Home</a><a href="/home"><i>▣</i>Raffle</a><a href="/support"><i>▤</i>Chats</a><a href="/invest"><i>▦</i>AI</a><a class="active" href="/income"><i>₿</i>Income</a><a href="/my"><i>♙</i>My</a></div>'
    return page

if __name__=="__main__":
 app.run(host="0.0.0.0",port=5000,debug=False)

@app.route("/reward")
def reward_page():
    if "uid" not in session:
        return redirect("/login")
    return S+"""<style>
body{background:#000;color:#fff;font-family:Georgia,serif}
.page{min-height:100vh;padding:20px 15px 100px;box-sizing:border-box}
.head{display:flex;align-items:center;gap:15px;margin-bottom:25px}
.back{color:#00baff;text-decoration:none;font-size:35px}
.title{color:#00baff;font-size:26px;font-weight:bold}
.card{background:#02080d;border:1px solid #078cff;border-radius:22px;padding:25px 18px;text-align:center}
.icon{font-size:55px}
h2{color:#00baff}
p{color:#aaa;line-height:1.5}
input{width:100%;box-sizing:border-box;padding:16px;border-radius:14px;border:1px solid #078cff;background:#050d15;color:#fff;font-size:16px}
button{width:100%;margin-top:15px;padding:16px;border:0;border-radius:14px;background:#08b9ee;color:#fff;font-weight:bold;font-size:17px}
.cancel{display:block;margin-top:15px;color:#00baff;text-decoration:none}
</style>
<div class="page">
<div class="head"><a class="back" href="/my">‹</a><div class="title">Reward Center</div></div>
<div class="card">
<div class="icon">🎁</div>
<h2>Enter Reward Code</h2>
<p>Please enter the reward code provided by CODEX700.</p>
<input id="code" placeholder="Enter code">
<button onclick="checkCode()">Confirm</button>
<a class="cancel" href="/my">Cancel</a>
</div>
</div>
<script>
function checkCode(){
 let c=document.getElementById("code").value.trim();
 alert(c ? "Reward code submitted." : "Please enter the reward code");
}
</script>"""


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


@app.route("/withdraw")
def withdraw_page():
    if "uid" not in session:
        return redirect("/login")
    c=db()
    u=c.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone()
    c.close()
    balance=u["balance"] if u and "balance" in u.keys() else 0

    return S+"""<style>
body{background:#000;color:#fff;font-family:Georgia,serif}
.page{min-height:100vh;padding:20px 15px 100px;box-sizing:border-box}
.head{display:flex;align-items:center;gap:15px;margin-bottom:25px}
.back{color:#00baff;text-decoration:none;font-size:35px}
.title{color:#00baff;font-size:26px;font-weight:bold}
.card{background:#02080d;border:1px solid #078cff;border-radius:22px;padding:20px;margin-bottom:18px}
.balance{text-align:center}
.label{color:#aaa}
.amount{color:#00baff;font-size:34px;font-weight:bold;margin-top:8px}
.methods{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;margin-top:12px}
.method{padding:13px 3px;text-align:center;border:1px solid #078cff;border-radius:12px;font-size:12px}
.method.active{background:#08b9ee}
input{width:100%;box-sizing:border-box;padding:16px;margin-top:10px;border-radius:14px;border:1px solid #078cff;background:#050d15;color:#fff;font-size:16px}
.note{color:#aaa;font-size:13px;line-height:1.5}
.disabled{width:100%;padding:16px;border:0;border-radius:14px;background:#075d78;color:#aaa;font-size:17px;font-weight:bold}
</style>
<div class="page">
<div class="head"><a class="back" href="/my">‹</a><div class="title">Withdraw</div></div>
<div class="card balance"><div class="label">Available Balance</div><div class="amount">"""+str(balance)+"""</div></div>
<div class="card">
<div class="label">Payout Method</div>
<div class="methods">
<div class="method active">MTN UG</div>
<div class="method">Airtel UG</div>
<div class="method">USDT</div>
</div>
<div style="margin-top:20px" class="label">Amount (UGX)</div>
<input type="number" placeholder="Enter amount">
</div>
<div class="card">
<div>Amount <span style="float:right;color:#00baff">0.00</span></div>
<div>Fee <span style="float:right;color:#00baff">0.00</span></div>
<div style="margin-top:8px"><b>You receive</b><span style="float:right;color:#00baff">0.00</span></div>
<p class="note">Withdrawal functionality is currently unavailable in this interface.</p>
<button class="disabled" disabled>Request Withdrawal</button>
</div>
</div>"""
