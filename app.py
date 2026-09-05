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
 c=db();u=c.execute("SELECT * FROM users WHERE id=?",(session.get("uid"),)).fetchone();c.close();return u
S="<meta name='viewport' content='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no'><style>*{box-sizing:border-box}body{background:#000;color:#fff;font-family:Arial;margin:0;padding-bottom:80px}a{color:inherit;text-decoration:none}.card{background:#0a0a0a;border:1px solid #8a6a00;border-radius:10px;padding:8px;margin:0;font-size:13px;line-height:1.3;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:normal;word-break:break-word;text-align:center}.btn{background:#c00;color:#fff;border:none;padding:10px 18px;border-radius:8px;display:inline-block}.logo{color:#c00;font-weight:900;font-size:22px}input{width:100%;padding:12px;margin:8px 0;background:#111;border:1px solid #d4a017;border-radius:8px;color:#fff}.nav{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333;font-size:11px}.red{color:#c00}.gold{color:#d4a017}</style>"
N="<div class=nav><a href='/home'><div>🏠<br>Home</div></a><a href='/invest'><div>📈<br>Invest</div></a><a href='/transactions'><div>⇄<br>Transactions</div></a><a href='/referrals'><div>👥<br>Referrals</div></a><a href='/account'><div>👤<br>Account</div></a></div>"
def hdr(): return "<div style='display:flex;justify-content:space-between;padding:12px;'><a href='/menu'>☰</a><div class=logo>⬣ CODEX</div><div><a href='/notifications'>🔔</a> <a href='/account'>👤</a></div></div>"


def fix_chats_table():
    try:
        import sqlite3
        con = sqlite3.connect("codex700.db")
        cols = [r[1] for r in con.execute("PRAGMA table_info(chats)").fetchall()]
        print("chats cols:", cols)
        if not cols:
            con.execute("CREATE TABLE chats (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, user_id TEXT, sender TEXT, who TEXT, msg TEXT, date TEXT, created TEXT)")
        else:
            for col in ["uid","user_id","sender","who","msg","date","created"]:
                if col not in cols:
                    con.execute(f"ALTER TABLE chats ADD COLUMN {col} TEXT")
                    print("added", col)
        con.commit(); con.close()
    except Exception as e:
        print("fix_chats_table error:", e)

fix_chats_table()


def ensure_checkin_schema():
    try:
        import sqlite3, time
        con = sqlite3.connect("codex700.db")
        con.execute("CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, created_at INTEGER)")
        # ensure users has balance and last_checkin
        cols = [r[1] for r in con.execute("PRAGMA table_info(users)").fetchall()]
        for col, typ in [("balance","INTEGER DEFAULT 0"),("last_checkin","INTEGER DEFAULT 0")]:
            if col not in cols:
                con.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
                print(f"added users.{col}")
        con.commit(); con.close()
    except Exception as e:
        print("checkin schema error:", e)
ensure_checkin_schema()

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
 c=db();rs=c.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC",(session.get("uid"),)).fetchall();c.close()
 h=S+hdr()+"<div class=card><h3>Notifications</h3>"
 for r in rs: h+="<p>"+r["msg"]+"</p>"
 return h+"</div>"+N
@app.route("/account")
def account_page():
    import pathlib
    return pathlib.Path("templates/account.html").read_text()

@app.route("/api/account")
def api_account():
    import sqlite3, datetime
    from flask import session, jsonify
    uid=session.get("user_id") or session.get("uid")
    con=sqlite3.connect("codex700.db"); con.row_factory=sqlite3.Row
    u=con.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone() if uid else None
    if not u:
        # guest zero defaults
        return jsonify({"name":"Guest","member_id":"CDX000000","email":"","phone":"","balance":0,"total_invested":0,"total_income":0,"active_investments":0,"joined":"-","lang":"en","notif_muted":False})
    # totals from transactions
    rows=con.execute("SELECT type,amount FROM transactions WHERE user_id=?",(str(uid),)).fetchall()
    inv=sum(-r["amount"] for r in rows if r["type"]=="invest" and r["amount"]<0)
    inc=sum(r["amount"] for r in rows if r["type"] in ("earn","referral","checkin") and r["amount"]>0)
    act=con.execute("SELECT COUNT(*) FROM investments WHERE user_id=? AND status='active'",(str(uid),)).fetchone()[0] if "investments" in [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else 0
    try: jd=datetime.datetime.fromtimestamp(int(u["joined_at"])).strftime("%d %b %Y")
    except: jd="-"
    d=dict(id=u["id"],name=u["name"] if "name" in u.keys() else "User",member_id=u["member_id"] if "member_id" in u.keys() else "",email=u["email"] if "email" in u.keys() else "",phone=u["phone"] if "phone" in u.keys() else "",balance=u["balance"] if "balance" in u.keys() else 0,total_invested=inv,total_income=inc,active_investments=act,joined=jd,lang=u["lang"] if "lang" in u.keys() and u["lang"] else "en",notif_muted=bool(u["notif_muted"]) if "notif_muted" in u.keys() and u["notif_muted"] else False)
    con.close()
    return jsonify(d)

@app.route("/api/account/lang", methods=["POST"])
def api_lang():
    import sqlite3
    from flask import session, request, jsonify
    l=request.get_json().get("lang","en")
    con=sqlite3.connect("codex700.db")
    con.execute("UPDATE users SET lang=? WHERE id=?",(l, session.get("user_id") or session.get("uid")))
    con.commit(); con.close()
    return jsonify({"ok":True})

@app.route("/api/account/notif", methods=["POST"])
def api_notif():
    import sqlite3
    from flask import session, request, jsonify
    m=1 if request.get_json().get("muted") else 0
    con=sqlite3.connect("codex700.db")
    con.execute("UPDATE users SET notif_muted=? WHERE id=?",(m, session.get("user_id") or session.get("uid")))
    con.commit(); con.close()
    return jsonify({"ok":True})

@app.route("/api/account/password", methods=["POST"])
def api_pwd():
    import sqlite3, hashlib
    from flask import session, request, jsonify
    pwd=request.get_json().get("pwd","")
    if len(pwd)<4: return jsonify({"msg":"Too short"})
    h=hashlib.sha256(pwd.encode()).hexdigest()
    con=sqlite3.connect("codex700.db")
    con.execute("UPDATE users SET password=? WHERE id=?",(h, session.get("user_id") or session.get("uid")))
    con.commit(); con.close()
    return jsonify({"msg":"Password changed successfully"})

@app.route("/api/account/reset", methods=["POST"])
def api_reset():
    return __import__("flask").jsonify({"msg":"Reset link sent to your email"})

@app.route("/api/account/statement")
def api_statement():
    import sqlite3, csv, io
    from flask import session, Response
    uid=str(session.get("user_id") or session.get("uid") or "guest")
    con=sqlite3.connect("codex700.db")
    rows=con.execute("SELECT created_at,type,title,amount,status,ref FROM transactions WHERE user_id=? ORDER BY id DESC",(uid,)).fetchall()
    con.close()
    out=io.StringIO(); w=csv.writer(out); w.writerow(["date","type","title","amount","status","ref"])
    import datetime
    for r in rows:
        w.writerow([datetime.datetime.fromtimestamp(r[0]).isoformat(),r[1],r[2],r[3],r[4],r[5]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=statement.csv"})

@app.route("/api/account/can-statement")
def can_statement():
    import sqlite3
    from flask import session, jsonify
    uid=str(session.get("user_id") or session.get("uid") or "guest")
    con=sqlite3.connect("codex700.db")
    c=con.execute("SELECT COUNT(*) FROM transactions WHERE user_id=? AND type='deposit'",(uid,)).fetchone()[0]
    con.close()
    if c==0:
        return jsonify({"ok":False,"msg":"You must deposit first to download statement"})
    return jsonify({"ok":True})

@app.route("/api/account/statement")
def api_statement_guard():
    import sqlite3
    from flask import session, jsonify
    uid=str(session.get("user_id") or session.get("uid") or "guest")
    con=sqlite3.connect("codex700.db")
    c=con.execute("SELECT COUNT(*) FROM transactions WHERE user_id=? AND type='deposit'",(uid,)).fetchone()[0]
    con.close()
    if c==0:
        return jsonify({"ok":False,"msg":"You must deposit first to download statement"}),403
    # call original statement logic inline
    import io, datetime
    con=sqlite3.connect("codex700.db")
    rows=con.execute("SELECT created_at,type,title,amount,status,ref FROM transactions WHERE user_id=? ORDER BY id DESC",(uid,)).fetchall()
    con.close()
    out=io.StringIO(); import csv; w=csv.writer(out); w.writerow(["date","type","title","amount","status","ref"])
    for r in rows:
        w.writerow([datetime.datetime.fromtimestamp(r[0]).isoformat(),r[1],r[2],r[3],r[4],r[5]])
    from flask import Response
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=statement.csv"})

@app.route("/raffle")
def raffle_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/raffle.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "raffle".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/referrals")
def referrals_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/referrals.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "referrals".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/invest")
def invest_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/invest.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "invest".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/deposit")
def deposit_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/deposit.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "deposit".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/withdraw")
def withdraw_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/withdraw.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "withdraw".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/daily-check")
def daily_check_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/daily_check.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "daily-check".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/daily_check")
def daily_check_page2_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/daily_check.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "daily_check".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/logout")
def logout_auto():
    from flask import session, redirect
    session.clear()
    return redirect("/register")

@app.route("/register")
def register_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/register.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "register".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/transactions")
def transactions_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/transactions.html")
    if fp.exists():
        return fp.read_text()
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "transactions".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"
