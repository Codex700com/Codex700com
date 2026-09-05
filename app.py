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
S="<meta name='viewport' content='width=device-width,initial-scale=1'><style>*{box-sizing:border-box}body{background:#000;color:#fff;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;padding-bottom:80px;-webkit-font-smoothing:antialiased;letter-spacing:.2px}a{color:inherit;text-decoration:none}.card{background:#0a0a0a;border:1px solid #8a6a00;border-radius:10px;padding:12px;margin:12px;font-size:14px;line-height:1.5;word-break:break-word;text-align:center}.card h2,.card h3{font-weight:800;letter-spacing:.8px;text-transform:uppercase;font-size:15px}.btn{background:#c00;color:#fff;border:none;padding:12px 20px;border-radius:8px;display:inline-block;font-weight:700;letter-spacing:.6px;text-transform:uppercase;font-size:14px}.logo{color:#c00;font-weight:900;font-size:22px;letter-spacing:2px;text-transform:uppercase;font-family:Inter,Arial,sans-serif}input{width:100%;padding:12px;margin:8px 0;background:#111;border:1px solid #d4a017;border-radius:8px;color:#fff;font-size:15px;font-family:Inter,Arial,sans-serif;letter-spacing:.3px}.nav{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333;font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase}.red{color:#c00}.gold{color:#d4a017}</style>"+"<style>.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px}.gbox{background:#0a0a0a;border:1px solid #8a6a00;border-radius:10px;min-height:88px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 4px;font-size:12.5px;line-height:1.25;word-break:normal;overflow-wrap:normal;white-space:normal}.gbox b{font-size:13px}</style>"""
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
def i():
    return redirect("/home") if "uid" in session else redirect("/register")
@app.route("/register",methods=["GET","POST"])
def reg():
 m=""
 if request.method=="POST":
  n=request.form["name"];p=request.form["phone"];pw=request.form["password"];cf=request.form["confirm"];inv=request.form.get("invite","")
  if pw!=cf: m="Wrong information due to passwords do not match"
  else:
   try:
    c=db()
    _ex=c.execute("SELECT id FROM users WHERE name=?",(n,)).fetchone()
    _ex2=c.execute("SELECT id FROM users WHERE phone=?",(p,)).fetchone()
    if _ex: c.close();m="Username already in use. Please choose another name."
    elif _ex2: c.close();m="Wrong information due to phone already registered. Please login."
    else:
     rc=uuid.uuid4().hex[:6].upper();c.execute("INSERT INTO users(name,phone,password,invite,balance,refcode) VALUES(?,?,?,?,0,?)",(n,p,pw,inv,rc));c.commit();c.close();return redirect("/login")
   except: m="Wrong information due to phone already registered"
 return S+"<div class=logo style='text-align:center;margin:20px'>👑 CODEX700</div><div class=card><h2 class=gold style='text-align:center'>REGISTER</h2>"+(f"<p>{m}</p>" if m else "")+"<form method=POST><input name=name placeholder='Enter Name' required><input name=phone placeholder='Enter Phone' required><input name=password type=password placeholder='Enter Password' required><input name=confirm type=password placeholder='Confirm Password' required><input name=invite placeholder='Invitation code'><button class=btn style='width:100%'>REGISTER</button></form><p style='text-align:center'>Have account? <a href='/login' class=gold>Login</a></p></div>"

@app.route("/login",methods=["GET","POST"])
def login():
 m="";ok=False
 if request.method=="POST":
  p=request.form["phone"];pw=request.form["password"];c=db();u=c.execute("SELECT * FROM users WHERE phone=?",(p,)).fetchone()
  uu=c.execute("SELECT * FROM users WHERE phone=? AND password=?",(p,pw)).fetchone();c.close()
  u=uu
  if not uu:
   _c=db();_ex=_c.execute("SELECT id FROM users WHERE phone=?",(p,)).fetchone();_c.close()
   m="Wrong information due to incorrect password. Please try again." if _ex else "Wrong information due to phone number not registered. Please register first."
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
 h+="<div class=grid4>"
 h+="<a href='/wallet'><div class=gbox>Wallet<br><b class=red>UGX "+str(u["balance"])+"</b></div></a>"
 h+="<a href='/investments'><div class=gbox>Invested<br><b class=red>UGX "+str(ti)+"</b></div></a>"
 h+="<a href='/transactions'><div class=gbox>Income<br><b class=red>UGX 0</b></div></a>"
 h+="<a href='/investments'><div class=card>Active<br><b class=red>"+str(ac)+"</b></div></a></div>"
 h+="<div class=card>🎁 Daily Check-In <a class=btn href='/checkin'>Check In →</a></div>"
 h+="<div class=grid4>"
 acts=[("Invest","/invest","📈"),("Deposit","/deposit","💰"),("Withdrawal","/withdraw","💸"),("Referrals","/referrals","👥"),("Transactions","/transactions","📄"),("Raffle","/raffle","🎁"),("Support","/support","🎧"),("Chat","/chat","💬")]
 for nm,lk,ic in acts: h+="<a href='"+lk+"'><div class=gbox>"+ic+"<br>"+nm+"</div></a>"
 h+="</div><a href='/raffle'><div class=card>🏆 <b class=red>RAFFLE DRAW</b><br><span class=btn>View Prizes →</span></div></a>"
 h+="<div class=card><b class=red>INVESTMENT PLANS</b> <a href='/invest' style='float:right'>View All ></a></div><div style='display:flex;gap:8px;overflow:auto;margin:10px'>"
 for pl,amt in [("L1 Plan Lock",500000),("L2 Plan Lock",1000000),("L3 Plan Lock",2000000)]: h+="<a href='/invest'><div class=card style='min-width:140px'><b>"+pl+"</b><br>UGX "+f"{amt:,}"+"</div></a>"
 h+="</div><div class=card>Need Help? <a class=btn href='/support'>Contact Support</a></div>"+N
 return h

@app.route("/menu")
@need
def menu():
 ls=[("Home","/home"),("Invest","/invest"),("Deposit","/deposit"),("Withdrawal","/withdraw"),("Transactions","/transactions"),("Referrals","/referrals"),("Raffle","/raffle"),("About Us","/about"),("Support","/support"),("Chat Manager","/chat"),("Account","/account"),("Logout","/logout")]
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
        from flask import render_template; return render_template(fp.name)
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "raffle".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"




@app.route("/confirm_buy/<pid>")
def confirm_buy(pid):
    from flask import session, redirect
    import sqlite3
    uid=str(session.get("user_id") or session.get("uid") or "guest")
    # price map
    prices={"A1":20000,"A2":100000,"M1":50000,"M2":100000,"M3":250000,"M4":500000,"M5":1000000,"M6":2000000,"M7":5000000,"L1":500000,"L2":1000000,"L3":2000000,"GS1":600000,"GS2":1200000,"GS3":2500000,"J1":800000,"J2":1500000,"J3":3000000}
    price=prices.get(pid,0)
    con=sqlite3.connect("codex700.db")
    con.execute("CREATE TABLE IF NOT EXISTS investments (user_id TEXT, plan TEXT, amount INTEGER, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    # plan purchase limits
    limits={"A1":2,"A2":2,"M1":1,"M2":1,"M3":1,"M4":1,"M5":1,"M6":4,"M7":4}
    cur_cnt=con.execute("SELECT COUNT(*) FROM investments WHERE user_id=? AND plan=?",(uid,pid)).fetchone()[0]
    max_allowed=limits.get(pid, 999)
    if cur_cnt>=max_allowed:
        con.close()
        return f"<h3>Limit reached: {pid} max {max_allowed} per user</h3>"
    # strict balance check - block if no money
    try:
        bal_row=con.execute("SELECT balance FROM users WHERE id=?",(uid,)).fetchone()
        bal=bal_row[0] if bal_row else 0
    except:
        bal=0
    if bal < price:
        con.close()
        return f"""<div style="margin:20px;padding:16px 18px;background:#3d1a1a;border:1px solid #7f2d2d;border-radius:12px;display:flex;justify-content:space-between;align-items:center;font-family:sans-serif">
<div style="color:#f59e0b;font-weight:600;line-height:1.5">Insufficient balance for {pid}.<br>Need UGX {price:,}.</div>
<a href='/deposit' style="background:linear-gradient(180deg,#fbbf24,#f59e0b);color:#000;padding:12px 20px;border-radius:10px;text-decoration:none;font-weight:700;display:flex;align-items:center;gap:8px">💳 Deposit</a>
</div>"""
    try:
        con.execute("UPDATE users SET balance=balance-? WHERE id=?",(price,uid))
    except:
        pass
    from datetime import datetime; _pr,_da,_du=DETAILS.get(pid,(price,0,30)); con.execute("INSERT INTO investments (user_id, plan, amount, daily, duration, created_at, credited) VALUES (?,?,?,?,?,?,0)",(uid,pid,price,_da,_du,datetime.utcnow().isoformat()))
    con.commit(); con.close()
    # plan details for confirmation
    details={"A1":(20000,3000,16,"CODEX A1 PLAN"),"A2":(100000,9000,15,"CODEX A2 PLAN"),
    "M1":(50000,10000,30,"CODEX M1 PLAN"),"M2":(100000,20000,30,"CODEX M2 PLAN"),
    "M3":(250000,50000,30,"CODEX M3 PLAN"),"M4":(500000,100000,30,"CODEX M4 PLAN"),
    "M5":(1000000,200000,30,"CODEX M5 PLAN"),"M6":(2000000,400000,30,"CODEX M6 PLAN"),
    "M7":(5000000,1000000,30,"CODEX M7 PLAN"),
    "L1":(500000,110000,30,"CODEX L1 PLAN LOCK"),"L2":(1000000,220000,30,"CODEX L2 PLAN LOCK"),"L3":(2000000,440000,30,"CODEX L3 PLAN LOCK"),
    "GS1":(600000,132000,30,"CODEX GS1 PLAN"),"GS2":(1200000,264000,30,"CODEX GS2 PLAN"),"GS3":(2500000,550000,30,"CODEX GS3 PLAN"),
    "J1":(800000,176000,30,"CODEX J1 PLAN"),"J2":(1500000,330000,30,"CODEX J2 PLAN"),"J3":(3000000,660000,30,"CODEX J3 PLAN")}
    p_price,p_daily,p_dur,p_name=details.get(pid,(price,0,30,pid))
    p_total=p_daily*p_dur
    return f"""<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
    <body style="margin:0;background:#000;color:#fff;font-family:sans-serif">
    <div style="padding:12px;display:flex;align-items:center;gap:12px"><a href="/home" style="color:#fff;text-decoration:none;font-size:22px">‹</a><div style="flex:1;text-align:center;font-weight:700;letter-spacing:1px">INVESTMENT CONFIRMATION</div><div style="width:22px"></div></div>
    <div style="margin:12px;border:1px solid #333;border-radius:16px;padding:24px;text-align:center;background:#0a0a0a">
    <div style="font-size:80px;color:#22c55e;border:4px solid #22c55e;width:110px;height:110px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto">✓</div>
    <div style="color:#22c55e;font-weight:800;font-size:22px;margin-top:16px">INVESTMENT SUBMITTED!</div>
    <div style="color:#ccc;margin-top:8px">Your investment has been successfully submitted.</div>
    <div style="margin-top:20px;background:#111;border:1px solid #222;border-radius:12px;padding:12px;display:flex;gap:12px;align-items:center;text-align:left">
    <div style="width:90px;height:70px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center">⛏️</div>
    <div><div style="color:#e11d48;font-weight:800">{p_name} 🔒</div><div style="color:#aaa;font-size:13px">High Performance Mining Machine</div></div>
    </div>
    <div style="margin-top:16px;background:#111;border:1px solid #222;border-radius:12px;padding:6px 16px;text-align:left">
    <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #222"><span>💰 Investment Amount</span><b style="color:#e11d48">UGX {p_price:,}</b></div>
    <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #222"><span>📈 Daily Return</span><b style="color:#e11d48">UGX {p_daily:,}</b></div>
    <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #222"><span>📅 Duration</span><b style="color:#e11d48">{p_dur} Days</b></div>
    <div style="display:flex;justify-content:space-between;padding:12px 0"><span>◑ Total Return</span><b style="color:#e11d48">UGX {p_total:,}</b></div>
    </div>
    <a href="/home" style="display:block;margin-top:20px;background:#e11d48;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:700">Back Home</a>
    </div></body></html>"""

@app.route("/buy/<pid>")
def buy_detail(pid):
    return f"""
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:sans-serif;margin:0;background:#fff;padding-bottom:80px}}
.top img{{width:100%;height:280px;object-fit:cover}}
.card{{padding:15px}}
.price{{color:#e11d48;font-size:22px;font-weight:bold}}
.name{{font-size:18px;font-weight:bold;margin:5px 0}}
.meta{{display:flex;justify-content:space-between;color:#666;font-size:13px;margin:10px 0}}
.box{{background:#f8f8f8;border-radius:10px;padding:12px;margin-top:10px}}
.row{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;font-size:14px}}
.row span{{color:#333}}.row b{{color:#111}}
.btn{{position:fixed;bottom:0;left:0;right:0;background:#e11d48;color:#fff;text-align:center;padding:16px;font-weight:bold;font-size:16px;text-decoration:none}}
</style></head><body>
<div class="top" style="height:210px;overflow:hidden;background:#111"><img src="/static/miner.jpg" style="width:100%;height:300px;object-fit:cover;object-position:bottom;margin-top:-80px;display:block"></div>
<div class="card">
<div class="name">{pid} Plan</div>
<div class="price" id="price">UGX...</div>
<div class="meta"><span>ROI <b id="roi" style="color:#e11d48"></b></span><span>Sold <b>78%</b></span></div>
<div class="box" id="details"></div>
</div>
<a class="btn" id="buybtn" href="#">Invest Now</a>
<script>
const D={{"A":[["A1",20000,3000,16],["A2",100000,9000,15]],"M":[["M1",50000,10000],["M2",100000,20000],["M3",250000,50000],["M4",500000,100000],["M5",1000000,200000],["M6",2000000,400000],["M7",5000000,1000000]],"L":[["L1",500000,110000],["L2",1000000,220000],["L3",2000000,440000]],"GS":[["GS1",600000,132000],["GS2",1200000,264000],["GS3",2500000,550000]],"J":[["J1",800000,176000],["J2",1500000,330000],["J3",3000000,660000]]}};
let pid="{pid}";
let found=null,cat="";
for(let k in D){{ D[k].forEach(x=>{{ if(x[0]==pid){{found=x;cat=k}} }}) }}
if(found){{
 let price=found[1],daily=found[2],dur=found[3]||30,total=daily*dur;
 let roi=Math.round(total/price*100);
 document.getElementById('price').innerText='UGX '+price.toLocaleString();
 document.getElementById('roi').innerText=roi+'%';
 document.getElementById('details').innerHTML=
 `<div class="row"><span>Lock-up period</span><b>${{dur}} day</b></div>`+
 `<div class="row"><span>Daily income</span><b>UGX ${{daily.toLocaleString()}}</b></div>`+
 `<div class="row"><span>Total income</span><b>UGX ${{total.toLocaleString()}}</b></div>`+
 `<div class="row"><span>Min quantity</span><b>1</b></div>`+
 `<div class="row"><span>Max quantity</span><b>2</b></div>`+
 `<div class="row"><span>Raffle tickets</span><b>1</b></div>`+
 `<div class="row"><span>Category</span><b>CODEX ${{cat}} SERIES</b></div>`+
 `<div class="row"><span>Sale</span><b>On sale</b></div>`+
 `<div class="row"><span>VIP required</span><b>VIP0</b></div>`;
 document.getElementById('buybtn').href='/confirm_buy/'+pid;
}}
</script></body></html>
"""

@app.route("/invest")
def invest_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/invest.html")
    if fp.exists():
        from flask import render_template; return render_template(fp.name)
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "invest".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/deposit")
def deposit_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/deposit.html")
    if fp.exists():
        from flask import render_template; return render_template(fp.name)
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "deposit".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "withdraw".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/daily-check")
def daily_check_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/daily_check.html")
    if fp.exists():
        from flask import render_template; return render_template(fp.name)
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "daily-check".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/daily_check")
def daily_check_page2_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/daily_check.html")
    if fp.exists():
        from flask import render_template; return render_template(fp.name)
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
        from flask import render_template; return render_template(fp.name)
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "register".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/transactions")
def transactions_page_auto():
    import pathlib
    # try template, else simple placeholder so no more 404
    fp = pathlib.Path("templates/transactions.html")
    if fp.exists():
        from flask import render_template; return render_template(fp.name)
    return "<h2 style='font-family:sans-serif;padding:20px'>"+ "transactions".title() + " page coming - route fixed, no more 404</h2><a href='/home'>Back Home</a>"

@app.route("/withdraw")
def withdraw_fixed():
    from flask import render_template, session
    bal = session.get("balance", 0)
    return render_template("withdraw.html", balance=bal)

@app.route("/referrals")
def referrals_page():
 from flask import render_template, request
 import hashlib
 uid=request.args.get("user") or "guest"
 code=hashlib.md5(uid.encode()).hexdigest()[:6].upper()
 link="https://codex700com.onrender.com/register?ref="+code
 return render_template("referrals.html",code=code,link=link,total=0,active=0,earnings=0,month_earnings=0,referrals=[],lv1=0,lv2=0,lv3=0)


@app.route("/about")
def about():
    h="<div class=card><h3>About Us</h3><p><b>Codex Company Kampala, Uganda</b> helps you attain <b>financial power and vision</b>.</p><p>Led by <b>CEO Tamale Imran</b> and the Codex Management Team.</p><p><b>Mission:</b> Make wealth simple for Ugandans.<br><b>Vision:</b> Financial freedom for every family.</p><p>📍 Kampala, Uganda<br>✅ Secure investments<br>✅ Fast payments<br>✅ 24/7 Support</p><p><a href='/menu'>Back to Menu</a></p></div>"
    return S+hdr()+h+N
@app.route("/support")
def support_page():
 from flask import render_template
 return render_template("support.html")


import os, json, datetime
CHAT_FILE="chat.json"
if not os.path.exists(CHAT_FILE):
    open(CHAT_FILE,"w").write("[]")

@app.route("/chat")
def chat_page():
    from flask import render_template
    return render_template("chat.html")

@app.route("/api/chat", methods=["GET","POST"])
def api_chat():
    from flask import request, jsonify
    if request.method=="POST":
        data=request.get_json(force=True)
        text=data.get("text","")[:1000]
        user=data.get("user","Anonymous")[:30]
        if not text.strip():
            return jsonify({"ok":False})
        msgs=json.load(open(CHAT_FILE))
        msgs.append({"user":user,"text":text,"time":datetime.datetime.now().strftime("%H:%M")})
        msgs=msgs[-200:]
        json.dump(msgs, open(CHAT_FILE,"w"))
        return jsonify({"ok":True})
    return json.load(open(CHAT_FILE))


CHECKIN_REWARD=500
def ensure_daily_checkin(con):
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkin (user_id INTEGER PRIMARY KEY, last_check TEXT)")
    con.commit()

@app.route("/checkin", methods=["GET","POST"])
def checkin_page():
    from datetime import datetime, timedelta
    uid=session.get("uid")
    if not uid: return redirect("/login")
    con=db(); ensure_daily_checkin(con)
    row=con.execute("SELECT last_check FROM daily_checkin WHERE user_id=?",(uid,)).fetchone()
    now=datetime.utcnow()
    last=None
    if row and row[0]:
        try: last=datetime.fromisoformat(row[0])
        except: pass
    can = (last is None) or (now-last>=timedelta(hours=24))
    msg=""
    if request.method=="POST":
        if can:
            con.execute("INSERT OR REPLACE INTO daily_checkin (user_id,last_check) VALUES (?,?)",(uid,now.isoformat()))
            con.execute("UPDATE users SET balance=balance+? WHERE id=?",(CHECKIN_REWARD,uid))
            con.commit(); last=now; can=False
            msg=f"<div style='background:#052e16;border:1px solid #16a34a;color:#22c55e;padding:12px;border-radius:10px;margin:12px;text-align:center;font-weight:700'>Successfully checked in! UGX {CHECKIN_REWARD:,} added.</div>"
        else:
            msg="<div style='margin:12px;text-align:center;color:#f59e0b'>Already checked in.</div>"
    rem = f"new Date(new Date('{last.isoformat()}').getTime()+24*3600000)" if (last and not can) else "null"
    con.close()
    return f"""<html><head><meta name='viewport' content='width=device-width,initial-scale=1'></head><body style='margin:0;background:#000;color:#fff;font-family:sans-serif;text-align:center'><div style='padding:14px;font-weight:800'>DAILY CHECK-IN</div>{msg}<div style='margin:20px;border:1px solid #222;border-radius:16px;padding:30px;background:#0a0a0a'><div style='font-size:60px'>📅</div><div>Reward: <b style='color:#e11d48'>UGX {CHECKIN_REWARD:,}</b></div><div id='tm' style='color:#f59e0b;font-weight:800;margin:12px;font-size:20px'></div><form method='POST'><button {"disabled" if not can else ""} style='background:{'#e11d48' if can else '#333'};color:#fff;border:0;padding:14px 40px;border-radius:10px;font-weight:800'>{"Check In Now" if can else "Checked In"}</button></form><div style='color:#666;font-size:13px'>No check-in = no reward.<br>Timer resets each check-in.</div></div><a href='/home' style='color:#e11d48'>Back</a><script>let end={rem};function tick(){{let e=document.getElementById('tm');if(!end){{e.innerText='Ready!';return;}}let d=end-new Date();if(d<=0){{e.innerText='Ready! Refresh.';return;}}let h=Math.floor(d/3600000),m=Math.floor(d%3600000/60000),s=Math.floor(d%60000/1000);e.innerText=h+'h '+m+'m '+s+'s';}}setInterval(tick,1000);tick();</script></body></html>"""


@app.route("/investments")
def investments_page():
    from flask import session, redirect
    if "uid" not in session: return redirect("/login")
    con=db()
    rows=con.execute("SELECT plan,amount,date FROM investments WHERE user_id=? ORDER BY rowid DESC",(session["uid"],)).fetchall()
    con.close()
    h="<div class=card><h3>My Investments</h3>"
    if not rows:
        h+="<p>No active investments yet.<br><a class=btn href='/invest'>Invest Now →</a></p>"
    else:
        for pl,amt,dt in rows:
            h+=f"<div class=card>📈 <b>{pl}</b><br>UGX {amt:,}<br><small>{dt}</small></div>"
    h+="</div>"
    return S+hdr()+h+N

if __name__=="__main__":
    print("Starting on http://127.0.0.1:5000/")
    app.run(host="127.0.0.1", port=5000, debug=True)