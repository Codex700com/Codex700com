import os, sqlite3, secrets, string, hashlib, hmac
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, redirect, session, render_template, flash, url_for

BASE=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(BASE,"codex700.db")
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-before-production")

PLANS={
 "CX-1":{"series":"CX series","price":250000,"daily":20000,"days":30,"total":600000},
 "CX-2":{"series":"CX series","price":500000,"daily":40000,"days":30,"total":1200000},
 "BM-1":{"series":"BM series","price":1000000,"daily":85000,"days":30,"total":2550000},
 "BM-2":{"series":"BM series","price":2000000,"daily":180000,"days":30,"total":5400000},
 "DS-3":{"series":"DS series","price":3500000,"daily":320000,"days":30,"total":9600000},
 "DS-4":{"series":"DS series","price":5000000,"daily":500000,"days":30,"total":15000000},
}
REWARDS=[(120,750000),(100,50000),(60,275000),(30,150000),(15,98000),(6,45000)]


def db():
    con=sqlite3.connect(DB,timeout=10)
    con.row_factory=sqlite3.Row
    return con

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def month_start():
    n=datetime.now(timezone.utc)
    return n.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
def previous_month_start():
    n=month_start()
    return n.replace(year=n.year-1,month=12) if n.month==1 else n.replace(month=n.month-1)
def pw_hash(p): return hashlib.sha256(p.encode()).hexdigest()
def make_code(con):
    chars=string.ascii_uppercase+string.digits
    while True:
        code=''.join(secrets.choice(chars) for _ in range(8))
        if not con.execute("SELECT 1 FROM users WHERE invite_code=?",(code,)).fetchone(): return code

def init_db():
    con=db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,phone TEXT UNIQUE NOT NULL,password TEXT NOT NULL,invite_code TEXT UNIQUE NOT NULL,invited_by INTEGER,balance REAL NOT NULL DEFAULT 0,wallet REAL NOT NULL DEFAULT 0,display_name TEXT NOT NULL DEFAULT '',mtn_number TEXT NOT NULL DEFAULT '',airtel_number TEXT NOT NULL DEFAULT '',usdt_wallet TEXT NOT NULL DEFAULT '',notifications_enabled INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL,is_admin INTEGER NOT NULL DEFAULT 0,salary_claimed_month TEXT,reward_claimed_month TEXT);
    CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,kind TEXT NOT NULL,amount REAL NOT NULL DEFAULT 0,status TEXT NOT NULL DEFAULT 'PENDING',reference TEXT,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,code TEXT NOT NULL,name TEXT NOT NULL,price REAL NOT NULL,daily_income REAL NOT NULL DEFAULT 0,lock_days INTEGER NOT NULL DEFAULT 30,total_income REAL NOT NULL DEFAULT 0,purchased_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'ACTIVE');
    CREATE TABLE IF NOT EXISTS support_messages(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,sender TEXT NOT NULL,message TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS raffle_tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,quantity INTEGER NOT NULL,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS reward_box_claims(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,box_id INTEGER NOT NULL,amount REAL NOT NULL,created_at TEXT NOT NULL,UNIQUE(uid,box_id));
    CREATE TABLE IF NOT EXISTS password_requests(id INTEGER PRIMARY KEY AUTOINCREMENT,phone TEXT NOT NULL,name TEXT,message TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'PENDING',created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS gift_codes(code TEXT PRIMARY KEY,amount REAL NOT NULL,used_by INTEGER,used_at TEXT);
    """)
    # Safe migrations for any copy that already has an older fresh DB.
    cols={r[1] for r in con.execute("PRAGMA table_info(users)").fetchall()}
    for col,typ in [("display_name","TEXT NOT NULL DEFAULT ''"),("mtn_number","TEXT NOT NULL DEFAULT ''"),("airtel_number","TEXT NOT NULL DEFAULT ''"),("usdt_wallet","TEXT NOT NULL DEFAULT ''"),("notifications_enabled","INTEGER NOT NULL DEFAULT 1"),("salary_claimed_month","TEXT"),("reward_claimed_month","TEXT")]:
        if col not in cols: con.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")
    con.commit(); con.close()

def current_user():
    if "uid" not in session:return None
    con=db(); u=con.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone(); con.close(); return u

def required(fn):
    @wraps(fn)
    def w(*a,**k): return fn(*a,**k) if current_user() else redirect(url_for("login"))
    return w

def admin_required(fn):
    @wraps(fn)
    def w(*a,**k):
        u=current_user()
        return fn(*a,**k) if u and u["is_admin"] else ("Forbidden",403)
    return w

def invite_counts(uid):
    cur=month_start(); prev=previous_month_start(); con=db()
    last=con.execute("SELECT COUNT(*) n FROM users WHERE invited_by=? AND created_at>=? AND created_at<?",(uid,prev.isoformat(),cur.isoformat())).fetchone()["n"]
    this=con.execute("SELECT COUNT(*) n FROM users WHERE invited_by=? AND created_at>=?",(uid,cur.isoformat())).fetchone()["n"]
    con.close(); return last,this

def active_income(uid):
    con=db(); rows=con.execute("SELECT * FROM products WHERE uid=? AND status='ACTIVE'",(uid,)).fetchall(); con.close()
    total=0; today=0
    n=datetime.now(timezone.utc)
    for r in rows:
        try:
            started=datetime.fromisoformat(r["purchased_at"])
            days=max(0,(n-started).days)
            total+=min(r["total_income"],r["daily_income"]*days)
            if days<r["lock_days"]: today+=r["daily_income"]
        except Exception: pass
    return total,today

@app.route("/")
def index(): return redirect(url_for("home") if current_user() else url_for("login"))

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        phone=request.form.get("phone","").strip(); password=request.form.get("password",""); confirm=request.form.get("confirm",""); invite=request.form.get("invite","").strip().upper(); cap=request.form.get("captcha_input","").strip(); real=request.form.get("real_captcha","").strip()
        if not phone or not password: flash("Phone number and password are required.","error")
        elif password!=confirm: flash("Passwords do not match.","error")
        elif cap!=real: flash("Incorrect verification code.","error")
        else:
            con=db()
            if con.execute("SELECT 1 FROM users WHERE phone=?",(phone,)).fetchone(): flash("Phone already registered.","error")
            else:
                inviter=con.execute("SELECT id FROM users WHERE invite_code=?",(invite,)).fetchone() if invite else None
                con.execute("INSERT INTO users(phone,password,invite_code,invited_by,created_at) VALUES(?,?,?,?,?)",(phone,pw_hash(password),make_code(con),inviter["id"] if inviter else None,now())); con.commit(); con.close(); flash("Registration successful. You can now login.","success"); return redirect(url_for("login"))
            con.close()
    real=''.join(secrets.choice(string.digits) for _ in range(4))
    return render_template("register.html",real_captcha=real,invite=request.args.get("ref",request.form.get("invite","")))

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        phone=request.form.get("phone","").strip(); password=request.form.get("password","")
        con=db(); u=con.execute("SELECT * FROM users WHERE phone=?",(phone,)).fetchone(); con.close()
        if not u or not hmac.compare_digest(u["password"],pw_hash(password)): flash("Invalid phone number or password.","error")
        else:
            session.clear()
            session["uid"]=u["id"]
            session["show_announcement"]=True
            return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("login"))

@app.route("/reset",methods=["GET","POST"])
def reset():
    if request.method=="POST":
        phone=request.form.get("phone","").strip(); name=request.form.get("name","").strip(); message=request.form.get("message","").strip()
        if not phone or not message: flash("Registered phone number and message are required.","error")
        else:
            con=db(); con.execute("INSERT INTO password_requests(phone,name,message,created_at) VALUES(?,?,?,?)",(phone,name,message,now())); con.commit(); con.close(); flash("Your request has been sent to the manager.","success"); return redirect(url_for("login"))
    return render_template("reset.html")

@app.route("/home")
@required
def home():
    u=current_user(); con=db(); products=con.execute("SELECT * FROM products WHERE uid=? ORDER BY id DESC",(u["id"],)).fetchall(); con.close(); ai_income,today=active_income(u["id"]); last,this=invite_counts(u["id"])
    show_announcement=session.pop("show_announcement",False)
    return render_template("home.html",user=u,products=products,ai_income=ai_income,today=today,invite_count=this,show_announcement=show_announcement)

@app.route("/my")
@required
def my():
    u=current_user(); last,this=invite_counts(u["id"]); ai_income,today=active_income(u["id"])
    return render_template("my.html",user=u,invited_last_month=last,invited_this_month=this,last_salary=last*3000,ai_income=ai_income,today=today)

@app.route("/my/claim-salary",methods=["POST"])
@required
def claim_salary():
    u=current_user(); last,_=invite_counts(u["id"]); key=previous_month_start().strftime("%Y-%m")
    con=db(); cur=con.execute("SELECT salary_claimed_month FROM users WHERE id=?",(u["id"],)).fetchone()
    if cur["salary_claimed_month"]==key: con.close(); flash("Last month's salary has already been claimed.","error"); return redirect(url_for("my"))
    if last<=0: con.close(); flash("The number of invite last month was not enough","error"); return redirect(url_for("my"))
    amount=last*3000; con.execute("UPDATE users SET balance=balance+?,salary_claimed_month=? WHERE id=?",(amount,key,u["id"])); con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(u["id"],"REFERRAL_SALARY",amount,"APPROVED","SAL-"+key,now())); con.commit(); con.close(); flash(f"UGX {amount:,.0f} last month's salary added to your balance.","success"); return redirect(url_for("my"))

@app.route("/my/claim-reward",methods=["POST"])
@required
def claim_reward():
    u=current_user(); last,_=invite_counts(u["id"]); key=previous_month_start().strftime("%Y-%m"); reward=next((amt for req,amt in REWARDS if last>=req),0)
    con=db(); cur=con.execute("SELECT reward_claimed_month FROM users WHERE id=?",(u["id"],)).fetchone()
    if cur["reward_claimed_month"]==key: con.close(); flash("Last month's reward has already been claimed.","error"); return redirect(url_for("my"))
    if reward<=0: con.close(); flash("The number of invite last month was not enough","error"); return redirect(url_for("my"))
    con.execute("UPDATE users SET balance=balance+?,reward_claimed_month=? WHERE id=?",(reward,key,u["id"])); con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(u["id"],"REFERRAL_REWARD",reward,"APPROVED","REW-"+key,now())); con.commit(); con.close(); flash(f"UGX {reward:,.0f} reward added to your balance.","success"); return redirect(url_for("my"))

@app.route("/invite")
@required
def invite():
    u=current_user(); link=request.host_url.rstrip('/')+"/register?ref="+u["invite_code"]
    return render_template("invite.html",user=u,link=link,active="My")

@app.route("/my-team")
@required
def my_team():
    u=current_user(); con=db(); rows=con.execute("SELECT phone,created_at FROM users WHERE invited_by=? ORDER BY id DESC",(u["id"],)).fetchall(); con.close(); return render_template("team.html",rows=rows,active="My")

@app.route("/deposit",methods=["GET","POST"])
@required
def deposit():
    if request.method=="POST":
        try: amount=float(request.form.get("amount") or 0)
        except: amount=0
        if amount<=0: flash("Enter a valid amount.","error")
        else:
            con=db(); ref="DEP-"+secrets.token_hex(4).upper(); con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(session["uid"],"DEPOSIT",amount,"PENDING",ref,now())); con.commit(); con.close(); flash("Deposit request submitted for approval.","success"); return redirect(url_for("deposit"))
    return render_template("form.html",title="Deposit details",action="/deposit",fields=[("amount","Amount (UGX)","number")],active="My")

@app.route("/withdraw",methods=["GET","POST"])
@required
def withdraw():
    if request.method=="POST":
        try: amount=float(request.form.get("amount") or 0)
        except: amount=0
        con=db(); u=con.execute("SELECT balance FROM users WHERE id=?",(session["uid"],)).fetchone()
        if amount<=0 or amount>u["balance"]: con.close(); flash("Insufficient balance or invalid amount.","error")
        else:
            ref="WDR-"+secrets.token_hex(4).upper(); con.execute("UPDATE users SET balance=balance-? WHERE id=?",(amount,session["uid"])); con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(session["uid"],"WITHDRAW",amount,"PENDING",ref,now())); con.commit(); con.close(); flash("Withdrawal request submitted.","success"); return redirect(url_for("withdraw"))
    return render_template("form.html",title="Withdraw details",action="/withdraw",fields=[("amount","Amount (UGX)","number")],active="My")

@app.route("/account",methods=["GET","POST"])
@required
def account():
    u=current_user()
    if request.method=="POST":
        con=db(); con.execute("UPDATE users SET display_name=?,mtn_number=?,airtel_number=?,usdt_wallet=?,notifications_enabled=? WHERE id=?",(request.form.get("display_name","").strip(),request.form.get("mtn_number","").strip(),request.form.get("airtel_number","").strip(),request.form.get("usdt_wallet","").strip(),1 if request.form.get("notifications") else 0,u["id"])); con.commit(); con.close(); flash("Settings saved.","success"); return redirect(url_for("account"))
    return render_template("settings.html",user=u,active="My")

@app.route("/card")
@required
def card(): return render_template("simple.html",title="Card",content="<h2>Card</h2><p>Save your payout details in Settings. Card-provider integration can be connected later.</p>",active="My")
@app.route("/bills")
@required
def bills(): return render_template("simple.html",title="Bills",content="<h2>Bills</h2><p>Bill payment providers are not connected yet. No money is charged from this page.</p>",active="My")
@app.route("/vip-tasks")
@required
def vip_tasks(): return render_template("simple.html",title="VIP Task",content="<h2>VIP Tasks</h2><p>No tasks are currently assigned.</p>",active="My")
@app.route("/manager")
@required
def manager(): return render_template("simple.html",title="Manager",content="<h2>Manager</h2><p>Use Chats to contact the manager.</p>",active="My")

@app.route("/reward")
@required
def reward(): return render_template("reward.html",rewards=REWARDS,active="My")

@app.route("/gift-code",methods=["GET","POST"])
@required
def gift_code():
    u=current_user(); con=db()
    if request.method=="POST":
        code=request.form.get("code","").strip().upper(); g=con.execute("SELECT * FROM gift_codes WHERE code=?",(code,)).fetchone()
        if not g: flash("Gift code not found.","error")
        elif g["used_by"]: flash("Gift code has already been used.","error")
        else:
            con.execute("UPDATE gift_codes SET used_by=?,used_at=? WHERE code=? AND used_by IS NULL",(u["id"],now(),code)); con.execute("UPDATE users SET balance=balance+? WHERE id=?",(g["amount"],u["id"])); con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(u["id"],"GIFT_CODE",g["amount"],"APPROVED",code,now())); con.commit(); flash(f"UGX {g['amount']:,.0f} added to your balance.","success")
    con.close(); return render_template("gift.html",active="My")

@app.route("/invest")
@required
def invest(): return render_template("invest.html",plans=PLANS,active="AI")

@app.route("/product",methods=["GET","POST"])
@required
def product():
    code=request.values.get("p","").upper()
    if code not in PLANS:return "Product not found",404
    plan=PLANS[code]
    if request.method=="POST":
        con=db(); u=con.execute("SELECT balance FROM users WHERE id=?",(session["uid"],)).fetchone()
        if u["balance"]<plan["price"]: con.close(); flash("Purchase failed due to insufficient balance.","error")
        else:
            con.execute("UPDATE users SET balance=balance-? WHERE id=?",(plan["price"],session["uid"])); con.execute("INSERT INTO products(uid,code,name,price,daily_income,lock_days,total_income,purchased_at) VALUES(?,?,?,?,?,?,?,?)",(session["uid"],code,code+" AI Machine",plan["price"],plan["daily"],plan["days"],plan["total"],now())); con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(session["uid"],"AI_PURCHASE",plan["price"],"APPROVED","BUY-"+code,now())); con.commit(); con.close(); flash("Purchase successful.","success")
        return redirect(url_for("invest"))
    return render_template("product.html",code=code,plan=plan,active="AI")

@app.route("/income")
@required
def income():
    con=db(); tx=con.execute("SELECT * FROM transactions WHERE uid=? ORDER BY id DESC",(session["uid"],)).fetchall(); con.close(); return render_template("income.html",tx=tx,active="Income")

@app.route("/support",methods=["GET","POST"])
@required
def support():
    if request.method=="POST":
        msg=request.form.get("message","").strip()
        if msg:
            con=db(); con.execute("INSERT INTO support_messages(uid,sender,message,created_at) VALUES(?,?,?,?)",(session["uid"],"USER",msg,now())); con.commit(); con.close(); flash("Message sent.","success")
        return redirect(url_for("support"))
    con=db(); messages=con.execute("SELECT * FROM support_messages WHERE uid=? ORDER BY id",(session["uid"],)).fetchall(); con.close(); return render_template("support.html",messages=messages,active="chats")

@app.route("/raffle")
@required
def raffle():
    u=current_user()
    con=db()
    # A completed/approved deposit unlocks the promotional reward boxes.
    deposited=con.execute("SELECT 1 FROM transactions WHERE uid=? AND kind='DEPOSIT' AND status='APPROVED' LIMIT 1",(u["id"],)).fetchone()
    claims={r["box_id"]: r["amount"] for r in con.execute("SELECT box_id,amount FROM reward_box_claims WHERE uid=?",(u["id"],)).fetchall()}
    con.close()
    boxes=[
        {"id":1,"amount":10000},
        {"id":2,"amount":15000},
        {"id":3,"amount":20000},
        {"id":4,"amount":30000},
        {"id":5,"amount":50000},
        {"id":6,"amount":100000},
    ]
    return render_template("raffle.html",eligible=bool(deposited),boxes=boxes,claims=claims,active="Raffle")

@app.route("/raffle/box/<int:box_id>",methods=["POST"])
@required
def open_reward_box(box_id):
    u=current_user()
    boxes={1:10000,2:15000,3:20000,4:30000,5:50000,6:100000}
    amount=boxes.get(box_id)
    if amount is None:
        flash("Reward box not found.","error")
        return redirect(url_for("raffle"))
    con=db()
    deposited=con.execute("SELECT 1 FROM transactions WHERE uid=? AND kind='DEPOSIT' AND status='APPROVED' LIMIT 1",(u["id"],)).fetchone()
    if not deposited:
        con.close()
        flash("Make and complete a deposit to unlock the reward boxes.","error")
        return redirect(url_for("raffle"))
    try:
        con.execute("INSERT INTO reward_box_claims(uid,box_id,amount,created_at) VALUES(?,?,?,?)",(u["id"],box_id,amount,now()))
    except sqlite3.IntegrityError:
        con.close()
        flash("This reward box has already been opened.","error")
        return redirect(url_for("raffle"))
    con.execute("UPDATE users SET balance=balance+? WHERE id=?",(amount,u["id"]))
    con.execute("INSERT INTO transactions(uid,kind,amount,status,reference,created_at) VALUES(?,?,?,?,?,?)",(u["id"],"REWARD_BOX",amount,"APPROVED",f"BOX-{box_id}-{secrets.token_hex(3).upper()}",now()))
    con.commit(); con.close()
    flash(f"UGX {amount:,.0f} reward added to your balance.","success")
    return redirect(url_for("raffle"))

@app.route("/admin")
@admin_required
def admin():
    con=db(); users=con.execute("SELECT id,phone,balance,created_at,is_admin FROM users ORDER BY id DESC").fetchall(); tx=con.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 100").fetchall(); requests=con.execute("SELECT * FROM password_requests ORDER BY id DESC LIMIT 50").fetchall(); messages=con.execute("SELECT * FROM support_messages ORDER BY id DESC LIMIT 100").fetchall(); con.close(); return render_template("admin.html",users=users,tx=tx,requests=requests,messages=messages)

@app.route("/admin/transaction/<int:tid>/<action>",methods=["POST"])
@admin_required
def admin_transaction(tid,action):
    con=db(); t=con.execute("SELECT * FROM transactions WHERE id=?",(tid,)).fetchone()
    if not t or t["status"]!="PENDING": con.close(); return redirect(url_for("admin"))
    if action=="approve":
        if t["kind"]=="DEPOSIT": con.execute("UPDATE users SET balance=balance+? WHERE id=?",(t["amount"],t["uid"]))
        con.execute("UPDATE transactions SET status='APPROVED' WHERE id=?",(tid,))
    elif action=="reject":
        if t["kind"]=="WITHDRAW": con.execute("UPDATE users SET balance=balance+? WHERE id=?",(t["amount"],t["uid"]))
        con.execute("UPDATE transactions SET status='REJECTED' WHERE id=?",(tid,))
    con.commit(); con.close(); return redirect(url_for("admin"))

@app.route("/admin/support/<int:uid>",methods=["POST"])
@admin_required
def admin_support(uid):
    msg=request.form.get("message","").strip()
    if msg:
        con=db(); con.execute("INSERT INTO support_messages(uid,sender,message,created_at) VALUES(?,?,?,?)",(uid,"MANAGER",msg,now())); con.commit(); con.close()
    return redirect(url_for("admin"))

@app.route("/admin/gift",methods=["POST"])
@admin_required
def admin_gift():
    try: amount=float(request.form.get("amount") or 0)
    except: amount=0
    if amount<=0: flash("Invalid gift amount.","error")
    else:
        code="HUT9-"+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(8)); con=db(); con.execute("INSERT INTO gift_codes(code,amount) VALUES(?,?)",(code,amount)); con.commit(); con.close(); flash("Gift code created: "+code,"success")
    return redirect(url_for("admin"))

@app.route("/admin/create")
def admin_create():
    phone=os.environ.get("ADMIN_PHONE"); password=os.environ.get("ADMIN_PASSWORD")
    if not phone or not password: return "Set ADMIN_PHONE and ADMIN_PASSWORD environment variables first.",400
    con=db(); exists=con.execute("SELECT 1 FROM users WHERE phone=?",(phone,)).fetchone()
    if not exists: con.execute("INSERT INTO users(phone,password,invite_code,created_at,is_admin) VALUES(?,?,?,?,1)",(phone,pw_hash(password),make_code(con),now()))
    else: con.execute("UPDATE users SET is_admin=1,password=? WHERE phone=?",(pw_hash(password),phone))
    con.commit(); con.close(); return "Admin account ready."

init_db()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
