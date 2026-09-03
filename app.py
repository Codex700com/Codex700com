from flask import Flask,request,redirect,session
import sqlite3,datetime,uuid
app=Flask(__name__);app.secret_key="codex700secret"
DB="codex700.db"
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 c=db()
 c.executescript("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,phone TEXT UNIQUE,password TEXT,invite TEXT,balance INTEGER DEFAULT 0,refcode TEXT);CREATE TABLE IF NOT EXISTS investments(id INTEGER PRIMARY KEY,user_id INT,plan TEXT,amount INT,active INT DEFAULT 1,date TEXT);CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY,user_id INT,type TEXT,amount INT,status TEXT,date TEXT,ref TEXT);CREATE TABLE IF NOT EXISTS checkins(user_id INT,date TEXT PRIMARY KEY);CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,user_id INT,msg TEXT,date TEXT);CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY,user_id INT,who TEXT,msg TEXT,date TEXT);")
 c.commit();c.close()
init()
def need(f):
 def w(*a,**kw):
  if "uid" not in session: return redirect("/login")
  return f(*a,**kw)
 w.__name__=f.__name__;return w
def cu():
 c=db();u=c.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone();c.close();return u
S="<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{box-sizing:border-box}body{background:#000;color:#fff;font-family:Arial;margin:0;padding-bottom:80px}a{color:inherit;text-decoration:none}.card{background:#0a0a0a;border:1px solid #8a6a00;border-radius:10px;padding:8px;margin:0;font-size:13px;line-height:1.3;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:normal;word-break:break-word;text-align:center}.btn{background:#c00;color:#fff;border:none;padding:10px 18px;border-radius:8px;display:inline-block}.logo{color:#c00;font-weight:900;font-size:22px}input{width:100%;padding:12px;margin:8px 0;background:#111;border:1px solid #d4a017;border-radius:8px;color:#fff}.nav{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333;font-size:11px}.red{color:#c00}.gold{color:#d4a017}</style>"
N="<div class=nav><a href='/home'><div>🏠<br>Home</div></a><a href='/invest'><div>📈<br>Invest</div></a><a href='/transactions'><div>⇄<br>Transactions</div></a><a href='/referrals'><div>👥<br>Referrals</div></a><a href='/account'><div>👤<br>Account</div></a></div>"
def hdr(): return "<div style='display:flex;justify-content:space-between;padding:12px;'><a href='/menu'>☰</a><div class=logo>⬣ CODEX</div><div><a href='/notifications'>🔔</a> <a href='/account'>👤</a></div></div>"

@app.route("/")
def i(): return redirect("/register")
@app.route("/register",methods=["GET","POST"])
def reg():
 m=""
 if request.method=="POST":
  n=request.form["name"];p=request.form["phone"];pw=request.form["password"];cf=request.form["confirm"];inv=request.form.get("invite","")
  if pw!=cf: m="Dear customer,ur password is invalid"
  else:
   try:
    c=db();rc=uuid.uuid4().hex[:6].upper();c.execute("INSERT INTO users(name,phone,password,invite,balance,refcode) VALUES(?,?,?,?,0,?)",(n,p,pw,inv,rc));c.commit();c.close();return redirect("/login")
   except: m="Phone already registered"
 return S+"<div class=logo style='text-align:center;margin:20px'>👑 CODEX700</div><div class=card><h2 class=gold style='text-align:center'>REGISTER</h2>"+(f"<p>{m}</p>" if m else "")+"<form method=POST><input name=name placeholder='Enter Name' required><input name=phone placeholder='Enter Phone' required><input name=password type=password placeholder='Enter Password' required><input name=confirm type=password placeholder='Confirm Password' required><input name=invite placeholder='Invitation code'><button class=btn style='width:100%'>REGISTER</button></form><p style='text-align:center'>Have account? <a href='/login' class=gold>Login</a></p></div>"

@app.route("/login",methods=["GET","POST"])
def login():
 m="";ok=False
 if request.method=="POST":
  p=request.form["phone"];pw=request.form["password"];c=db();u=c.execute("SELECT * FROM users WHERE phone=? AND password=?",(p,pw)).fetchone();c.close()
  if not u: m="Dear customer, wrong information applied"
  else: session["uid"]=u["id"];ok=True
 if ok: return S+"<div class=card><p>registration successful</p><script>setTimeout(()=>location.href='/home',1500)</script></div>"
 return S+"<div class=logo style='text-align:center;margin:20px'>👑 CODEX700</div><div class=card><h2 class=gold style='text-align:center'>LOGIN</h2>"+(f"<p>{m}</p>" if m else "")+"<form method=POST><input name=phone placeholder='Enter Phone' required><input name=password type=password placeholder='Enter Password' required><button class=btn style='width:100%'>LOGIN</button></form><p style='text-align:center'>No account? <a href='/register' class=gold>Register</a></p></div>"

@app.route("/home")
@need
def home():
 u=cu();c=db()
 ti=c.execute("SELECT COALESCE(SUM(amount),0) s FROM investments WHERE user_id=?",(u["id"],)).fetchone()["s"]
 ac=c.execute("SELECT COUNT(*) n FROM investments WHERE user_id=? AND active=1",(u["id"],)).fetchone()["n"]
 c.close()
 h=S+hdr()
 h+="<div class=card><div>WELCOME BACK,</div><div class=red style='font-weight:900;font-size:20px'>"+u["name"].upper()+"</div><br><a class=btn href='/invest'>Invest Now →</a></div>"
 h+="<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:8px'>"
 h+="<a href='/wallet'><div class=card>Wallet<br><b class=red>UGX "+str(u["balance"])+"</b></div></a>"
 h+="<a href='/investments'><div class=card>Invested<br><b class=red>UGX "+str(ti)+"</b></div></a>"
 h+="<a href='/transactions'><div class=card>Income<br><b class=red>UGX 0</b></div></a>"
 h+="<a href='/investments'><div class=card>Active<br><b class=red>"+str(ac)+"</b></div></a></div>"
 h+="<div class=card>🎁 Daily Check-In <a class=btn href='/checkin'>Check In →</a></div>"
 h+="<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:8px'>"
 acts=[("Invest","/invest","📈"),("Deposit","/deposit","💰"),("Withdraw","/withdraw","💸"),("Referrals","/referrals","👥"),("Transactions","/transactions","📄"),("Raffle","/raffle","🎁"),("Support","/support","🎧"),("Chat","/chat","💬")]
 for nm,lk,ic in acts: h+="<a href='"+lk+"'><div class=card>"+ic+"<br>"+nm+"</div></a>"
 h+="</div><a href='/raffle'><div class=card>🏆 <b class=red>RAFFLE DRAW</b><br><span class=btn>View Prizes →</span></div></a>"
 h+="<div class=card><b class=red>INVESTMENT PLANS</b> <a href='/invest' style='float:right'>View All ></a></div><div style='display:flex;gap:8px;overflow:auto;margin:10px'>"
 for pl,amt in [("Starter Plan",50000),("Silver Plan",250000),("Gold Plan",500000),("Platinum Plan",1000000)]: h+="<a href='/invest'><div class=card style='min-width:140px'><b>"+pl+"</b><br>UGX "+str(amt)+"</div></a>"
 h+="</div><div class=card>Need Help? <a class=btn href='/support'>Contact Support</a></div>"+N
 return h

@app.route("/menu")
@need
def menu():
 ls=[("Home","/home"),("Invest","/invest"),("Deposit","/deposit"),("Withdraw","/withdraw"),("Transactions","/transactions"),("Referrals","/referrals"),("Raffle","/raffle"),("Support","/support"),("Chat Manager","/chat"),("Account","/account"),("Logout","/logout")]
 h=S+hdr()+"<div class=card><h3>Menu</h3>"
 for nm,lk in ls: h+="<p><a href='"+lk+"'>"+nm+"</a></p>"
 return h+"</div>"+N
@app.route("/notifications")
@need
def notif():
 c=db();rs=c.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC",(session["uid"],)).fetchall();c.close()
 h=S+hdr()+"<div class=card><h3>Notifications</h3>"
 for r in rs: h+="<p>"+r["msg"]+"</p>"
 return h+"</div>"+N
@app.route("/account_old")
@need
def acc():
 u=cu();return S+hdr()+"<div class=card><h3>Account</h3><p>"+u["name"]+"</p><p>"+u["phone"]+"</p><p>UGX "+str(u["balance"])+"</p><p>Ref: "+u["refcode"]+"</p><a class=btn href='/logout'>Logout</a></div>"+N
@app.route("/logout")
def lo(): session.clear();return redirect("/login")
@app.route("/wallet")
@need
def wal():
 u=cu();return S+hdr()+"<div class=card><h3>Wallet UGX "+str(u["balance"])+"</h3><a class=btn href='/deposit'>Deposit</a> <a class=btn href='/withdraw'>Withdraw</a></div>"+N
@app.route("/invest")
@need
def inv():
 h=S+hdr()+"<div class=card><h3>Investment Plans</h3></div>"
 for pl,amt in [("Starter Plan",50000),("Silver Plan",250000),("Gold Plan",500000),("Platinum Plan",1000000)]:
  h+="<div class=card><b>"+pl+"</b><br>Daily 20% 30 Days<br>Min UGX "+str(amt)+"<br><br><a class=btn href='/do_invest?plan="+pl+"&amt="+str(amt)+"'>Invest Now</a></div>"
 return h+N
@app.route("/do_invest")
@need
def doinv():
 pl=request.args.get("plan");amt=int(request.args.get("amt"));u=cu()
 if u["balance"]<amt: return S+"<div class=card>Insufficient <a href='/deposit'>Deposit</a></div>"+N
 c=db();c.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,u["id"]));c.execute("INSERT INTO investments(user_id,plan,amount,date) VALUES(?,?,?,?)",(u["id"],pl,amt,datetime.date.today().isoformat()));c.execute("INSERT INTO transactions(user_id,type,amount,status,date,ref) VALUES(?,?,?,?,?,?)",(u["id"],"investment",amt,"completed",datetime.date.today().isoformat(),uuid.uuid4().hex[:8]));c.commit();c.close()
 return redirect("/investments")
@app.route("/investments")
@need
def invs():
 c=db();rs=c.execute("SELECT * FROM investments WHERE user_id=?",(session["uid"],)).fetchall();c.close()
 h=S+hdr()+"<div class=card><h3>My Investments</h3>"
 for r in rs: h+="<p>"+r["plan"]+" UGX "+str(r["amount"])+"</p>"
 return h+"</div>"+N
@app.route("/deposit",methods=["GET","POST"])
@need
def dep():
 if request.method=="POST":
  amt=int(request.form["amount"]);c=db();c.execute("UPDATE users SET balance=balance+? WHERE id=?",(amt,session["uid"]));c.execute("INSERT INTO transactions(user_id,type,amount,status,date,ref) VALUES(?,?,?,?,?,?)",(session["uid"],"deposit",amt,"completed",datetime.date.today().isoformat(),uuid.uuid4().hex[:8]));c.commit();c.close();return redirect("/wallet")
 return S+hdr()+"<div class=card><h3>Deposit</h3><form method=POST><input name=amount type=number placeholder='Amount' required><button class=btn>Deposit</button></form></div>"+N
@app.route("/withdraw",methods=["GET","POST"])
@need
def wit():
 u=cu();m=""
 if request.method=="POST":
  amt=int(request.form["amount"])
  if amt>u["balance"]: m="Insufficient balance"
  else: c=db();c.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,u["id"]));c.execute("INSERT INTO transactions(user_id,type,amount,status,date,ref) VALUES(?,?,?,?,?,?)",(u["id"],"withdraw",amt,"completed",datetime.date.today().isoformat(),uuid.uuid4().hex[:8]));c.commit();c.close();return redirect("/transactions")
 return S+hdr()+"<div class=card><h3>Withdraw Bal UGX "+str(u["balance"])+"</h3>"+m+"<form method=POST><input name=amount type=number required><button class=btn>Withdraw</button></form></div>"+N
@app.route("/transactions")
@need
def tr():
 c=db();rs=c.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC",(session["uid"],)).fetchall();c.close()
 h=S+hdr()+"<div class=card><h3>Transactions</h3>"
 for r in rs: h+="<p>"+r["date"]+" "+r["type"]+" UGX "+str(r["amount"])+" "+r["ref"]+" "+r["status"]+"</p>"
 return h+"</div>"+N
@app.route("/checkin")
@need
def ci():
 c=db();t=datetime.date.today().isoformat();ex=c.execute("SELECT * FROM checkins WHERE user_id=? AND date=?",(session["uid"],t)).fetchone();c.close()
 if ex: h="Today's reward has already been claimed."
 else: h="<a class=btn href='/claim'>CLAIM UGX 500</a>"
 return S+hdr()+"<div class=card><h3>Daily Check-In UGX 500</h3>"+h+"</div>"+N
@app.route("/claim")
@need
def cl():
 t=datetime.date.today().isoformat();c=db()
 try: c.execute("INSERT INTO checkins(user_id,date) VALUES(?,?)",(session["uid"],t));c.execute("UPDATE users SET balance=balance+500 WHERE id=?",(session["uid"],));c.commit()
 except: pass
 c.close();return redirect("/checkin")
@app.route("/referrals")
@need
def rf():
 u=cu();c=db();n=c.execute("SELECT COUNT(*) n FROM users WHERE invite=?",(u["refcode"],)).fetchone()["n"];c.close()
 link="https://codex700com.onrender.com/register?ref="+u["refcode"]
 return S+hdr()+"<div class=card><h3>Referrals</h3><input id=rl value='"+link+"' readonly><button class=btn onclick=\"navigator.clipboard.writeText(document.getElementById('rl').value);alert('Referral link copied.')\">Copy Link</button><p>Total: "+str(n)+"</p><p>Code: "+u["refcode"]+"</p></div>"+N
@app.route("/raffle")
@need
def ra(): return S+hdr()+"<div class=card><h3 class=red>RAFFLE DRAW</h3><p>Prizes daily</p><p>Draw: Tomorrow 8PM</p><p>My tickets: 0</p><p>Winners: Brian, Shakira</p></div>"+N
@app.route("/support")
@need
def sup(): return S+hdr()+"<div class=card><h3>Support</h3><p>FAQ</p><a class=btn href='/chat'>Chat with support</a></div>"+N
@app.route("/chat",methods=["GET","POST"])
@need
def ch():
 c=db()
 if request.method=="POST": c.execute("INSERT INTO chats(user_id,who,msg,date) VALUES(?,?,?,?)",(session["uid"],"user",request.form["msg"],datetime.datetime.now().isoformat()));c.commit()
 rs=c.execute("SELECT * FROM chats WHERE user_id=? ORDER BY id",(session["uid"],)).fetchall();c.close()
 h=S+hdr()+"<div class=card><h3>Chat</h3>"
 for r in rs: h+="<p><b>"+r["who"]+":</b> "+r["msg"]+"</p>"
 return h+"<form method=POST><input name=msg required><button class=btn>Send</button></form></div>"+N
exec(open('acc_new.py').read(), globals())
if __name__=="__main__": app.run(host="0.0.0.0",port=5000)
