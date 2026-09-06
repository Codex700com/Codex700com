from flask import Flask,request,redirect,session
import sqlite3,datetime,uuid
app=Flask(__name__);app.secret_key="codex700secret"
try:
 from admin_panel import admin_bp
 app.register_blueprint(admin_bp)
 print('admin wired')
except Exception as e:
 print('admin wire fail',e)

def ensure_admin_column():
    import sqlite3
    try:
        con=sqlite3.connect("codex700.db")
        cols=[r[1] for r in con.execute("PRAGMA table_info(users)")]
        if "is_admin" not in cols:
            con.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        con.execute("UPDATE users SET is_admin=1 WHERE id=1")
        con.commit()
        con.close()
    except Exception as e:
        print("admin mig failed:", e)
ensure_admin_column()

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
S="<meta name='viewport' content='width=device-width,initial-scale=1'><style>*{box-sizing:border-box}body{background:#000;color:#fff;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;padding-bottom:80px;-webkit-font-smoothing:antialiased;letter-spacing:.2px}a{color:inherit;text-decoration:none}.card{background:#0a0a0a;border:1px solid #0a84ff;border-radius:10px;padding:12px;margin:12px;font-size:14px;line-height:1.5;word-break:break-word;text-align:center}.card h2,.card h3{font-weight:800;letter-spacing:.8px;text-transform:uppercase;font-size:15px}.btn{background:linear-gradient(180deg,#29b6ff,#0a84ff);color:#fff;border:none;padding:12px 20px;border-radius:8px;display:inline-block;font-weight:700;letter-spacing:.6px;text-transform:uppercase;font-size:14px}.logo{color:#1da1f2;font-weight:900;font-size:22px;letter-spacing:2px;text-transform:uppercase;font-family:Inter,Arial,sans-serif}input{width:100%;padding:12px;margin:8px 0;background:#111;border:1px solid #0a84ff;border-radius:8px;color:#fff;font-size:15px;font-family:Inter,Arial,sans-serif;letter-spacing:.3px}.nav{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333;font-size:11px;font-weight:600;letter-spacing:.5px;text-transform:uppercase}.red{color:#1da1f2}.gold{color:#0a84ff}</style>"+"<style>.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px}.gbox{color:#fff !important;background:linear-gradient(180deg,#1da1f2,#0a84ff);border:1px solid #0a84ff;border-radius:12px;height:84px;min-height:84px;max-height:84px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:6px 2px;font-size:12px;font-weight:800;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.gbox b{font-size:13px}</style>"""
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
 nm=u["name"].upper(); bal=f"{u['balance']:,}"; tiv=f"{ti:,}"
 h="""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><style>
 *{box-sizing:border-box}body{margin:0;background:#020a24;color:#fff;font-family:Inter,system-ui,Arial;padding-bottom:110px}
 .top{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:#020a24;position:sticky;top:0;z-index:5}
 .logo{text-align:center;line-height:1}.logo b{font-size:32px;color:#ffcc00;letter-spacing:2px}.logo span{font-size:10px;letter-spacing:4px;color:#fff}
 .hero{margin:8px 10px;border:2px solid #1e90ff;border-radius:16px;padding:16px;background:radial-gradient(circle at 80% 20%,#0a4fff33,#020a24 60%),linear-gradient(135deg,#062a7a,#020a24);position:relative;overflow:hidden;box-shadow:0 0 20px #1e90ff55}
 .hero h4{margin:0;font-weight:600;color:#dbeafe}.hero h2{margin:4px 0;color:#00cfff;font-size:28px}.hero p{margin:6px 0;color:#cbd5e1}.hero i{color:#ffcc00}
 .btn-gold{display:inline-block;background:linear-gradient(180deg,#ffdf6b,#ffb700);color:#000;font-weight:900;padding:12px 32px;border-radius:30px;text-decoration:none;margin-top:10px;box-shadow:0 4px 12px #ffb70066}
 .globe{position:absolute;right:10px;top:10px;width:110px;height:110px;background:radial-gradient(circle,#1e90ff88,transparent);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;color:#ffcc00;font-weight:900;text-align:center}
 .stats{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin:10px}
 .sbox{background:linear-gradient(180deg,#0a2f8a,#041a5a);border:1.5px solid #1e90ff;border-radius:14px;padding:12px 4px;text-align:center;box-shadow:0 0 12px #1e90ff44}
 .sbox div{font-size:22px}.sbox b{font-size:13px}.sbox span{color:#00cfff;font-weight:800}
 .banner{margin:10px;border:1.5px solid #ffcc00;border-radius:14px;padding:12px;display:flex;align-items:center;justify-content:space-between;background:linear-gradient(90deg,#0a2a7a,#020a24)}
 .banner small{color:#cbd5e1}.btn-blue{background:#1e90ff;color:#fff;padding:10px 18px;border-radius:25px;text-decoration:none;font-weight:800}
 .grid{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin:10px}
 .card2{background:linear-gradient(180deg,#0a2f8a,#041a5a);border:1.5px solid #1e90ff;border-radius:14px;padding:14px 6px;text-align:center;text-decoration:none;color:#fff}
 .card2 small{color:#7dd3fc;font-size:11px}.card2 b{font-size:14px}
 .card2.gold{background:linear-gradient(180deg,#8a6d00,#5a4500);border-color:#ffcc00;box-shadow:0 0 15px #ffcc0088}
 .nav{position:fixed;bottom:0;left:0;right:0;background:#020a24;border-top:1px solid #1e90ff55;display:flex;padding:8px 0}
 .nav a{flex:1;text-align:center;color:#8aa0b8;text-decoration:none;font-size:10px}.nav a.on{color:#ffcc00}
 .foot{text-align:center;color:#00cfff;font-style:italic;margin:12px}
 </style></head><body>
 <div class="top"><a href="/menu" style="font-size:28px;color:#ffcc00;text-decoration:none">☰</a><div class="logo"><b>CODEX</b><br><span>INVEST • GROW • WIN</span></div><div style="font-size:22px"><a href="/notifications" style="text-decoration:none">🔔</a> <a href="/account" style="text-decoration:none">👤</a></div></div>
 <div class="hero"><h4>👑 WELCOME BACK,</h4><h2>"""+nm+"""</h2><p>Big dreams require action.<br><i>You're one step closer to freedom!</i></p><a class="btn-gold" href="/invest">↗ INVEST NOW →</a><div class="globe">INVEST<br>TODAY<br>BUILD<br>TOMORROW</div></div>
 <div class="stats">
 <div class="sbox"><div>💼</div><b>Wallet</b><br><span>UGX """+bal+"""</span></div>
 <div class="sbox"><div>🪙</div><b>Invested</b><br><span>UGX """+tiv+"""</span></div>
 <div class="sbox"><div>💰</div><b>Income</b><br><span>UGX 0</span></div>
 <div class="sbox"><div>📈</div><b>Active</b><br><span>"""+str(ac)+"""</span></div></div>
 <div class="banner"><div>🎁 <b style="color:#ffcc00">Daily Check-In</b><br><small>Log in daily and win rewards!</small></div><a class="btn-blue" href="/checkin">📅 CHECK IN →</a></div>
 <div class="grid">
 <a class="card2" href="/invest">📈<br><b>Invest</b><br><small>Start your journey</small></a>
 <a class="card2" href="/deposit">💲<br><b>Deposit</b><br><small>Fund your wallet</small></a>
 <a class="card2 gold" href="/withdraw">💼<br><b>Withdraw</b><br><small>Get your earnings</small></a>
 <a class="card2" href="/referrals">👥<br><b>Referral</b><br><small>Earn together</small></a>
 <a class="card2" href="/transactions">🧾<br><b>Transactions</b><br><small>View all records</small></a>
 <a class="card2" href="/raffle">🎁<br><b>Raffle</b><br><small>Win amazing prizes</small></a>
 <a class="card2" href="/support">🎧<br><b>Support</b><br><small>We are here to help</small></a>
 <a class="card2" href="/chat">💬<br><b>Chat</b><br><small>Talk to manager</small></a>
 </div>
 <div class="banner"><div>🏆 <b style="color:#ffcc00">RAFFLE DRAW</b><br><small>More deposits = More chances = Bigger prizes!</small></div><a class="btn-blue" href="/raffle">🎁 VIEW PRIZES →</a></div>
 <div class="foot">Your Success is Our Priority</div>
 <div class="nav"><a href="/home" class="on">🏠<br>HOME</a><a href="/invest">📊<br>INVEST</a><a href="/transactions">⇄<br>TRANSACTIONS</a><a href="/referrals">👥<br>REFERRALS</a><a href="/account">👤<br>ACCOUNT</a></div>
 </body></html>"""
 return h

@app.route("/menu")
@need
def menu():
 ls=[("Home","/home"),("Invest","/invest"),("Deposit","/deposit"),("Withdrawal","/withdraw"),("Transactions","/transactions"),("Referrals","/referrals"),("Raffle","/raffle"),("About Us","/about"),("Support","/support"),("Chat Manager","/chat"),("Account","/account"),("Logout","/logout")]
 try:
  import sqlite3
  _u=session.get("uid") or session.get("uid")
  _c=sqlite3.connect("codex700.db"); _c.row_factory=sqlite3.Row
  _me=_c.execute("SELECT is_admin FROM users WHERE id=?",(_u,)).fetchone(); _c.close()

 except: pass
 h=S+hdr()+"<div class=card><h3>Menu</h3>"
 try:
  _adm=False
  import sqlite3 as _sq
  _cc=_sq.connect("codex700.db"); _cc.row_factory=_sq.Row
  _row=_cc.execute("SELECT is_admin FROM users WHERE id=?",(session.get("uid"),)).fetchone(); _cc.close()
  if _row and _row["is_admin"]==1: ls.insert(len(ls)-1,("Admin Panel","/admin/"))
 except: pass
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
    uid=session.get("uid") or session.get("uid")
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
    con.execute("UPDATE users SET lang=? WHERE id=?",(l, session.get("uid") or session.get("uid")))
    con.commit(); con.close()
    return jsonify({"ok":True})

@app.route("/api/account/notif", methods=["POST"])
def api_notif():
    import sqlite3
    from flask import session, request, jsonify
    m=1 if request.get_json().get("muted") else 0
    con=sqlite3.connect("codex700.db")
    con.execute("UPDATE users SET notif_muted=? WHERE id=?",(m, session.get("uid") or session.get("uid")))
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
    con.execute("UPDATE users SET password=? WHERE id=?",(h, session.get("uid") or session.get("uid")))
    con.commit(); con.close()
    return jsonify({"msg":"Password changed successfully"})

@app.route("/api/account/reset", methods=["POST"])
def api_reset():
    return __import__("flask").jsonify({"msg":"Reset link sent to your email"})

@app.route("/api/account/statement")
def api_statement():
    import sqlite3, csv, io
    from flask import session, Response
    uid=str(session.get("uid") or session.get("uid") or "guest")
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
    uid=str(session.get("uid") or session.get("uid") or "guest")
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
    uid=str(session.get("uid") or session.get("uid") or "guest")
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
    uid=str(session.get("uid") or session.get("uid") or "guest")
    # price map
    prices={"A1":20000,"A2":100000,"M1":50000,"M2":100000,"M3":250000,"M4":500000,"M5":1000000,"M6":2000000,"M7":5000000,"L1":500000,"L2":1000000,"L3":2000000,"GS1":600000,"GS2":1200000,"GS3":2500000,"J1":800000,"J2":1500000,"J3":3000000,"K1":100000,"K2":5000000}
    price=prices.get(pid,0)
    con=sqlite3.connect("codex700.db")
    con.execute("CREATE TABLE IF NOT EXISTS investments (user_id TEXT, plan TEXT, amount INTEGER, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
    # plan purchase limits
    limits={"A1":2,"A2":2,"M1":1,"M2":1,"M3":1,"M4":1,"M5":1,"M6":4,"M7":4,"K1":1,"K2":1}
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
<div style="color:#1da1f2;font-weight:600;line-height:1.5">Insufficient balance for {pid}.<br>Need UGX {price:,}.</div>
<a href='/deposit' style="background:linear-gradient(180deg,#1da1f2,#1da1f2);color:#000;padding:12px 20px;border-radius:10px;text-decoration:none;font-weight:700;display:flex;align-items:center;gap:8px">💳 Deposit</a>
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
    "J1":(800000,176000,30,"CODEX J1 PLAN"),"J2":(1500000,330000,30,"CODEX J2 PLAN"),"K1":(1000000,500000,3,"CODEX K1 PLAN"),"K2":(5000000,2500000,3,"CODEX K2 PLAN"),"J3":(3000000,660000,30,"CODEX J3 PLAN")}
    p_price,p_daily,p_dur,p_name=details.get(pid,(price,0,30,pid))
    p_total=p_daily*p_dur
    return f"""<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
/* SHINING GOLD THEME */
body{background:#000!important;color:#f5d67b!important}
.card,.gbox{
  background:#0a0a0a!important;
  border:1px solid #1da1f2!important;
  border-radius:14px!important;
  box-shadow:0 0 12px rgba(251,191,36,0.55),0 0 28px rgba(251,191,36,0.18),inset 0 0 8px rgba(251,191,36,0.12)!important;
  color:#ffffff!important;
}
.gbox b,.card b{
  color:#1da1f2!important;
  text-shadow:0 0 8px rgba(251,191,36,0.9)!important;
  font-weight:800!important;
}
a{color:#1da1f2!important}
button,.btn{
  background:linear-gradient(180deg,#ffffff,#1da1f2)!important;
  color:#000!important;
  border:none!important;
  box-shadow:0 0 15px rgba(251,191,36,0.7)!important;
  font-weight:800!important;
  border-radius:10px!important;
}
h1,h2,h3{color:#ffffff!important;text-shadow:0 0 12px rgba(251,191,36,0.6)!important}
.grid4 .gbox{height:88px;min-height:88px}
</style>
</head>
    <body style="margin:0;background:#000;color:#fff;font-family:sans-serif">
    <div style="padding:12px;display:flex;align-items:center;gap:12px"><a href="/home" style="color:#fff;text-decoration:none;font-size:22px">‹</a><div style="flex:1;text-align:center;font-weight:700;letter-spacing:1px">INVESTMENT CONFIRMATION</div><div style="width:22px"></div></div>
    <div style="margin:12px;border:1px solid #333;border-radius:16px;padding:24px;text-align:center;background:#0a0a0a">
    <div style="font-size:80px;color:#22c55e;border:4px solid #22c55e;width:110px;height:110px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto">✓</div>
    <div style="color:#22c55e;font-weight:800;font-size:22px;margin-top:16px">INVESTMENT SUBMITTED!</div>
    <div style="color:#ccc;margin-top:8px">Your investment has been successfully submitted.</div>
    <div style="margin-top:20px;background:#111;border:1px solid #222;border-radius:12px;padding:12px;display:flex;gap:12px;align-items:center;text-align:left">
    <div style="width:90px;height:70px;background:#222;border-radius:8px;display:flex;align-items:center;justify-content:center">⛏️</div>
    <div><div style="color:#1da1f2;font-weight:800">{p_name} 🔒</div><div style="color:#aaa;font-size:13px">High Performance Mining Machine</div></div>
    </div>
    <div style="margin-top:16px;background:#111;border:1px solid #222;border-radius:12px;padding:6px 16px;text-align:left">
    <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #222"><span>💰 Investment Amount</span><b style="color:#1da1f2">UGX {p_price:,}</b></div>
    <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #222"><span>📈 Daily Return</span><b style="color:#1da1f2">UGX {p_daily:,}</b></div>
    <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #222"><span>📅 Duration</span><b style="color:#1da1f2">{p_dur} Days</b></div>
    <div style="display:flex;justify-content:space-between;padding:12px 0"><span>◑ Total Return</span><b style="color:#1da1f2">UGX {p_total:,}</b></div>
    </div>
    <a href="/home" style="display:block;margin-top:20px;background:#1da1f2;color:#fff;padding:14px;border-radius:10px;text-decoration:none;font-weight:700">Back Home</a>
    </div></body></html>"""

@app.route("/buy/<pid>")
def buy_detail(pid):
    return f"""
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:sans-serif;margin:0;background:#fff;padding-bottom:80px}}
.top img{{width:100%;height:280px;object-fit:cover}}
.card{{padding:15px}}
.price{{color:#1da1f2;font-size:22px;font-weight:bold}}
.name{{font-size:18px;font-weight:bold;margin:5px 0}}
.meta{{display:flex;justify-content:space-between;color:#666;font-size:13px;margin:10px 0}}
.box{{background:#f8f8f8;border-radius:10px;padding:12px;margin-top:10px}}
.row{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee;font-size:14px}}
.row span{{color:#333}}.row b{{color:#111}}
.btn{{position:fixed;bottom:0;left:0;right:0;background:#1da1f2;color:#fff;text-align:center;padding:16px;font-weight:bold;font-size:16px;text-decoration:none}}
</style>
<style>
/* SHINING GOLD THEME */
body{background:#000!important;color:#f5d67b!important}
.card,.gbox{
  background:#0a0a0a!important;
  border:1px solid #1da1f2!important;
  border-radius:14px!important;
  box-shadow:0 0 12px rgba(251,191,36,0.55),0 0 28px rgba(251,191,36,0.18),inset 0 0 8px rgba(251,191,36,0.12)!important;
  color:#ffffff!important;
}
.gbox b,.card b{
  color:#1da1f2!important;
  text-shadow:0 0 8px rgba(251,191,36,0.9)!important;
  font-weight:800!important;
}
a{color:#1da1f2!important}
button,.btn{
  background:linear-gradient(180deg,#ffffff,#1da1f2)!important;
  color:#000!important;
  border:none!important;
  box-shadow:0 0 15px rgba(251,191,36,0.7)!important;
  font-weight:800!important;
  border-radius:10px!important;
}
h1,h2,h3{color:#ffffff!important;text-shadow:0 0 12px rgba(251,191,36,0.6)!important}
.grid4 .gbox{height:88px;min-height:88px}
</style>
</head><body>
<div class="top" style="height:210px;overflow:hidden;background:#111"><img src="/static/miner.jpg" style="width:100%;height:300px;object-fit:cover;object-position:bottom;margin-top:-80px;display:block"></div>
<div class="card">
<div class="name">{pid} Plan</div>
<div class="price" id="price">UGX...</div>
<div class="meta"><span>ROI <b id="roi" style="color:#1da1f2"></b></span><span>Sold <b>78%</b></span></div>
<div class="box" id="details"></div>
</div>
<a class="btn" id="buybtn" href="#">Invest Now</a>
<script>
const D={{"A":[["A1",20000,3000,16],["A2",100000,9000,15]],"M":[["M1",50000,10000],["M2",100000,20000],["M3",250000,50000],["M4",500000,100000],["M5",1000000,200000],["M6",2000000,400000],["M7",5000000,1000000]],"L":[["L1",500000,110000],["L2",1000000,220000],["L3",2000000,440000]],"GS":[["GS1",600000,132000],["GS2",1200000,264000],["GS3",2500000,550000]],"J":[["J1",800000,176000],["J2",1500000,330000],["J3",3000000,660000]],"K":[["K1",1000000,500000],["K2",5000000,2500000]]}};
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

@app.route("/product")
def product_page():
    from flask import render_template
    return render_template("product_detail.html")

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
def withdraw():
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


REWARDS=[500,700,1000,1500,2000,3000,5000]
def ensure_daily_checkin(con):
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkin (user_id INTEGER PRIMARY KEY, last_check TEXT, streak INTEGER DEFAULT 0)")
    con.commit()
@app.route("/checkin", methods=["GET","POST"])
def checkin_page():
    from datetime import datetime, timedelta
    uid=session.get("uid")
    if not uid: return redirect("/login")
    con=db(); ensure_daily_checkin(con)
    row=con.execute("SELECT last_check, streak FROM daily_checkin WHERE user_id=?",(uid,)).fetchone()
    now=datetime.utcnow()+timedelta(hours=3)
    today=now.date().isoformat()
    last_check=None; streak=0
    if row and row[0]:
        try:
            last_check=datetime.fromisoformat(row[0]); streak=row[1] or 0
        except: pass
    last_date=last_check.date().isoformat() if last_check else None
    claimed=(last_date==today)
    if claimed:
        cur_day=streak or 1; can=False
    else:
        cur_day=streak+1 if (last_check and (now.date()-last_check.date()).days==1) else 1
        cur_day=((cur_day-1)%7)+1
        can=True
    reward=[500,700,1000,1500,2000,3000,5000][(cur_day-1)%7]
    if request.method=="POST" and can:
        con.execute("INSERT OR REPLACE INTO daily_checkin (user_id,last_check,streak) VALUES (?,?,?)",(uid,now.isoformat(),cur_day))
        con.execute("UPDATE users SET balance=balance+? WHERE id=?",(reward,uid))
        try: con.execute("INSERT INTO transactions(user_id,type,amount,status,created_at) VALUES(?,?,?,?,?)",(uid,"Daily Checkin Day "+str(cur_day),reward,"completed",now.isoformat()))
        except: pass
        con.commit(); claimed=True; can=False; streak=cur_day
    nxt=datetime(now.year,now.month,now.day)+timedelta(days=1)
    secs=int((nxt-now).total_seconds()) if claimed else 0
    cards=""
    for i,amt in enumerate([500,700,1000,1500,2000,3000,5000],1):
        if (claimed and i<=cur_day) or (not claimed and i<cur_day):
            st='<div style="background:#16a34a;color:#fff;font-size:11px;padding:4px 8px;border-radius:12px;margin-top:6px">Claimed</div>'; bo="border:2px solid #00ff66"; bg="background:#052e16"
        elif i==cur_day and can:
            st='<div style="background:#f59e0b;color:#000;font-size:11px;padding:4px 8px;border-radius:12px;margin-top:6px;font-weight:800">Claim</div>'; bo="border:2px solid #f59e0b"; bg="background:#0a0a3a"
        else:
            st='<div style="background:#334155;color:#cbd5e1;font-size:11px;padding:4px 8px;border-radius:12px;margin-top:6px">Pending</div>'; bo="border:1px solid #1e90ff55"; bg="background:#0a1440"
        cards+=f'<div style="flex:1;{bg};{bo};border-radius:12px;padding:8px 4px;text-align:center"><div style="color:#00cfff;font-size:12px">Day {i}</div><div style="font-size:28px">X</div><div style="font-size:11px">UGX {amt:,}</div>{st}</div>'
    claim_html=f'<div style="margin:10px;padding:16px;background:linear-gradient(135deg,#0a3cc0,#00cfff);border-radius:16px;text-align:center"><div>UGX {reward:,}</div><form method="POST"><button style="background:#00c853;color:#fff;padding:14px 18px;border-radius:12px;font-weight:900">CLAIM REWARD</button></form></div>' if can else f'<div style="margin:10px;padding:16px;background:#001a5e;border-radius:16px;text-align:center"><div style="color:#00ff66">CLAIMED</div><div>Next reward in:</div><div id="timer" style="font-size:32px;color:#ffcc00">--:--:--</div><script>let s={secs};function tick(){{let h=Math.floor(s/3600),m=Math.floor(s%3600/60),ss=s%60;document.getElementById("timer").innerText=String(h).padStart(2,"0")+":"+String(m).padStart(2,"0")+":"+String(ss).padStart(2,"0");if(s>0)s--;}};tick();setInterval(tick,1000);</script></div>'
    disp_streak = streak if claimed else cur_day
    elig = "You are eligible to claim your reward!" if can else "You have claimed today. Come back tomorrow!"
    con.close()
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{{margin:0;background:#020a24;color:#fff;font-family:Inter,system-ui,Arial;padding-bottom:90px}}
    .top{{display:flex;align-items:center;justify-content:space-between;padding:12px}}
    .banner{{margin:10px;border-radius:18px;padding:20px;background:linear-gradient(135deg,#0a2a9a,#020a24);border:1px solid #1e90ff55;position:relative;overflow:hidden}}
    .card{{margin:10px;border:1px solid #1e90ff44;border-radius:14px;padding:12px;background:#041338}}
    .bottom{{position:fixed;bottom:0;left:0;right:0;display:flex;background:#020a24;border-top:1px solid #1e90ff33;padding:8px}}
    .bottom a{{flex:1;text-align:center;color:#88aaff;text-decoration:none;font-size:12px}}
    </style></head><body>
    <div class="top"><a href="/home" style="color:#fff;font-size:26px;text-decoration:none">←</a>
    <div style="text-align:center"><b style="font-size:24px;color:#00cfff">👑 CODEX</b><div style="font-size:9px;letter-spacing:3px;color:#88aaff">INVEST • GROW • WIN</div></div><div>🔔 👤</div></div>
    <div class="banner"><div style="font-size:38px;font-weight:900;line-height:1">DAILY<br><span style="color:#ffcc00">CHECK-IN</span></div>
    <div style="color:#00cfff;margin-top:8px">Log in daily, stay active<br>and earn amazing rewards!</div>
    <div style="font-size:55px;margin-top:10px">🎁</div>
    <div style="position:absolute;right:14px;top:16px;text-align:right;color:#00cfff;font-style:italic;line-height:1.4">👑<br>Small Steps<br>Every Day<br>= Big Results</div></div>
    <div class="card" style="display:flex;align-items:center;justify-content:space-between">
    <div>📅 <b>Today's Check-In</b><br><small style="color:#00cfff">{elig}</small></div>
    <div><span style="background:#00c853;color:#fff;padding:6px 14px;border-radius:20px;font-size:13px">✓ Day {cur_day}</span></div>
    <div style="text-align:center">🔥<br><b style="color:#ffcc00">{disp_streak} Day</b><br><small>Streak</small></div></div>
    <div class="card"><div style="display:flex;justify-content:space-between;align-items:center"><b>🎁 7-DAY REWARDS</b><span style="font-size:11px;border:1px solid #ffcc00;padding:4px 8px;border-radius:12px">🔥 Keep streak!</span></div>
    <div style="display:flex;gap:6px;margin-top:10px">"""+cards+"""</div></div>
    """+claim_html+"""
    <div class="card" style="display:flex;gap:12px;align-items:center"><div style="font-size:50px">🏆</div>
    <div><i style="color:#ffcc00;font-size:20px">Stay Consistent!</i><br><small>The more days you check in,<br>the bigger your rewards!</small><br><i style="color:#00cfff;font-size:13px">Discipline Today = Financial Freedom Tomorrow</i></div></div>
    <div class="bottom"><a href="/home">🏠<br>Home</a><a href="/invest">📊<br>Invest</a><a href="/transactions">🔄<br>Transactions</a><a href="/referrals">👥<br>Referrals</a><a href="/account">👤<br>Account</a></div>
    </body></html>"""
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

















@app.route("/api/notifs")
def api_notifs():
    import sqlite3; con=sqlite3.connect("codex700.db"); con.row_factory=sqlite3.Row
    ns=list(con.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 5")); con.close()
    return {"notifs":[dict(n) for n in ns]}







@app.route("/deposit-submit", methods=["POST"])
def deposit_submit():
 import sqlite3, os, time
 from flask import request, session, jsonify
 uid=session.get("uid")
 if not uid:
  return jsonify({"ok":False,"msg":"Please login first"})
 airtel=request.form.get("airtel_number","").strip()
 amount=request.form.get("amount","").strip()
 txid=request.form.get("txid","").strip()
 if not airtel or not amount or not txid:
  return jsonify({"ok":False,"msg":"Fill all fields"})
 try: amt=int(float(amount))
 except: return jsonify({"ok":False,"msg":"Invalid amount"})
 if amt<1000: return jsonify({"ok":False,"msg":"Minimum 1000 UGX"})
 f=request.files.get("screenshot")
 shot_path=""
 if f and f.filename:
  os.makedirs("static/shots", exist_ok=True)
  fn=f"{uid}_{int(time.time())}_{f.filename.replace('/','_')}"
  fp=os.path.join("static/shots", fn)
  f.save(fp); shot_path="/"+fp
 con=sqlite3.connect("codex700.db")
 con.execute("CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY, user_id INT, airtel TEXT, amount INT, txid TEXT, screenshot TEXT, status TEXT DEFAULT 'pending', created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
 # prevent duplicate txid
 cur=con.execute("SELECT id FROM deposits WHERE txid=?",(txid,)).fetchone()
 if cur:
  con.close(); return jsonify({"ok":False,"msg":"This Transaction ID already used"})
 con.execute("INSERT INTO deposits (user_id, airtel, amount, txid, screenshot, status) VALUES (?,?,?,?,?, 'pending')",(uid, airtel, amt, txid, shot_path))
 con.commit(); con.close()
 return jsonify({"ok":True,"msg":"Deposit submitted! Will be reviewed shortly."})












# --- ADMIN PANEL Deep Blue / White ---
if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route("/raffle-buy", methods=["POST"])
def raffle_buy():
    from flask import request, jsonify, session
    import sqlite3, datetime
    data = request.get_json(force=True)
    qty = max(1, int(data.get("qty",1)))
    PRICE=5000
    cost=PRICE*qty
    uid = session.get("uid") or session.get("user_id")
    if not uid:
        return jsonify(ok=False, msg="Please login first")
    con = sqlite3.connect("codex.db")
    # ensure tables exist in codex.db, but balance is in main db - try both
    import glob
    maindb = "codex700.db" if os.path.exists("codex700.db") else "codex.db"
    # use main db connection for balance
    import sqlite3 as s2
    mcon = s2.connect(maindb)
    mcon.row_factory = s2.Row
    u = mcon.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
    bal = u["balance"] if u else 0
    if bal < cost:
        mcon.close(); con.close()
        return jsonify(ok=False, msg=f"Insufficient balance. Need UGX {cost:,}, you have UGX {bal:,}")
    mcon.execute("UPDATE users SET balance=balance-? WHERE id=?", (cost, uid))
    mcon.execute("INSERT INTO transactions(user_id,type,amount,status,date,ref) VALUES(?,?,?,?,?,?)", (uid,"raffle",-cost,"completed",datetime.datetime.now().isoformat(),f"RAFFLE-{qty}"))
    mcon.commit(); mcon.close()
    con.execute("CREATE TABLE IF NOT EXISTS rtickets (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, qty INT, date TEXT)")
    for _ in range(qty):
        con.execute("INSERT INTO rtickets (user_id,qty,date) VALUES (?,?,?)", (str(uid),1,datetime.datetime.now().isoformat()))
    con.commit()
    total = con.execute("SELECT COUNT(*) FROM rtickets WHERE user_id=?", (str(uid),)).fetchone()[0]
    con.close()
    return jsonify(ok=True, msg=f"Purchased {qty} ticket(s) for UGX {cost:,}!", total=total)

@app.route("/raffle-my")
def raffle_my():
    from flask import jsonify, session
    import sqlite3
    uid=str(session.get("uid") or session.get("user_id") or 1)
    con=sqlite3.connect("codex.db")
    con.execute("CREATE TABLE IF NOT EXISTS rtickets (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, qty INT, date TEXT)")
    total=con.execute("SELECT COUNT(*) FROM rtickets WHERE user_id=?", (uid,)).fetchone()[0]
    con.close()
    return jsonify(total=total)

@app.route("/raffle-winners")
def raffle_winners():
    from flask import jsonify
    return jsonify([["Lucky256","iPhone 14","15 Aug 2026"],["Bright001","$500 Cash","01 Aug 2026"]])

@app.route("/set-language", methods=["POST"])
def set_language():
    from flask import request, jsonify, session
    import sqlite3
    d=request.get_json(force=True)
    lang=d.get("lang","en")
    session["lang"]=lang
    uid=session.get("uid") or session.get("user_id")
    if uid:
        try:
            db="codex700.db" if os.path.exists("codex700.db") else "codex.db"
            con=sqlite3.connect(db)
            try: con.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'en'")
            except: pass
            con.execute("UPDATE users SET lang=? WHERE id=?",(lang,uid))
            con.commit(); con.close()
        except Exception as e: print(e)
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
