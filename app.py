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
 for pl,amt in [("Starter Plan",50000),("Silver Plan",250000),("Gold Plan",500000),("Platinum Plan",10000000)]: h+="<a href='/invest'><div class=card style='min-width:140px'><b>"+pl+"</b><br>UGX "+str(amt)+"</div></a>"
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
@app.route("/account")
@app.route("/account_old")
@need
def acc():
 u=cu();return S+hdr()+"<div class=card><h3>Account</h3><p>"+u["name"]+"</p><p>"+u["phone"]+"</p><p>UGX "+str(u["balance"])+"</p><p>Ref: "+u["refcode"]+"</p><a class=btn href='/logout'>Logout</a></div>"+N
@app.route("/logout")
def lo(): session.clear();return redirect("/login")
@app.route("/wallet")
@need
def wal():
 return S+hdr()+"<div class=card><h3>Wallet</h3><p>UGX "+str(cu()['balance'])+"</p></div>"+N


@app.route("/withdraw_submit", methods=["POST"])
def withdraw_submit():
    from flask import request
    try: amt=int(request.form.get("amount",0))
    except: amt=0
    if amt < 10000:
        return "<h3 style='color:red;text-align:center;margin-top:50px'>The minimum withdraw is 10k</h3><br><center><a href='/withdraw'>Back</a></center>"
    return "<h3 style='color:green;text-align:center;margin-top:50px'>withdrawal successful, wait for review</h3><br><center><a href='/withdraw'>Back</a></center>"
@app.route("/withdraw")
def withdraw():
    bal = 0
    import pathlib as _pl
    _p=_pl.Path(__file__).parent/"w.html"
    _p2=_pl.Path("w.html")
    _f=_p if _p.exists() else _p2
    html=_f.read_text().replace("BALPLACE", str(bal)) if _f.exists() else "withdraw page missing w.html"
    return html

@app.route("/invest")
def invest():
    return open('templates/invest.html').read()

def init_dep():
 try:
  _c=db();_c.execute("CREATE TABLE IF NOT EXISTS deposits(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,phone TEXT,amount INTEGER,txn_id TEXT,status TEXT DEFAULT 'pending')");_c.commit();_c.close()
 except Exception as e: print(e)
try:
 init_dep()
 init_inv()
except: pass

def invest():
    import os
    return open('templates/invest.html').read()

@app.route('/invest/<pid>')
def invest_detail(pid):
 u=cur_user()
 if not u: return redirect('/login')
 p=PLANS.get(pid)
 if not p: return redirect('/invest')
 b=wallet(u[0])
 total=p['daily']*p['days']
 return f"<style>body{background:#000;color:#fff;font-family:sans-serif;padding:20px}.card{background:#111;border:1px solid gold;border-radius:12px;padding:20px}.btn{background:red;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none;display:inline-block;margin:5px}</style><div class=card><h2 style='color:red'>{p['name']}</h2>Amount: UGX {p['price']:,}<br>Duration: {p['days']} Days<br>Configured Daily Return: UGX {p['daily']:,}<br>Projected Total Return: UGX {total:,}<br>Wallet Balance: UGX {b:,}<br><br><small>Actual credits are subject to platform rules. Projected returns are not guaranteed profits.</small><br><br><a class=btn href='/invest/confirm/{pid}'>CONFIRM INVESTMENT</a> <a class=btn style='background:#333' href='/invest'>CANCEL</a></div>"

@app.route('/invest/confirm/<pid>')
def invest_confirm(pid):
 import datetime
 u=cur_user()
 if not u: return redirect('/login')
 p=PLANS.get(pid)
 if not p: return redirect('/invest')
 b=wallet(u[0])
 if b < p['price']:
  need=p['price']-b
  return f"<style>body{{background:#000;color:#fff;font-family:sans-serif;padding:20px}}.card{{background:#111;border:1px solid red;border-radius:12px;padding:20px}}</style><div class=card><h2 style='color:red'>INSUFFICIENT FUNDS</h2>You need UGX {p['price']:,} to activate {p['name']}.<br>Current balance: UGX {b:,}<br>Additional required: UGX {need:,}<br><br><a href='/deposit' style='background:red;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none'>DEPOSIT FUNDS</a> <a href='/invest' style='color:#fff'>CANCEL</a></div>"
 # deduct atomically
 c=db()
 try:
  c.execute("BEGIN IMMEDIATE")
  r=c.execute("SELECT balance FROM users WHERE id=?",(u[0],)).fetchone()
  if r[0] < p['price']:
   c.rollback();c.close();return redirect(f'/invest/{pid}')
  import datetime as dt
  sd=dt.date.today().isoformat();ed=(dt.date.today()+dt.timedelta(days=p['days'])).isoformat();now=dt.datetime.now().isoformat()
  c.execute("UPDATE users SET balance=balance-? WHERE id=?",(p['price'],u[0]))
  cur=c.execute("INSERT INTO investments(user_id,plan_id,plan_name,amount,daily_return,duration_days,start_date,end_date,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(u[0],pid,p['name'],p['daily'],p['daily'],p['days'],sd,ed,'ACTIVE',now))
  iid=cur.lastrowid
  c.execute("INSERT INTO transactions(user_id,type,amount,ref,status,created_at) VALUES(?,?,?,?,?,?)",(u[0],'INVESTMENT',-p['price'],f'INV-{iid}-{pid}','completed',now))
  c.commit()
 except Exception as e:
  try:c.rollback()
  except:pass
  c.close();return f"Error: {e}"
 c.close()
 return f"<style>body{{background:#000;color:#fff;font-family:sans-serif;padding:20px}}.card{{background:#111;border:1px solid gold;border-radius:12px;padding:20px}}</style><div class=card><h2 style='color:red'>INVESTMENT ACTIVATED</h2>Plan: {p['name']}<br>Amount: UGX {p['price']:,}<br>Start: {sd}<br>End: {ed}<br>Status: ACTIVE<br><br><a href='/investments' style='background:red;color:#fff;padding:12px 20px;border-radius:8px;text-decoration:none'>VIEW MY INVESTMENT</a></div>"

@app.route('/investments')
def my_investments():
 import datetime
 u=cur_user()
 if not u: return redirect('/login')
 credit_daily()
 c=db();rows=c.execute("SELECT * FROM investments WHERE user_id=? ORDER BY id DESC",(u[0],)).fetchall();c.close()
 h="<style>body{background:#000;color:#fff;font-family:sans-serif;padding:15px}.card{background:#111;border:1px solid gold;border-radius:12px;padding:15px;margin:10px 0}.bar{background:#333;height:8px;border-radius:4px}.fill{background:gold;height:8px;border-radius:4px}</style><h2 style='color:red'>MY INVESTMENTS</h2>"
 for r in rows:
  iid,_,pid,pname,amt,dret,days,sd,ed,st,acc,_,_=r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12]
  import datetime as dt
  try:rem=(dt.date.fromisoformat(ed)-dt.date.today()).days
  except:rem=0
  rem=max(0,rem);prog=int(((days-rem)/days*100)) if days else 0
  h+=f"<div class=card><b style='color:red'>{pname}</b><br>Amount: UGX {amt:,}<br>Start: {sd} End: {ed}<br>Status: {st}<br>Daily: UGX {dret:,} Accrued: UGX {acc:,}<br>Remaining: {rem} days<div class=bar><div class=fill style='width:{prog}%'></div></div><small>NEXT RETURN: countdown server-side</small></div>"
 return h+"<a href='/invest' style='color:red'>← Back to Plans</a>"
