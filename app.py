
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
    con=db(); cur=con.execute("SELECT name FROM users WHERE phone=?", (session["u"],)).fetchone(); con.close()
    name = cur[0].upper() if cur else "USER"
    return render_template_string(f"""<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><style>*{chr(123)}box-sizing:border-box{chr(125)}body{chr(123)}background:#000;color:#fff;font-family:Arial;margin:0;padding-bottom:80px{chr(125)}.h{chr(123)}display:flex;justify-content:space-between;align-items:center;padding:12px{chr(125)}.logo{chr(123)}color:#c00;font-weight:900;font-size:22px{chr(125)}.banner{chr(123)}margin:10px;border:1px solid #a00;border-radius:12px;padding:15px;background:linear-gradient(90deg,#100000,#300);display:flex;justify-content:space-between;align-items:center{chr(125)}.btn{chr(123)}background:#c00;color:#fff;border:none;padding:10px 18px;border-radius:8px;font-weight:700{chr(125)}.grid4{chr(123)}display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin:10px{chr(125)}.card{chr(123)}background:#0a0a0a;border:1px solid #333;border-radius:10px;padding:10px;text-align:center;font-size:12px{chr(125)}.card b{chr(123)}color:#c00{chr(125)}.check{chr(123)}margin:10px;background:#200;border:1px solid #500;border-radius:10px;padding:12px;display:flex;justify-content:space-between;align-items:center{chr(125)}.grid4b{chr(123)}display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin:10px{chr(125)}.item{chr(123)}background:#0a0a0a;border:1px solid #333;border-radius:10px;padding:15px 5px;text-align:center;font-size:12px{chr(125)}.plans{chr(123)}display:flex;gap:8px;overflow:auto;margin:10px{chr(125)}.plan{chr(123)}min-width:140px;background:#0a0a0a;border:1px solid #333;border-radius:10px;padding:10px;font-size:12px{chr(125)}.red{chr(123)}color:#c00{chr(125)}.nav{chr(123)}position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333;font-size:11px{chr(125)}.nav div{chr(123)}text-align:center;color:#888{chr(125)}.nav.on{chr(123)}color:#c00{chr(125)}</style><div class=h><div class=logo>⬣ CODEX</div><div>🔔³ 👤</div></div><div class=banner><div><div>WELCOME BACK,</div><div style="color:#c00;font-weight:900;font-size:20px">{name}</div><div style="font-size:13px;color:#aaa">Let's grow your wealth together</div><br><button class=btn>Invest Now →</button></div><div style="font-size:50px">🏦</div></div><div class=grid4><div class=card>👛<br>Wallet Balance<br><b>UGX 0</b><br>👁</div><div class=card>📈<br>Total Invested<br><b>UGX 0</b></div><div class=card>💰<br>Total Income<br><b>UGX 0</b></div><div class=card>💼<br>Active Plans<br><b>0</b></div></div><div class=check><div>🎁 <b>Daily Check-In Reward</b><br><small>Check in daily and get <span class=red>UGX 500</span></small></div><button class=btn>Check In →</button></div><div class=grid4b><div class=item>📈<br>Invest</div><div class=item>💰<br>Deposit</div><div class=item>💸<br>Withdraw</div><div class=item>👥<br>Referrals</div><div class=item>📄<br>Transactions</div><div class=item>🎁<br>Raffle</div><div class=item>🎧<br>Support</div><div class=item>💬<br>Chat Manager</div></div><div class=check><div>🏆 <b class=red>RAFFLE DRAW</b><br><small>Win amazing prizes daily</small><br><button class=btn>View Prizes →</button></div><div style="font-size:40px">🎁</div></div><div style="margin:10px;color:#c00;font-weight:900">📈 INVESTMENT PLANS <span style="float:right;font-weight:400">View All Plans ></span></div><div class=plans><div class=plan><b>Starter Plan</b><br>Daily Return <span class=red style="float:right">20%</span><br>Duration <span style="float:right">30 Days</span><br>Min. Invest <span class=red style="float:right">UGX 50,000</span></div><div class=plan><b>Silver Plan</b><br>Daily Return <span class=red style="float:right">20%</span><br>Duration <span style="float:right">30 Days</span><br>Min. Invest <span class=red style="float:right">UGX 250,000</span></div><div class=plan><b>Gold Plan</b><br>Daily Return <span class=red style="float:right">20%</span><br>Duration <span style="float:right">30 Days</span><br>Min. Invest <span class=red style="float:right">UGX 500,000</span></div><div class=plan><b>Platinum Plan</b><br>Daily Return <span class=red style="float:right">20%</span><br>Duration <span style="float:right">30 Days</span><br>Min. Invest <span class=red style="float:right">UGX 1,000,000</span></div></div><div class=check><div>🎧 <b>Need Help?</b><br><small>Our support team is always here for you.</small></div><button class=btn>Contact Support</button></div><div class=nav><div class=on>🏠<br>Home</div><div>📈<br>Invest</div><div>⇄<br>Transactions</div><div>👥<br>Referrals</div><div>👤<br>Account</div></div>""")

if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
