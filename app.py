import sqlite3, pathlib, os, random
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
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#fff;font-family:system-ui,sans-serif;overflow-x:hidden}
.card{position:relative;z-index:2;min-height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column}
a{color:#0a84ff}
</style>
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
    return S+WAVE+'<div style="position:relative;z-index:2;min-height:100vh;display:flex;align-items:center;justify-content:center"><div style="background:rgba(0,0,0,0.7);border:1px solid #0a84ff;border-radius:16px;padding:30px;text-align:center"><p style="color:#4ade80">Registration Successful!</p><script>setTimeout(function(){location.href="/login"},1200)</script></div></div>'
 colors=["#3b82f6","#f59e0b","#10b981","#a855f7","#ec4899"]
 col_html="".join(['<span style="color:'+random.choice(colors)+';font-weight:900;margin:1px">'+ch+'</span>' for ch in captcha])
 html='<style>.reg-wrap{position:relative;z-index:2;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding-top:10vh;padding-left:18px;padding-right:18px}.welcome{font-size:34px;font-weight:800;color:#fff;margin-bottom:22px}.pill{width:100%;max-width:360px;height:52px;background:rgba(0,0,0,0.55);border:1px solid #555;border-radius:26px;display:flex;align-items:center;padding:0 16px;margin:9px 0;position:relative}.pill input{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:15px;margin-left:10px}.captcha-box{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:#fff;border-radius:8px;padding:6px 14px;font-size:22px;letter-spacing:3px;font-weight:800}.reg-btn{width:100%;max-width:360px;height:50px;background:transparent;border:1.6px solid #0a84ff;border-radius:26px;color:#0a84ff;font-size:19px;font-weight:600;margin-top:18px;cursor:pointer}.err{color:#ff6b6b;font-size:13px;max-width:360px;text-align:center;margin:6px;background:rgba(255,0,0,0.08);padding:8px;border-radius:8px}</style><div class="reg-wrap"><div class="welcome">Welcome</div><div class="err">'+m+'</div><form method="POST" style="width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center"><input type="hidden" name="real_captcha" value="'+captcha+'"><div class="pill"><input name="phone" placeholder="Phone Number" required></div><div class="pill"><input name="password" type="password" placeholder="Set Password" required></div><div class="pill"><input name="confirm" type="password" placeholder="Confirm Password" required></div><div class="pill"><input name="captcha_input" placeholder="Verification Code" required><div class="captcha-box">'+col_html+'</div></div><div class="pill"><input name="invite" placeholder="Invitation Code"></div><button class="reg-btn">Register</button><div style="margin-top:14px"><a href="/login" style="color:#aaa;text-decoration:none">‹ Login</a></div></form></div>'
 return S+WAVE+html

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
   return S+WAVE+'<div class="card"><p style="color:#4ade80">Login successful</p><script>setTimeout(function(){location.href="/home"},800)</script></div>'
  else:
   m="Wrong password. Please try again." if ex else "Phone not registered. Please register first."
 html='<style>.login-wrap{position:relative;z-index:2;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding-top:18vh;padding-left:18px;padding-right:18px}.welcome{font-size:36px;font-weight:800;color:#fff;margin-bottom:28px}.pill{width:100%;max-width:360px;height:52px;background:rgba(0,0,0,0.5);border:1px solid #555;border-radius:14px;display:flex;align-items:center;padding:0 14px;margin:10px 0}.pill input{flex:1;background:transparent;border:none;outline:none;color:#fff;font-size:15px;margin-left:10px}.login-btn{width:100%;max-width:360px;height:50px;background:transparent;border:1.5px solid #0a84ff;border-radius:12px;color:#0a84ff;font-size:18px;font-weight:600;margin-top:22px;cursor:pointer}.err{color:#ff6b6b;font-size:13px;max-width:360px;text-align:center;margin:6px}.bot{width:100%;max-width:360px;display:flex;justify-content:space-between;margin-top:16px;color:#bbb;font-size:13px}.bot a{color:#bbb;text-decoration:none}</style><div class="login-wrap"><div class="welcome">Welcome</div><div class="err">'+m+'</div><form method="POST" style="width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center"><div class="pill"><input name="phone" placeholder="Phone Number" required></div><div class="pill"><input name="password" type="password" placeholder="Login Password" required></div><button class="login-btn">Login</button><div class="bot"><a href="/register">Register</a><a href="/reset">Forgot your password?</a></div></form></div>'
 return S+WAVE+html

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
 return S+WAVE+'<div class="card"><h2>Welcome to CODEX700</h2><p>Home page</p><a href="/login">Logout</a></div>'

if __name__=="__main__":
 app.run(host="0.0.0.0",port=5000,debug=True)
