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
*{box-sizing:border-box}
body{margin:0;background:#0b0f1a;color:#e2e8f0;font-family:system-ui;display:flex;min-height:100vh}
.sidebar{width:230px;background:#111827;min-height:100vh;padding:15px;position:sticky;top:0;height:100vh;flex-shrink:0;transition:transform .3s}
.sidebar a{display:block;color:#9ca3af;text-decoration:none;padding:10px;border-radius:8px;margin:3px 0}
.sidebar a:hover{background:#1f2937;color:#fbbf24}
.main{flex:1;padding:15px;min-width:0;overflow-x:hidden}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.card{background:#151d2e;padding:15px;border-radius:12px;border:1px solid #1f2a44}
.panel{background:#151d2e;border-radius:12px;padding:15px;border:1px solid #1f2a44;margin-top:12px;overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px;min-width:600px}th,td{padding:8px;border-bottom:1px solid #1f2a44;text-align:left;white-space:nowrap}
.btn{padding:7px 11px;border-radius:6px;border:0;cursor:pointer;background:#fbbf24}
.btnr{background:#ef4444;color:#fff}.btng{background:#22c55e;color:#fff}
input,textarea{width:100%;padding:8px;margin:5px 0;background:#0b0f1a;border:1px solid #334155;color:#fff;border-radius:8px}
.topbar{display:none;background:#111827;padding:10px 15px;position:sticky;top:0;z-index:100;align-items:center;justify-content:space-between}
.hamburger{background:none;border:0;color:#fbbf24;font-size:24px;cursor:pointer}
@media(max-width:768px){
body{flex-direction:column}
.topbar{display:flex}
.sidebar{position:fixed;left:0;top:0;z-index:99;transform:translateX(-100%);width:250px}
.sidebar.open{transform:translateX(0)}
.main{padding:10px}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:98}
.overlay.show{display:block}
}
</style></head><body>
<div class=topbar><span style="color:#fbbf24;font-weight:800">CODEX ADMIN</span><button class=hamburger onclick="document.querySelector('.sidebar').classList.toggle('open');document.querySelector('.overlay').classList.toggle('show')">☰</button></div>
<div class=overlay onclick="document.querySelector('.sidebar').classList.remove('open');this.classList.remove('show')"></div>
<div class=sidebar><h2 style="color:#fbbf24;margin:0">CODEX</h2><small>ADMIN PANEL</small>
<a href=/admin/>Dashboard</a><a href=/admin/users>Users</a><a href=/admin/deposits>Deposits</a><a href=/admin/withdrawals>Withdrawals</a><a href=/admin/plans2>Plans</a><a href=/admin/notify>Notify</a><a href=/admin/chats>Chats</a><a href=/admin/settings>Settings</a><a href=/admin/logout style="color:#ef4444">Logout</a></div><div class=main>"""
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
    for r in rows:
        blk=r["blocked"] if "blocked" in r.keys() else 0
        h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["name"])+"</td><td>"+str(r["phone"])+"</td><td>UGX "+str(r["balance"])+"</td><td><a class=btn href=/admin/user_block/"+str(r["id"])+">"+("Unblock" if blk else "Block")+"</a></td></tr>"
    h=h.replace("<th>Balance</th>","<th>Balance</th><th>Action</th>")
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
    con=db()
    try: rows=con.execute("SELECT d.*, u.name as uname FROM deposits d LEFT JOIN users u ON u.id=d.user_id ORDER BY d.id DESC LIMIT 200").fetchall()
    except: rows=[]
    con.close()
    h="<div class=panel><h3>Deposits</h3><table><tr><th>ID</th><th>User</th><th>Amount</th><th>Status</th><th>Action</th></tr>"
    for r in rows: h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["user_id"])+"</td><td>"+str(r["amount"])+"</td><td>"+str(r["status"])+"</td><td><a class=btn href=/admin/dep_ok/"+str(r["id"])+">Approve</a> <a class=btn style=background:#ef4444;color:#fff href=/admin/dep_no/"+str(r["id"])+">Reject</a></td></tr>"
    return page(h+"</table></div>")
@admin_bp.route('/withdrawals')
def withdrawals():
    if guard(): return guard()
    con=db(); rows=con.execute("SELECT * FROM transactions WHERE type='withdraw' ORDER BY id DESC LIMIT 100").fetchall(); con.close()
    h="<div class=panel><h3>Withdrawals</h3><table><tr><th>ID</th><th>User</th><th>Amount</th><th>Status</th><th>Action</th></tr>"
    for r in rows: h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["user_id"])+"</td><td>"+str(r["amount"])+"</td><td>"+str(r["status"])+"</td><td><a class=btn href=/admin/wd_ok/"+str(r["id"])+">Approve</a> <a class=btn style=background:#ef4444;color:#fff href=/admin/wd_no/"+str(r["id"])+">Reject</a></td></tr>"
    return page(h+"</table></div>")
@admin_bp.route('/dep_ok/<int:i>')
def dep_ok(i):
    if guard(): return guard()
    con=db(); r=con.execute("SELECT * FROM deposits WHERE id=?",(i,)).fetchone()
    con.execute("UPDATE deposits SET status='approved' WHERE id=?",(i,))
    con.execute("INSERT INTO transactions(user_id,type,amount,status) VALUES(?,?,?,?)",(r["user_id"],"deposit",r["amount"],"approved") if r else (0,"deposit",0,"approved"))
    con.execute("UPDATE users SET balance=balance+? WHERE id=?",(r["amount"],r["user_id"]) if r else (0,0))
    con.commit(); con.close()
    return redirect('/admin/deposits')
@admin_bp.route('/wd_ok/<int:i>')
def wd_ok(i):
    if guard(): return guard()
    con=db(); con.execute("UPDATE withdrawals SET status='approved' WHERE id=?",(i,))
    r=con.execute("SELECT * FROM withdrawals WHERE id=?",(i,)).fetchone()
    con.execute("INSERT INTO transactions(user_id,type,amount,status) VALUES(?,?,?,?)",(r["user_id"],"withdraw",r["amount"],"approved") if r else (0,"withdraw",0,"approved"))
    con.commit(); con.close()
    return redirect('/admin/withdrawals')
@admin_bp.route('/plans')
def plans():
    if guard(): return guard()
    return page("<div class=panel><h3>Plans</h3><p>Manage in app.py - investments table active.</p></div>")
@admin_bp.route('/settings')
def settings():
    if guard(): return guard()
    return page("<div class=panel><h3>Settings</h3><p>OK</p></div>")

# --- Editable Plans v2 ---
def _ensure_plans():
    con=db()
    con.execute("CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY, name TEXT, min_amount INT, return_pct INT, duration_days INT)")
    if con.execute("SELECT COUNT(*) FROM plans").fetchone()[0]==0:
        con.execute("INSERT INTO plans(name,min_amount,return_pct,duration_days) VALUES('Starter',50000,20,7)")
        con.execute("INSERT INTO plans(name,min_amount,return_pct,duration_days) VALUES('Pro',200000,35,14)")
        con.commit()
    con.close()
_ensure_plans()

@admin_bp.route('/plans2')
def plans2():
    if guard(): return guard()
    con=db(); rows=con.execute("SELECT * FROM plans ORDER BY min_amount").fetchall(); con.close()
    h="<div class=panel><h3>Investment Plans - Editable</h3><a class=btn href=/admin/plans2_add>Add Plan</a><table><tr><th>Name</th><th>Min UGX</th><th>Return %</th><th>Days</th><th>Action</th></tr>"
    for r in rows:
        h+="<tr><td>"+str(r["name"])+"</td><td>"+str(r["min_amount"])+"</td><td>"+str(r["return_pct"])+"%</td><td>"+str(r["duration_days"])+"</td><td><a class=btn href=/admin/plans2_edit/"+str(r["id"])+">Edit</a> <a class=btnr href=/admin/plans2_del/"+str(r["id"])+">Del</a></td></tr>"
    return page(h+"</table></div>")

@admin_bp.route('/plans_add', methods=['GET','POST'])
def plans_add():
    if guard(): return guard()
    if request.method=='POST':
        con=db(); con.execute("INSERT INTO plans(name,min_amount,return_pct,duration_days) VALUES(?,?,?,?)",(request.form.get('name'),int(request.form.get('min',0)),int(request.form.get('pct',0)),int(request.form.get('days',0)))); con.commit(); con.close()
        return redirect('/admin/plans22')
    return page("<div class=panel><h3>Add Plan</h3><form method=post><input name=name placeholder='Plan name'><input name=min type=number placeholder='Min price UGX'><input name=pct type=number placeholder='Return %'><input name=days type=number placeholder='Duration days'><button class=btn>Save</button></form></div>")

@admin_bp.route('/plans_edit/<int:pid>', methods=['GET','POST'])
def plans_edit(pid):
    if guard(): return guard()
    con=db()
    if request.method=='POST':
        con.execute("UPDATE plans SET name=?, min_amount=?, return_pct=?, duration_days=? WHERE id=?",(request.form.get('name'),int(request.form.get('min',0)),int(request.form.get('pct',0)),int(request.form.get('days',0)),pid)); con.commit(); con.close()
        return redirect('/admin/plans22')
    r=con.execute("SELECT * FROM plans WHERE id=?",(pid,)).fetchone(); con.close()
    return page(f"<div class=panel><h3>Edit {r['name']}</h3><form method=post><input name=name value=\"{r['name']}\"><input name=min type=number value=\"{r['min_amount']}\"><input name=pct type=number value=\"{r['return_pct']}\"><input name=days type=number value=\"{r['duration_days']}\"><button class=btn>Update Price</button></form></div>")

@admin_bp.route('/plans_del/<int:pid>')
def plans_del(pid):
    if guard(): return guard()
    con=db(); con.execute("DELETE FROM plans WHERE id=?",(pid,)); con.commit(); con.close()
    return redirect('/admin/plans22')
@admin_bp.route('/dep_no/<int:i>')
def dep_no(i):
    if guard(): return guard()
    con=db(); con.execute("UPDATE transactions SET status='rejected' WHERE id=?", (i,)); con.commit(); con.close()
    return redirect('/admin/deposits')

@admin_bp.route('/wd_no/<int:i>')
def wd_no(i):
    if guard(): return guard()
    con=db()
    r=con.execute("SELECT * FROM transactions WHERE id=?", (i,)).fetchone()
    if r and r["status"]!="approved":
        con.execute("UPDATE users SET balance=balance+? WHERE id=?", (r["amount"], r["user_id"]))
    con.execute("UPDATE transactions SET status='rejected' WHERE id=?", (i,))
    con.commit(); con.close()
    return redirect('/admin/withdrawals')

@admin_bp.route('/user_block/<int:uid>')
def user_block(uid):
    if guard(): return guard()
    con=db()
    try: con.execute("ALTER TABLE users ADD COLUMN blocked INT DEFAULT 0")
    except: pass
    cur=con.execute("SELECT blocked FROM users WHERE id=?", (uid,)).fetchone()
    nb=0 if cur["blocked"] else 1
    con.execute("UPDATE users SET blocked=? WHERE id=?", (nb, uid))
    con.commit(); con.close()
    return redirect('/admin/users')

# Chat reply
@admin_bp.route('/chats')
def chats():
    if guard(): return guard()
    con=db()
    con.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,message TEXT,admin_reply TEXT,image TEXT,created_at TEXT)")
    try:
        rows=con.execute("SELECT m.*, COALESCE(u.name, u.phone, 'User-'||m.user_id) as name FROM messages m LEFT JOIN users u ON u.id=m.user_id ORDER BY m.id DESC LIMIT 200").fetchall()
    except Exception as e:
        print("chats error",e)
        rows=con.execute("SELECT id, user_id, message, admin_reply, image, created_at, 'User-'||user_id as name FROM messages ORDER BY id DESC LIMIT 200").fetchall()
    con.close()
    h="<div class=panel><h3>User Messages ("+str(len(rows))+")</h3><table><tr><th>User</th><th>Msg</th><th>Image</th><th>Time</th><th>Reply</th></tr>"
    for r in rows:
        img=f"<a href=/{r['image']} target=_blank><img src=/{r['image']} style='width:60px'></a>" if r['image'] else "-"
        h+=f"<tr><td>{r['name']}</td><td>{r['message'] or ''}</td><td>{img}</td><td>{r['created_at'] or ''}</td><td><form action=/admin/reply_chat/{r['id']} method=post><input name=reply value='{r['admin_reply'] or ''}' placeholder='Reply'><button class=btn>Reply</button></form></td></tr>"
    return page(h+"</table></div>")

@admin_bp.route('/reply/<int:mid>', methods=['POST'])
def reply(mid):
    if guard(): return guard()
    con=db(); con.execute("UPDATE messages SET admin_reply=? WHERE id=?", (request.form.get('reply',''), mid)); con.commit(); con.close()
    return redirect('/admin/chats')

@admin_bp.route('/plans_preview')
def plans_preview():
    if guard(): return guard()
    con=db()
    rows=con.execute("SELECT * FROM plans ORDER BY min_amount").fetchall()
    con.close()
    h="<div class=panel><h3>Preview - As Users See</h3><div style='display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px'>"
    for r in rows:
        d=dict(r)
        img=d.get('image','')
        price=d.get('price') or d.get('min_amount')
        lim=d.get('limit_qty') or '-'
        imgtag=f"<img src='{img}' style='width:100%;height:140px;object-fit:cover;border-radius:12px'>" if img else "<div style='width:100%;height:140px;background:#eee;border-radius:12px;display:flex;align-items:center;justify-content:center'>no image</div>"
        h+=f"<div style='border:1px solid #ddd;border-radius:12px;padding:12px;background:#fff'>{imgtag}<h4>{d.get('name')}</h4><div>Price: UGX {price}</div><div>{d.get('return_pct')}% in {d.get('duration_days')} days</div><div>Limit: {lim}</div></div>"
    h+="</div><br><a class=btn href=/admin/plans2>Back to table</a></div>"
    return page(h)

@admin_bp.route('/deposits')
def deposits_fixed():
    if guard(): return guard()
    con=db()
    try:
        rows=con.execute("SELECT d.*, u.name as uname FROM deposits d LEFT JOIN users u ON u.id=d.user_id ORDER BY d.id DESC LIMIT 200").fetchall()
    except: rows=[]
    con.close()
    h="<div class=panel><h3>Deposits</h3><table><tr><th>ID</th><th>User</th><th>Amount</th><th>TxID</th><th>Status</th><th>Action</th></tr>"
    for r in rows:
        try:
            h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["uname"] or r["user_id"])+"</td><td>"+str(r["amount"])+"</td><td>"+str(r["txid"] or "")+"</td><td>"+str(r["status"])+"</td><td><a class=btn href=/admin/dep_ok/"+str(r["id"])+">Approve</a> <a class=btn style=background:#ef4444;color:#fff href=/admin/dep_no/"+str(r["id"])+">Reject</a></td></tr>"
        except: pass
    return page(h+"</table></div>")

@admin_bp.route('/withdrawals')
def withdrawals_fixed():
    if guard(): return guard()
    con=db()
    try:
        rows=con.execute("SELECT w.*, u.name as uname FROM withdrawals w LEFT JOIN users u ON u.id=w.user_id ORDER BY w.id DESC LIMIT 200").fetchall()
    except: rows=[]
    con.close()
    h="<div class=panel><h3>Withdrawals</h3><table><tr><th>ID</th><th>User</th><th>Amount</th><th>Phone</th><th>Status</th><th>Action</th></tr>"
    for r in rows:
        try:
            h+="<tr><td>"+str(r["id"])+"</td><td>"+str(r["uname"] or r["user_id"])+"</td><td>"+str(r["amount"])+"</td><td>"+str(r["phone"] or "")+"</td><td>"+str(r["status"])+"</td><td><a class=btn href=/admin/wd_ok/"+str(r["id"])+">Approve</a> <a class=btn style=background:#ef4444;color:#fff href=/admin/wd_no/"+str(r["id"])+">Reject</a></td></tr>"
        except: pass
    return page(h+"</table></div>")
