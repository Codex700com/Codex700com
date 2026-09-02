
from flask import Flask, request, redirect, session, render_template_string
import sqlite3, os
app = Flask(__name__)
app.secret_key = "codex700"
DB="codex700.db"

def db():
    con=sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE, password TEXT, invite TEXT)")
    return con

CSS="""<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<style>
*{box-sizing:border-box} html,body{margin:0;padding:0;overflow-x:hidden}
body{background:#000;color:#fff;font-family:Arial;display:flex;flex-direction:column;align-items:center;min-height:100vh;margin:0;justify-content:center;padding:15px}
.logo{color:gold;font-size:28px;font-weight:900;margin:30px 0 15px}
.box{background:#0a0a0a;border:2px solid gold;border-radius:20px;padding:25px;width:90%;max-width:380px;box-shadow:0 0 20px gold}
h2{color:gold;text-align:center;margin-bottom:20px}
label{color:#d4a017;display:block;margin:12px 0 5px}
input{width:100%;padding:12px;background:#111;border:1px solid #d4a017;border-radius:12px;color:#fff;box-sizing:border-box}
button{width:100%;padding:14px;margin-top:20px;background:linear-gradient(orange,gold);border:none;border-radius:12px;font-weight:900;font-size:18px}
a{color:gold}
.msg{background:#220000;border:1px solid red;padding:10px;border-radius:8px;margin:10px 0;text-align:center}
.ok{background:#002200;border:1px solid green;padding:10px;border-radius:8px;margin:10px 0;text-align:center}
.link{text-align:center;margin-top:15px}
</style>
"""

REG=CSS+"""
<div class="logo">👑 CODEX700 🔥</div>
<div class="box"><h2>REGISTER</h2>
{% if msg %}<div class="msg">{{msg}}</div>{% endif %}
<form method="POST">
<label>Name</label><input name="name" placeholder="Enter Name" required>
<label>Phone number</label><input name="phone" placeholder="Enter Phone number" required>
<label>Password</label><input name="password" type="password" placeholder="Enter Password" required>
<label>Confirm password</label><input name="confirm" type="password" placeholder="Confirm Password" required>
<label>Invitation code</label><input name="invite" placeholder="Invitation code">
<button>REGISTER</button>
</form><div class="link">Have account? <a href="/login">Login</a></div></div>
"""

LOG=CSS+"""
<div class="logo">👑 CODEX700 🔥</div>
<div class="box"><h2>LOGIN</h2>
{% if msg %}<div class="msg">{{msg}}</div>{% endif %}
{% if ok %}<div class="ok">{{ok}}</div><script>setTimeout(()=>location.href='/dashboard',1500)</script>{% endif %}
{% if not ok %}
<form method="POST">
<label>Phone number</label><input name="phone" placeholder="Enter Phone number" required>
<label>Password</label><input name="password" type="password" placeholder="Enter Password" required>
<button>LOGIN</button>
</form><div class="link">No account? <a href="/register">Register</a></div>
{% endif %}</div>
"""

@app.route("/")
def i(): return redirect("/register")

@app.route("/register", methods=["GET","POST"])
def reg():
    msg=None
    if request.method=="POST":
        n=request.form["name"]; p=request.form["phone"]; pw=request.form["password"]; c=request.form["confirm"]; inv=request.form.get("invite","")
        if pw!=c:
            msg="Dear customer,ur password is invalid"
        else:
            try:
                con=db(); con.execute("INSERT INTO users(name,phone,password,invite) VALUES(?,?,?,?)",(n,p,pw,inv)); con.commit(); con.close()
                return redirect("/login")
            except: msg="Phone already registered"
    return render_template_string(REG, msg=msg)

@app.route("/login", methods=["GET","POST"])
def login():
    msg=None; ok=None
    if request.method=="POST":
        p=request.form["phone"]; pw=request.form["password"]
        con=db(); cur=con.execute("SELECT * FROM users WHERE phone=? AND password=?",(p,pw)).fetchone(); con.close()
        if not cur:
            msg="Dear customer, wrong information applied"
        else:
            session["u"]=p
            ok="registration successful"
    return render_template_string(LOG, msg=msg, ok=ok)

@app.route("/dashboard")
def dash():
    if "u" not in session: return redirect("/login")
    return f"<body style='background:#000;color:gold;text-align:center;font-family:Arial'><h1>👑 CODEX700 Dashboard</h1><p>Welcome {session['u']}</p><a href='/login' style='color:gold'>Logout</a></body>"

if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
