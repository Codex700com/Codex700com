from flask import Flask,request,redirect,session,render_template
import sqlite3,datetime,uuid
app=Flask(__name__);app.secret_key="codex700secret"
try:
 from admin_panel import admin_bp
 app.register_blueprint(admin_bp)
 print('admin wired')
except Exception as e:
 print('admin wire fail',e)


def ensure_invest_columns():
    import sqlite3, time
    con=sqlite3.connect("codex700.db")
    try:
        cols=[r[1] for r in con.execute("PRAGMA table_info(investments)")]
        for col, typ in [("daily_return","INTEGER DEFAULT 0"),("duration_days","INTEGER DEFAULT 30"),
                         ("purchase_ts","INTEGER DEFAULT 0"),("expiry_ts","INTEGER DEFAULT 0"),
                         ("img","TEXT DEFAULT ''"),("product_name","TEXT DEFAULT ''"),
                         ("credited_days","INTEGER DEFAULT 0"),("total_expected","INTEGER DEFAULT 0")]:
            if col not in cols:
                con.execute(f"ALTER TABLE investments ADD COLUMN {col} {typ}")
        con.commit()
    except Exception as e: print("migrate invest fail",e)
    con.close()
ensure_invest_columns()

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
N="<div class=nav><a href='/home'><div>🏠<br>Home</div></a><a href='/invest'><div>📈<br>Invest</div></a><a href='/my-investments'><div>💼<br>My Invest</div></a><a href='/transactions'><div>⇄<br>Transactions</div></a><a href='/referrals'><div>👥<br>Referrals</div></a><a href='/account'><div>👤<br>Account</div></a></div>"
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
    inc=c.execute("SELECT COALESCE(SUM(amount),0) s FROM transactions WHERE user_id=? AND type IN ('earn','referral','checkin','daily_return')",(u["id"],)).fetchone()["s"]
    c.close()
    def fmt(x):
        try:
            return f"{int(x or 0):,}"
        except:
            return "0"
    return render_template('home.html', user_name=u["name"].upper(), wallet_balance=fmt(u['balance']), total_invested=fmt(ti), total_income=fmt(inc), active_count=ac)

@app.route("/menu")
@need
def menu():
 ls=[("Home","/home"),("Invest","/invest"),("My Investments","/my-investments"),("Deposit","/deposit"),("Withdrawal","/withdraw"),("Transactions","/transactions"),("Referrals","/referrals"),("Raffle","/raffle"),("About Us","/about"),("Support","/support"),("Chat Manager","/chat"),("Account","/account"),("Logout","/logout")]
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
    import sqlite3, datetime
    from flask import session, render_template
    uid=session.get('uid')
    con=sqlite3.connect("codex700.db"); con.row_factory=sqlite3.Row
    u=con.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone() if uid else None
    if not u:
        return render_template("account.html",
            user_name="Guest", member_id="CDX000000",
            wallet_balance="0", total_invested_f="0",
            total_income_f="0", active_investments=0,
            lang_name="English")
    # totals
    try:
        rows=con.execute("SELECT type,amount FROM transactions WHERE user_id=?",(str(uid),)).fetchall()
    except: rows=[]
    inv=sum(-r["amount"] for r in rows if r["type"]=="invest" and r["amount"]<0)
    inc=sum(r["amount"] for r in rows if r["type"] in ("earn","referral","checkin","daily_return") and r["amount"]>0)
    try:
        act=con.execute("SELECT COUNT(*) FROM investments WHERE user_id=? AND active=1",(uid,)).fetchone()[0]
    except: act=0
    con.close()
    def fmt(n): return "{:,}".format(int(n or 0))
    # get name safely
    uname = u["name"] if "name" in u.keys() else u["phone"] if "phone" in u.keys() else "User"
    mid = u["member_id"] if "member_id" in u.keys() and u["member_id"] else f"CDX{str(uid).zfill(6)}"
    bal = u["balance"] if "balance" in u.keys() else 0
    return render_template("account.html",
        user_name=uname, member_id=mid,
        wallet_balance=fmt(bal), total_invested_f=fmt(inv),
        total_income_f=fmt(inc), active_investments=act,
        lang_name="English")

@app.route("/api/account")
def api_account():
    import sqlite3, datetime
    from flask import session, jsonify
    uid=session.get("uid") or session.get("user_id") or session.get("uid")
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





# --- AUTO-MIGRATE OLD DB FOR PERSISTENT TIMER ---
try:
    import sqlite3
    _c=sqlite3.connect("codex700.db")
    for _q in ["ALTER TABLE investments ADD COLUMN daily INTEGER","ALTER TABLE investments ADD COLUMN duration INTEGER","ALTER TABLE investments ADD COLUMN created_at TEXT","ALTER TABLE investments ADD COLUMN end_at TEXT","ALTER TABLE investments ADD COLUMN credited INTEGER DEFAULT 0","ALTER TABLE investments ADD COLUMN status TEXT DEFAULT 'active'"]:
        try: _c.execute(_q)
        except: pass
    _c.execute("CREATE TABLE IF NOT EXISTS daily_checkins (user_id TEXT PRIMARY KEY, last_claim TEXT, streak INTEGER DEFAULT 0)")
    _c.commit(); _c.close()
except Exception as _e:
    print("migrate err", _e)
# --- END MIGRATE ---


@app.route("/confirm_buy/<pid>")
def confirm_buy(pid):
    from flask import session, redirect
    import sqlite3
    uid=str(session.get("uid") or session.get("uid") or "guest")
    # price map
    prices={"A1":20000,"A2":100000,"M1":50000,"M2":100000,"M3":250000,"M4":500000,"M5":1000000,"M6":2000000,"M7":5000000,"L1":500000,"L2":1000000,"L3":2000000,"GS1":600000,"GS2":1200000,"GS3":2500000,"J1":800000,"J2":1500000,"J3":3000000,"K1":100000,"K2":5000000}
    price=prices.get(pid,0)
    con=sqlite3.connect("codex700.db")
    con.execute("CREATE TABLE IF NOT EXISTS investments (user_id TEXT, plan TEXT, amount INTEGER, daily INTEGER, duration INTEGER, created_at TEXT, end_at TEXT, credited INTEGER DEFAULT 0, status TEXT DEFAULT 'active', ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
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
        details_map={"A1":(20000,3000,16),"A2":(100000,9000,15),"M1":(50000,10000,30),"M2":(100000,20000,30),"M3":(250000,50000,30),"M4":(500000,100000,30),"M5":(1000000,200000,30),"M6":(2000000,400000,30),"M7":(5000000,1000000,30),"L1":(500000,110000,30),"L2":(1000000,220000,30),"L3":(2000000,440000,30),"GS1":(600000,132000,30),"GS2":(1200000,264000,30),"GS3":(2500000,550000,30),"J1":(500000,110000,30),"J2":(1000000,220000,30),"J3":(2000000,440000,30)}
        _pr,_da,_du=details_map.get(pid,(price,0,30))
        _total=_da*_du
        return render_template('invest_fail.html', plan_name=pid, amount=f"{price:,}", balance=f"{bal:,}", daily=f"UGX {_da:,}", duration=str(_du), total=f"UGX {_total:,}", current_balance=bal)
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
 'body{{background:#000!important;color:#f5d67b!important}}'
'.card,.gbox{{'
'background:#0a0a0a!important;'
'border:1px solid #1da1f2!important;'
'border-radius:14px!important;'
'box-shadow:0 0 12px rgba(251,191,36,0.55),0 0 28px rgba(251,191,36,0.18),inset 0 0 8px rgba(251,191,36,0.12)!important;'
'color:#ffffff!important;'
'}}'
'.gbox b,.card b{{'
'color:#1da1f2!important;'
'text-shadow:0 0 8px rgba(251,191,36,0.9)!important;'
'font-weight:800!important;'
'}}'
'a{{color:#1da1f2!important}}'
'button,.btn{{'
'background:linear-gradient(180deg,#ffffff,#1da1f2)!important;'
'color:#000!important;'
'border:none!important;'
'box-shadow:0 0 15px rgba(251,191,36,0.7)!important;'
'font-weight:800!important;'
'border-radius:10px!important;'
'}}'
'h1,h2,h3{{color:#ffffff!important;text-shadow:0 0 12px rgba(251,191,36,0.6)!important}}'
'.grid4 .gbox{{height:88px;min-height:88px}}'
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
    from flask import render_template, request
    plan=request.args.get("p","A2")
    img="miner_k.jpg" if plan.startswith("K") else "miner.jpg"
    return render_template("product_detail.html", plan=plan, img=img)

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
    from flask import render_template, session

    uid = session.get("uid")
    if not uid:
        return redirect("/login")

    con = db()
    rows = []

    # Existing transactions table
    try:
        tx = con.execute(
            "SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC",
            (uid,)
        ).fetchall()

        for r in tx:
            rows.append({
                "type": r["type"] if "type" in r.keys() else "Transaction",
                "amount": r["amount"] if "amount" in r.keys() else 0,
                "status": r["status"] if "status" in r.keys() else "pending",
                "ref": r["ref"] if "ref" in r.keys() else "",
                "date": r["date"] if "date" in r.keys() else ""
            })
    except Exception:
        pass

    # Deposits table
    try:
        deps = con.execute(
            "SELECT * FROM deposits WHERE user_id=? ORDER BY id DESC",
            (uid,)
        ).fetchall()

        for r in deps:
            ref = ""
            if "txid" in r.keys():
                ref = r["txid"] or ""
            elif "txn_id" in r.keys():
                ref = r["txn_id"] or ""

            rows.append({
                "type": "Deposit",
                "amount": r["amount"] if "amount" in r.keys() else 0,
                "status": r["status"] if "status" in r.keys() else "pending",
                "ref": ref,
                "date": (
                    r["created"] if "created" in r.keys()
                    else r["date"] if "date" in r.keys()
                    else ""
                )
            })
    except Exception:
        pass

    # Withdrawals table
    try:
        tables = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        table_names = [x["name"] for x in tables]

        if "withdrawals" in table_names:
            info = con.execute("PRAGMA table_info(withdrawals)").fetchall()
            cols = [x["name"] for x in info]

            user_col = "user_id" if "user_id" in cols else (
                "uid" if "uid" in cols else None
            )

            if user_col:
                wds = con.execute(
                    f"SELECT * FROM withdrawals WHERE {user_col}=? ORDER BY id DESC",
                    (uid,)
                ).fetchall()

                for r in wds:
                    ref = ""
                    for c in ("txid", "txn_id", "ref", "reference"):
                        if c in r.keys() and r[c]:
                            ref = r[c]
                            break

                    rows.append({
                        "type": "Withdrawal",
                        "amount": r["amount"] if "amount" in r.keys() else 0,
                        "status": r["status"] if "status" in r.keys() else "pending",
                        "ref": ref,
                        "date": (
                            r["created"] if "created" in r.keys()
                            else r["date"] if "date" in r.keys()
                            else ""
                        )
                    })
    except Exception:
        pass

    con.close()

    # Newest first
    rows.reverse()

    return render_template("transactions.html", rows=rows)

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

@app.route("/api/my-chat")
def api_my_chat():
 from flask import session, jsonify
 uid=session.get("user_id") or session.get("uid") or session.get("id")
 if not uid: return jsonify([])
 try:
  con=db()
  con.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, admin_reply TEXT, created_at TEXT)")
  rows=con.execute("SELECT id, message as text, admin_reply, created_at FROM messages WHERE user_id=? ORDER BY id ASC",(uid,)).fetchall()
  con.close()
  return jsonify([dict(r) for r in rows])
 except Exception as e:
  print("my-chat error",e)
  return jsonify([])

@app.route("/api/chat", methods=["GET","POST"])
def api_chat():
    from flask import request, jsonify, session
    if request.method=="POST":
        data=request.get_json(force=True)
        text=data.get("text","")[:1000]
        if not text.strip():
            return jsonify({"ok":False})
        user=data.get("user","Anonymous")[:30]
        msgs=json.load(open(CHAT_FILE))
        msgs.append({"user":user,"text":text,"time":datetime.datetime.now().strftime("%H:%M")})
        msgs=msgs[-200:]
        json.dump(msgs, open(CHAT_FILE,"w"))
        try:
            uid=session.get("user_id") or session.get("uid") or session.get("id")
            if uid:
                con=db()
                con.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, admin_reply TEXT, created_at TEXT)")
                con.execute("INSERT INTO messages (user_id, message, created_at) VALUES (?,?,?)",(uid, text.strip(), datetime.datetime.now().isoformat()))
                con.commit(); con.close()
        except Exception as e:
            print("msg save error", e)
        return jsonify({"ok":True})
    # private inbox for logged-in user
    try:
        from flask import session
        uid=session.get("user_id") or session.get("uid") or session.get("id")
        if uid:
            con=db()
            con.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, admin_reply TEXT, created_at TEXT)")
            rows=con.execute("SELECT id, message, admin_reply, created_at FROM messages WHERE user_id=? ORDER BY id ASC LIMIT 100",(uid,)).fetchall()
            con.close()
            return {"private":[dict(r) for r in rows]}
    except Exception as e:
        print("private inbox error",e)
    return json.load(open(CHAT_FILE))


REWARDS=[500,700,1000,1500,2000,3000,5000]
def ensure_daily_checkin(con):
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkin (user_id INTEGER PRIMARY KEY, last_check TEXT, streak INTEGER DEFAULT 0)")
    con.commit()
@app.route("/checkin", methods=["GET","POST"])
def checkin_page():
    from datetime import datetime, timedelta
    uid=session.get("uid") or session.get("user_id")
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
            st='<div style="background:#334155;color:#cbd5e1;font-size:11px;padding:4px 8px;border-radius:12px;margin-top:6px">Pending</div>'; bo="border:1px solid #00b0ff55"; bg="background:#0a1440"
        cards+=f'<div style="flex:1;{bg};{bo};border-radius:12px;padding:8px 4px;text-align:center"><div style="color:#00cfff;font-size:12px">Day {i}</div><div style="font-size:28px">X</div><div style="font-size:11px">UGX {amt:,}</div>{st}</div>'
    claim_html=f'<div style="margin:10px;padding:16px;background:linear-gradient(135deg,#0a3cc0,#00cfff);border-radius:16px;text-align:center"><div>UGX {reward:,}</div><form method="POST"><button style="background:#00c853;color:#fff;padding:14px 18px;border-radius:12px;font-weight:900">CLAIM REWARD</button></form></div>' if can else f'<div style="margin:10px;padding:16px;background:#001a5e;border-radius:16px;text-align:center"><div style="color:#00ff66">CLAIMED</div><div>Next reward in:</div><div id="timer" style="font-size:32px;color:#00b0ff">--:--:--</div><script>let s={secs};function tick(){{let h=Math.floor(s/3600),m=Math.floor(s%3600/60),ss=s%60;document.getElementById("timer").innerText=String(h).padStart(2,"0")+":"+String(m).padStart(2,"0")+":"+String(ss).padStart(2,"0");if(s>0)s--;}};tick();setInterval(tick,1000);</script></div>'
    disp_streak = streak if claimed else cur_day
    elig = "You are eligible to claim your reward!" if can else "You have claimed today. Come back tomorrow!"
    con.close()
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{{margin:0;background:#000000;color:#fff;font-family:Inter,system-ui,Arial;padding-bottom:90px}}
    .top{{display:flex;align-items:center;justify-content:space-between;padding:12px}}
    .banner{{margin:10px;border-radius:18px;padding:20px;background:linear-gradient(135deg,#0a2a9a,#000000);border:1px solid #00b0ff55;position:relative;overflow:hidden}}
    .card{{margin:10px;border:1px solid #00b0ff44;border-radius:14px;padding:12px;background:#041338}}
    .bottom{{position:fixed;bottom:0;left:0;right:0;display:flex;background:#000000;border-top:1px solid #00b0ff33;padding:8px}}
    .bottom a{{flex:1;text-align:center;color:#88aaff;text-decoration:none;font-size:12px}}
    </style></head><body>
    <div class="top"><a href="/home" style="color:#fff;font-size:26px;text-decoration:none">←</a>
    <div style="text-align:center"><b style="font-size:24px;color:#00cfff">👑 CODEX</b><div style="font-size:9px;letter-spacing:3px;color:#88aaff">INVEST • GROW • WIN</div></div><div>🔔 👤</div></div>
    <div class="banner"><div style="font-size:38px;font-weight:900;line-height:1">DAILY<br><span style="color:#00b0ff">CHECK-IN</span></div>
    <div style="color:#00cfff;margin-top:8px">Log in daily, stay active<br>and earn amazing rewards!</div>
    <div style="font-size:55px;margin-top:10px">🎁</div>
    <div style="position:absolute;right:14px;top:16px;text-align:right;color:#00cfff;font-style:italic;line-height:1.4">👑<br>Small Steps<br>Every Day<br>= Big Results</div></div>
    <div class="card" style="display:flex;align-items:center;justify-content:space-between">
    <div>📅 <b>Today's Check-In</b><br><small style="color:#00cfff">{elig}</small></div>
    <div><span style="background:#00c853;color:#fff;padding:6px 14px;border-radius:20px;font-size:13px">✓ Day {cur_day}</span></div>
    <div style="text-align:center">🔥<br><b style="color:#00b0ff">{disp_streak} Day</b><br><small>Streak</small></div></div>
    <div class="card"><div style="display:flex;justify-content:space-between;align-items:center"><b>🎁 7-DAY REWARDS</b><span style="font-size:11px;border:1px solid #00b0ff;padding:4px 8px;border-radius:12px">🔥 Keep streak!</span></div>
    <div style="display:flex;gap:6px;margin-top:10px">"""+cards+"""</div></div>
    """+claim_html+"""
    <div class="card" style="display:flex;gap:12px;align-items:center"><div style="font-size:50px">🏆</div>
    <div><i style="color:#00b0ff;font-size:20px">Stay Consistent!</i><br><small>The more days you check in,<br>the bigger your rewards!</small><br><i style="color:#00cfff;font-size:13px">Discipline Today = Financial Freedom Tomorrow</i></div></div>
    <div class="bottom"><a href="/home">🏠<br>Home</a><a href="/invest">📊<br>Invest</a><a href="/my-investments">💼<br>My Invest</a><a href="/transactions">🔄<br>Transactions</a><a href="/referrals">👥<br>Referrals</a><a href="/account">👤<br>Account</a></div>
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



















# --- ADMIN PANEL Deep Blue / White ---

def init_invest_tables():
    import sqlite3
    db = sqlite3.connect('codex700.db')
    db.execute("""CREATE TABLE IF NOT EXISTS investments
    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id TEXT,
     product_name TEXT, quantity INTEGER, amount INTEGER,
     start_ts INTEGER, maturity_ts INTEGER,
     daily_income INTEGER, total_expected INTEGER,
     status TEXT DEFAULT 'ACTIVE', credited INTEGER DEFAULT 0)""")
    db.execute("""CREATE TABLE IF NOT EXISTS transactions
    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT,
     amount INTEGER, desc TEXT, created_ts INTEGER)""")
    db.execute("""CREATE TABLE IF NOT EXISTS notifications
    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, msg TEXT, created_ts INTEGER)""")
    db.commit()

def process_maturities(user_id=None):
    import sqlite3, time
    db = sqlite3.connect('codex700.db')
    db.row_factory = sqlite3.Row
    now = int(time.time())
    q = "SELECT * FROM investments WHERE status='ACTIVE' AND maturity_ts<=? AND credited=0"
    args = [now]
    if user_id:
        q += " AND user_id=?"
        args.append(user_id)
    rows = db.execute(q, args).fetchall()
    for inv in rows:
        cur = db.cursor()
        cur.execute("BEGIN IMMEDIATE")
        r = cur.execute("SELECT status, credited FROM investments WHERE id=?", (inv["id"],)).fetchone()
        if not r or r[0]!='ACTIVE' or r[1]!=0:
            db.rollback(); continue
        cur.execute("UPDATE users SET balance=balance+? WHERE id=?", (inv["total_expected"], inv["user_id"]))
        cur.execute("UPDATE investments SET status='COMPLETED', credited=1 WHERE id=?", (inv["id"],))
        cur.execute("INSERT INTO transactions (user_id,type,amount,desc,created_ts) VALUES (?,?,?,?,?)",
            (inv["user_id"], "maturity", inv["total_expected"], f"{inv['product_name']} matured", now))
        cur.execute("INSERT INTO notifications (user_id,title,msg,created_ts) VALUES (?,?,?,?)",
            (inv["user_id"], f"{inv['product_name']} Investment Completed",
             f"Your {inv['product_name']} investment has matured. Your account balance has been updated.", now))
        db.commit()
    try: init_invest_tables()
    except: pass


@app.route('/invest/confirm', methods=['POST'])
def invest_confirm():
    import sqlite3, time
    from flask import request, session, redirect
    if 'user_id' not in session: return redirect('/login')
    uid = session['user_id']
    pid = request.form.get('product_id','J1')
    try: qty = int(request.form.get('quantity',1))
    except: qty = 1
    if qty<1 or qty>10: return "Invalid quantity",400
    if pid not in PRODUCTS: return "Invalid product",400
    pr = PRODUCTS[pid]
    amount = pr['price']*qty
    db = sqlite3.connect('codex700.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute("BEGIN IMMEDIATE")
    row = cur.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
    if not row or row[0] < amount:
        db.rollback()
        return render_template('invest_success.html', success=False, plan_name=pid, amount=f"{amount:,}", balance=f"{row[0] if row else 0:,}", daily_pct=int(pr.get('daily_rate',20)*100) if 'daily_rate' in pr else 20, duration_days=pr.get('days',45)), 400
    now = int(time.time())
    maturity = now + pr['days']*86400
    daily = pr['daily']*qty
    total = daily*pr['days']
    cur.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, uid))
    cur.execute("""INSERT INTO investments (user_id,product_id,product_name,quantity,amount,start_ts,maturity_ts,daily_income,total_expected,status)
                   VALUES (?,?,?,?,?,?,?,?,?,'ACTIVE')""", (uid,pid,pid,qty,amount,now,maturity,daily,total))
    inv_id = cur.lastrowid
    cur.execute("INSERT INTO transactions (user_id,type,amount,desc,created_ts) VALUES (?,?,?,?,?)",
                (uid,'invest',-amount,f"{pid} x{qty} invested",now))
    db.commit()
    return redirect(f'/invest/success/{inv_id}')

@app.route('/invest/success/<int:inv_id>')
def invest_success(inv_id):
    import sqlite3
    from flask import session, redirect
    if 'user_id' not in session: return redirect('/login')
    db = sqlite3.connect('codex700.db')
    db.row_factory = sqlite3.Row
    inv = db.execute("SELECT * FROM investments WHERE id=?", (inv_id,)).fetchone()
    if not inv:
        return 'not found',404

@app.route('/my-investments')
def my_investments():
    import time, sqlite3
    uid=session.get('uid') or session.get('user_id')
    if not uid: return redirect('/login')
    now=int(time.time())
    con=sqlite3.connect("codex700.db"); con.row_factory=sqlite3.Row
    # credit daily returns
    for inv in list(con.execute("SELECT * FROM investments WHERE user_id=? AND active=1", (uid,))):
        try:
            start=inv["purchase_ts"] or now
            daily=inv["daily_return"] or 0
            credited=inv["credited_days"] or 0
            duration=inv["duration_days"] or 30
            expiry=inv["expiry_ts"] or (start+duration*86400)
            total_days=int((expiry-start)//86400)
            days_passed=min(total_days, (now-start)//86400)
            claimable=int(days_passed-credited)
            if claimable>0 and daily>0:
                con.execute("UPDATE users SET balance=balance+? WHERE id=?", (claimable*daily, uid))
                con.execute("UPDATE investments SET credited_days=? WHERE id=?", (credited+claimable, inv["id"]))
                con.execute("INSERT INTO transactions(user_id,type,amount,desc,created_ts) VALUES(?,?,?,?,?)",(uid,'daily_return',claimable*daily,f"Daily return {inv['product_name']}",now))
            if now>=expiry:
                con.execute("UPDATE investments SET active=0 WHERE id=?", (inv["id"],))
        except Exception as e: print("credit err",e)
    con.commit()
    active=list(con.execute("SELECT * FROM investments WHERE user_id=? AND active=1 ORDER BY expiry_ts DESC", (uid,)))
    done=list(con.execute("SELECT * FROM investments WHERE user_id=? AND active=0 ORDER BY id DESC LIMIT 20", (uid,)))
    con.close()
    return render_template('my_investments.html', active=active, done=done, now=now)

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
    uid=session.get("uid") or session.get("user_id") or session.get("user_id")
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


def init_invest_tables_v1():
    import sqlite3
    db = sqlite3.connect('codex700.db')
    db.execute("""CREATE TABLE IF NOT EXISTS investments
    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, product_id TEXT,
     product_name TEXT, quantity INTEGER, amount INTEGER,
     start_ts INTEGER, maturity_ts INTEGER,
     daily_income INTEGER, total_expected INTEGER,
     status TEXT DEFAULT 'ACTIVE', credited INTEGER DEFAULT 0)""")
    db.execute("""CREATE TABLE IF NOT EXISTS transactions
    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT,
     amount INTEGER, desc TEXT, created_ts INTEGER)""")
    db.execute("""CREATE TABLE IF NOT EXISTS notifications
    (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, msg TEXT, created_ts INTEGER)""")
    db.commit()

def process_maturities_v1(user_id=None):
    import sqlite3, time
    db = sqlite3.connect('codex700.db')
    db.row_factory = sqlite3.Row
    now = int(time.time())
    q = "SELECT * FROM investments WHERE status='ACTIVE' AND maturity_ts<=? AND credited=0"
    args = [now]
    if user_id:
        q += " AND user_id=?"
        args.append(user_id)
    rows = db.execute(q, args).fetchall()
    for inv in rows:
        cur = db.cursor()
        cur.execute("BEGIN IMMEDIATE")
        r = cur.execute("SELECT status, credited FROM investments WHERE id=?", (inv["id"],)).fetchone()
        if not r or r[0]!='ACTIVE' or r[1]!=0:
            db.rollback(); continue
        cur.execute("UPDATE users SET balance=balance+? WHERE id=?", (inv["total_expected"], inv["user_id"]))
        cur.execute("UPDATE investments SET status='COMPLETED', credited=1 WHERE id=?", (inv["id"],))
        cur.execute("INSERT INTO transactions (user_id,type,amount,desc,created_ts) VALUES (?,?,?,?,?)",
            (inv["user_id"], "maturity", inv["total_expected"], f"{inv['product_name']} matured", now))
        cur.execute("INSERT INTO notifications (user_id,title,msg,created_ts) VALUES (?,?,?,?)",
            (inv["user_id"], f"{inv['product_name']} Investment Completed",
             f"Your {inv['product_name']} investment has matured. Your account balance has been updated.", now))
        db.commit()
    try: init_invest_tables()
    except: pass


@app.route('/invest/confirm', methods=['POST'], endpoint='invest_confirm_v2')
def invest_confirm_v2():
    import sqlite3, time
    from flask import request, session, redirect
    if 'user_id' not in session: return redirect('/login')
    uid = session['user_id']
    pid = request.form.get('product_id','J1')
    try: qty = int(request.form.get('quantity',1))
    except: qty = 1
    if qty<1 or qty>10: return "Invalid quantity",400
    if pid not in PRODUCTS: return "Invalid product",400
    pr = PRODUCTS[pid]
    amount = pr['price']*qty
    db = sqlite3.connect('codex700.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute("BEGIN IMMEDIATE")
    row = cur.execute("SELECT balance FROM users WHERE id=?", (uid,)).fetchone()
    if not row or row[0] < amount:
        db.rollback()
        return render_template('invest_success.html', success=False, plan_name=pid, amount=f"{amount:,}", balance=f"{row[0] if row else 0:,}", daily_pct=int(pr.get('daily_rate',20)*100) if 'daily_rate' in pr else 20, duration_days=pr.get('days',45)), 400
    now = int(time.time())
    maturity = now + pr['days']*86400
    daily = pr['daily']*qty
    total = daily*pr['days']
    cur.execute("UPDATE users SET balance=balance-? WHERE id=?", (amount, uid))
    cur.execute("""INSERT INTO investments (user_id,product_id,product_name,quantity,amount,start_ts,maturity_ts,daily_income,total_expected,status)
                   VALUES (?,?,?,?,?,?,?,?,?,'ACTIVE')""", (uid,pid,pid,qty,amount,now,maturity,daily,total))
    inv_id = cur.lastrowid
    cur.execute("INSERT INTO transactions (user_id,type,amount,desc,created_ts) VALUES (?,?,?,?,?)",
                (uid,'invest',-amount,f"{pid} x{qty} invested",now))
    db.commit()
    return redirect(f'/invest/success/{inv_id}')

@app.route('/invest/success/<int:inv_id>', endpoint='invest_success_v1')
def invest_success_v1(inv_id):
    import sqlite3
    from flask import session, redirect
    if 'user_id' not in session: return redirect('/login')
    db = sqlite3.connect('codex700.db')
    db.row_factory = sqlite3.Row
    inv = db.execute("SELECT * FROM investments WHERE id=?", (inv_id,)).fetchone()
    if not inv:
        return 'not found',404


@app.route("/api/daily-status")
def api_daily_status():
    import sqlite3
    from datetime import datetime, timedelta
    from flask import session, jsonify
    uid=str(session.get("uid") or session.get("user_id") or "guest")
    if uid=="guest":
        return jsonify({"claimed":False})
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkins (user_id TEXT PRIMARY KEY, last_claim TEXT, streak INTEGER DEFAULT 0)")
    row=con.execute("SELECT * FROM daily_checkins WHERE user_id=?",(uid,)).fetchone()
    con.close()
    now=datetime.utcnow()
    if not row:
        return jsonify({"claimed":False,"streak":0})
    last=row["last_claim"][:10]
    today=now.date().isoformat()
    if last==today:
        tomorrow=datetime.combine(now.date()+timedelta(days=1), datetime.min.time())
        diff=tomorrow-now
        return jsonify({"claimed":True,"next_in":int(diff.total_seconds()),"streak":row["streak"]})
    else:
        return jsonify({"claimed":False,"streak":row["streak"]})

@app.route("/api/daily-checkin", methods=["POST"])
def api_daily_checkin():
    import sqlite3
    from datetime import datetime, timedelta
    from flask import session, jsonify
    uid=str(session.get("uid") or session.get("user_id") or "guest")
    if uid=="guest":
        return jsonify({"ok":False,"msg":"Login first"})
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkins (user_id TEXT PRIMARY KEY, last_claim TEXT, streak INTEGER DEFAULT 0)")
    row=con.execute("SELECT * FROM daily_checkins WHERE user_id=?",(uid,)).fetchone()
    now=datetime.utcnow()
    today=now.date().isoformat()
    if row:
        last=row["last_claim"][:10]
        if last==today:
            tomorrow=datetime.combine(now.date()+timedelta(days=1), datetime.min.time())
            diff=tomorrow-now
            con.close()
            return jsonify({"ok":False,"msg":"Already claimed today","next_in":int(diff.total_seconds()),"streak":row["streak"]})
        yesterday=(now.date()-timedelta(days=1)).isoformat()
        new_streak=row["streak"]+1 if last==yesterday else 1
        reward=500*new_streak
        con.execute("UPDATE daily_checkins SET last_claim=?, streak=? WHERE user_id=?",(now.isoformat(), new_streak, uid))
        con.execute("UPDATE users SET balance=balance+? WHERE id=?",(reward, uid))
        con.commit()
        con.close()
        return jsonify({"ok":True,"msg":f"Checked in! +{reward} UGX","streak":new_streak,"reward":reward})
    else:
        con.execute("INSERT INTO daily_checkins (user_id, last_claim, streak) VALUES (?,?,?)",(uid, now.isoformat(), 1))
        con.execute("UPDATE users SET balance=balance+? WHERE id=?",(500, uid))
        con.commit()
        con.close()
        return jsonify({"ok":True,"msg":"First check-in! +500 UGX","streak":1,"reward":500})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__=='__main__':
 app.run(host='0.0.0.0', port=5000, debug=True)


@app.route("/withdraw-submit", methods=["POST"])
def withdraw_submit():
    import sqlite3
    from flask import request, session, jsonify
    uid=session.get("uid") or session.get("user_id") or session.get("user_id")
    if not uid: return jsonify({"ok":False,"msg":"Login first"})
    amt=request.form.get("amount","").strip()
    phone=request.form.get("phone","").strip()
    try: amt=int(float(amt))
    except: return jsonify({"ok":False,"msg":"Invalid amount"})
    if amt<5000: return jsonify({"ok":False,"msg":"Minimum 5000 UGX"})
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    bal=con.execute("SELECT balance FROM users WHERE id=?",(uid,)).fetchone()[0]
    if bal<amt:
        con.close(); return jsonify({"ok":False,"msg":"Insufficient balance"})
    con.execute("CREATE TABLE IF NOT EXISTS withdrawals (id INTEGER PRIMARY KEY, user_id INT, amount INT, phone TEXT, status TEXT DEFAULT 'pending', created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    con.execute("UPDATE users SET balance=balance-? WHERE id=?",(amt,uid))
    con.execute("INSERT INTO withdrawals (user_id,amount,phone,status) VALUES (?,?,?, 'pending')",(uid,amt,phone))
    con.commit(); con.close()
    return jsonify({"ok":True,"msg":"Withdrawal requested, wait for approval"})

@app.route("/deposit-submit", methods=["POST"])
def deposit_submit():
    from flask import request, session, jsonify
    try:
        uid = session.get("uid") or session.get("user_id")
        if not uid:
            from flask import redirect
            return redirect("/login")
        airtel = request.form.get("phone_number","").strip()
        amount = request.form.get("amount","").strip()
        txid = request.form.get("txid","").strip()
        if not airtel or not amount or not txid:
            return jsonify({"ok":False,"msg":"Fill all fields"})
        import sqlite3, os, time
        os.makedirs("static/shots", exist_ok=True)
        f=request.files.get("screenshot")
        sp=""
        if f and f.filename:
            fn=f"{uid}_{int(time.time())}_{f.filename.replace('/','_')}"
            fp=os.path.join("static/shots", fn)
            f.save(fp); sp="/"+fp
        con=sqlite3.connect("codex700.db")
        con.execute("CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY, user_id INT, airtel TEXT, amount INT, txid TEXT, screenshot TEXT, status TEXT DEFAULT 'pending', created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        con.execute("INSERT INTO deposits (user_id, airtel, amount, txid, screenshot) VALUES (?,?,?,?,?)",(uid,airtel,amount,txid,sp))
        con.commit(); con.close()
        from flask import redirect
        return redirect("/transactions")
    except Exception as e:
        return jsonify({"ok":False,"msg":"Server error: "+str(e)})

