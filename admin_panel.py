from flask import Blueprint, request, redirect, session, render_template_string
import sqlite3, datetime
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
DB="codex700.db"
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def guard():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    return None
TOP="""<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>
body{margin:0;background:#0b0f1a;color:#e2e8f0;display:flex;font-family:system-ui}
.sidebar{width:230px;background:#111827;min-height:100vh;padding:15px;position:sticky;top:0;height:100vh}
.sidebar a{display:block;color:#9ca3af;text-decoration:none;padding:10px;border-radius:8px;margin:3px 0}
.sidebar a:hover{background:#1f2937;color:#fbbf24}
.main{flex:1;padding:15px;min-width:0}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.card{background:#151d2e;padding:15px;border-radius:12px;border:1px solid #1f2a44}
.panel{background:#151d2e;border-radius:12px;padding:15px;border:1px solid #1f2a44;margin-top:12px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:8px;border-bottom:1px solid #1f2a44;text-align:left}
.btn{padding:7px 11px;border-radius:6px;border:0;cursor:pointer;background:#fbbf24}
.btnr{background:#ef4444;color:#fff}.btng{background:#22c55e;color:#fff}
input,textarea{width:100%;padding:8px;margin:5px 0;background:#0b0f1a;border:1px solid #334155;color:#fff;border-radius:8px}
</style></head><body><div class=sidebar><h2 style="color:#fbbf24;margin:0">CODEX</h2><small>ADMIN PANEL</small>
<a href=/admin/>Dashboard</a><a href=/admin/users>Users</a><a href=/admin/deposits>Deposits</a><a href=/admin/withdrawals>Withdrawals</a><a href=/admin/plans>Plans</a><a href=/admin/notify>Notify</a><a href=/admin/settings>Settings</a><a href=/admin/logout style="color:#ef4444">Logout</a></div><div class=main>"""
BOT="</div></body></html>"
def page(c): return render_template_string(TOP+c+BOT)
@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('u',''); p=request.form.get('p','')
        con=db(); r=con.execute("SELECT * FROM users WHERE (name=? OR phone=?) AND password=?", (u,u,p)).fetchone()
        is_admin = r and (r["id"]==1 or ("is_admin" in r.keys() and r["is_admin"]==1))
        con.close()
        if is_admin:
            session['is_admin']=True; session['uid']=r["id"]
            return redirect('/admin/')
        return page("<div class=panel><h3>Login failed</h3><a href=/admin/login>Retry</a></div>")
    return page("<div class=panel><h3>Admin Login</h3><form method=post><input name=u placeholder=Username/phone><input name=p type=password placeholder=Password><button class=btn>Login</button></form></div>")
@admin_bp.route('/logout')
def logout():
    session.clear(); return redirect('/admin/login')
@admin_bp.route('/')
def dash():
    if guard(): return guard()
    con=db()
    users=con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    dep=con.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='deposit' AND status='approved'").fetchone()[0] if True else 0
    wd=con.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='withdraw' AND status='approved'").fetchone()[0]
    try: act=con.execute("SELECT COUNT(*) FROM investments WHERE active=1").fetchone()[0]
    except: act=0
    con.close()
    c="<div class=cards>"
    c+="<div class=card><h4>Total Users</h4><h1>"+str(users)+"</h1></div>"
    c+="<div class=card><h4>Total Deposits</h4><h1>UGX "+str(dep)+"</h1></div>"
    c+="<div class=card><h4>Total Withdrawals</h4><h1>UGX "+str(wd)+"</h1></div>"
    c+="<div class=card><h4>Active Investments</h4><h1>"+str(act)+"</h1></div></div>"
    c+="<div class=panel><h3>Send Notification to All</h3><form action=/admin/notify method=post><input name=title placeholder=Title><textarea name=msg placeholder=Message></textarea><button class=btn>Send to all users</button></form></div>"
    c+="<div class=panel><h3>Search Users</h3><form action=/admin/users method=get><input name=q placeholder='name or phone'><button class=btn>Search</button></form></div>"
    return page(c)
@admin_bp.route('/users')
def users():
    if guard(): return guard()
    q=request.args.get('q','').strip()
    con=db()
    if q: rows=con.execute("SELECT * FROM users WHERE name LIKE? OR phone LIKE? ORDER BY id DESC LIMIT 100", ("%"+q+"%","%"+q+"%")).fetchall()
    else: rows=con.execute("SELECT * FROM users ORDER BY id DESC LIMIT 100").fetchall()
    con.close()
    h="<div class=panel><h3>Users ("+str(len(rows))+")</h3><table><tr><th>ID</th><th>Name</th><th>Phone</th><th>Balance</th></tr>"
    for r in rows: h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["name"])+"</td><td>"+str(r["phone"])+"</td><td>"+str(r["balance"])+"</td></tr>"
    h+="</table></div>"
    return page(h)
@admin_bp.route('/notify', methods=['GET','POST'])
def notify():
    if guard(): return guard()
    if request.method=='POST':
        title=request.form.get('title',''); msg=request.form.get('msg','')
        full=(title+" - "+msg) if title else msg
        con=db(); users=con.execute("SELECT id FROM users").fetchall()
        now=datetime.datetime.now().isoformat()
        for u in users: con.execute("INSERT INTO notifications(user_id,msg,date) VALUES(?,?,?)", (u["id"], full, now))
        con.commit(); con.close()
        return page("<div class=panel><h3>Sent to "+str(len(users))+" users</h3><a href=/admin/>Back</a></div>")
    return page("<div class=panel><h3>Notify</h3><form method=post><input name=title placeholder=Title><textarea name=msg></textarea><button class=btn>Send</button></form></div>")
@admin_bp.route('/deposits')
def deposits():
    if guard(): return guard()
    con=db(); rows=con.execute("SELECT * FROM transactions WHERE type='deposit' ORDER BY id DESC LIMIT 100").fetchall(); con.close()
    h="<div class=panel><h3>Deposits</h3><table><tr><th>ID</th><th>User</th><th>Amount</th><th>Status</th><th>Action</th></tr>"
    for r in rows: h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["user_id"])+"</td><td>"+str(r["amount"])+"</td><td>"+str(r["status"])+"</td><td><a class=btn href=/admin/dep_ok/"+str(r["id"])+">Approve</a></td></tr>"
    return page(h+"</table></div>")
@admin_bp.route('/withdrawals')
def withdrawals():
    if guard(): return guard()
    con=db(); rows=con.execute("SELECT * FROM transactions WHERE type='withdraw' ORDER BY id DESC LIMIT 100").fetchall(); con.close()
    h="<div class=panel><h3>Withdrawals</h3><table><tr><th>ID</th><th>User</th><th>Amount</th><th>Status</th><th>Action</th></tr>"
    for r in rows: h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["user_id"])+"</td><td>"+str(r["amount"])+"</td><td>"+str(r["status"])+"</td><td><a class=btn href=/admin/wd_ok/"+str(r["id"])+">Approve</a></td></tr>"
    return page(h+"</table></div>")
@admin_bp.route('/dep_ok/<int:i>')
def dep_ok(i):
    if guard(): return guard()
    con=db(); con.execute("UPDATE transactions SET status='approved' WHERE id=?", (i,)); con.commit(); con.close()
    return redirect('/admin/deposits')
@admin_bp.route('/wd_ok/<int:i>')
def wd_ok(i):
    if guard(): return guard()
    con=db(); con.execute("UPDATE transactions SET status='approved' WHERE id=?", (i,)); con.commit(); con.close()
    return redirect('/admin/withdrawals')
@admin_bp.route('/plans')
def plans():
    if guard(): return guard()
    return page("<div class=panel><h3>Plans</h3><p>Manage in app.py - investments table active.</p></div>")
@admin_bp.route('/settings')
def settings():
    if guard(): return guard()
    return page("<div class=panel><h3>Settings</h3><p>OK</p></div>")
