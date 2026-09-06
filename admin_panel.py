from flask import Blueprint, request, session, redirect, render_template_string, jsonify
import sqlite3, os, time
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
def db():
    c=sqlite3.connect('database.db'); c.row_factory=sqlite3.Row; return c
def ok(): return session.get('is_admin')
def guard():
    if not ok(): return redirect('/admin/login')
    return None
BASE = """<style>body{font-family:system-ui;background:#0f172a;color:#fff;margin:0}.nav{background:#1e293b;padding:12px;display:flex;gap:10px;flex-wrap:wrap}.nav a{color:#94a3b8;text-decoration:none;padding:8px}.wrap{padding:20px;max-width:1000px;margin:auto}.card{background:#1e293b;padding:16px;border-radius:10px;margin:10px 0}</style><div class=nav><a href=/admin>Dashboard</a> <a href=/admin/users>Users</a> <a href=/admin/deposits>Deposits</a> <a href=/admin/withdrawals>Withdrawals</a></div><div class=wrap>{c}</div>"""

@admin_bp.route('/login', methods=['GET','POST'])
def login():
    from flask import request, session, redirect
    if request.method=='POST':
        # TODO: check real admin password here
        session['is_admin']=True
        return redirect('/admin/')
    return '<form method=post><input name=u placeholder=username><input name=p type=password placeholder=password><button>Login</button></form>'
@admin_bp.route('/')
def adm_dash():
    if g:=guard(): return g
    con=db()
    def q(s):
        try: return con.execute(s).fetchone()[0]
        except: return 0
    s=dict(total_users=q("SELECT COUNT(*) FROM users"), active_users=q("SELECT COUNT(*) FROM users WHERE status='active'"), total_deposits=q("SELECT COALESCE(SUM(amount),0) FROM deposits WHERE status='approved'"), total_withdrawals=q("SELECT COALESCE(SUM(amount),0) FROM withdrawals WHERE status='approved'"), pending_deposits=q("SELECT COUNT(*) FROM deposits WHERE status='pending'"), pending_withdrawals=q("SELECT COUNT(*) FROM withdrawals WHERE status='pending'"))
    con.close()
    html="<h2>Dashboard</h2>"+"".join(f"<p>{k}: <b>{v}</b></p>" for k,v in s.items())
    return render_template_string(BASE.format(c=html))

@admin_bp.route('/users')
def adm_users():
    if g:=guard(): return g
    con=db()
    try: users=con.execute("SELECT id,username,phone,email,balance,status FROM users LIMIT 100").fetchall()
    except: users=[]
    con.close()
    h="<h2>Users</h2><form><input name=q placeholder='Search'><button>Search</button></form><table border=1>"
    for u in users: h+=f"<tr><td>{u['id']}</td><td>{u['username']}</td><td>{u['balance']}</td><td>{u['status']}</td><td><a href=/admin/user/{u['id']}>View</a></td></tr>"
    return render_template_string(BASE.format(c=h+"</table>"))

@admin_bp.route('/user/<int:uid>')
def adm_user_view(uid):
    if g:=guard(): return g
    con=db(); u=con.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone(); con.close()
    if not u: return "Not found"
    return render_template_string(BASE.format(c=f"<h2>{u['username']}</h2><p>Phone:{u['phone']} Email:{u['email']} Balance:{u['balance']}</p><a href=/admin/user/{uid}/toggle>Suspend/Activate</a>"))

@admin_bp.route('/user/<int:uid>/toggle')
def adm_user_toggle(uid):
    if g:=guard(): return g
    con=db(); con.execute("UPDATE users SET status=CASE WHEN status='active' THEN 'suspended' ELSE 'active' END WHERE id=?",(uid,)); con.commit(); con.close()
    return redirect('/admin/users')

@admin_bp.route('/deposits')
def adm_deposits():
    if g:=guard(): return g
    con=db()
    try: rows=con.execute("SELECT * FROM deposits ORDER BY id DESC LIMIT 100").fetchall()
    except: rows=[]
    con.close()
    h="<h2>Deposits</h2><table border=1><tr><th>ID</th><th>User</th><th>Amt</th><th>Method</th><th>Status</th><th>Action</th></tr>"
    for r in rows: h+=f"<tr><td>{r['id']}</td><td>{r['user_id']}</td><td>{r['amount']}</td><td>{r['method'] if 'method' in r.keys() else ''}</td><td>{r['status']}</td><td><a href=/admin/deposit/{r['id']}/approve>Approve</a> <a href=/admin/deposit/{r['id']}/reject>Reject</a></td></tr>"
    return render_template_string(BASE.format(c=h+"</table>"))

@admin_bp.route('/deposit/<int:did>/<act>')
def adm_deposit_act(did,act):
    if g:=guard(): return g
    con=db(); con.execute("UPDATE deposits SET status=? WHERE id=?",('approved' if act=='approve' else 'rejected',did))
    if act=='approve':
        d=con.execute("SELECT user_id,amount FROM deposits WHERE id=?",(did,)).fetchone()
        if d: con.execute("UPDATE users SET balance=balance+? WHERE id=?",(d['amount'],d['user_id']))
    con.commit(); con.close(); return redirect('/admin/deposits')

@admin_bp.route('/withdrawals')
def adm_withdrawals():
    if g:=guard(): return g
    con=db()
    try: rows=con.execute("SELECT * FROM withdrawals ORDER BY id DESC LIMIT 100").fetchall()
    except: rows=[]
    con.close()
    h="<h2>Withdrawals</h2><table border=1>"
    for r in rows: h+=f"<tr><td>{r['id']}</td><td>{r['user_id']}</td><td>{r['amount']}</td><td>{r['status']}</td><td><a href=/admin/withdrawal/{r['id']}/approve>Approve</a> <a href=/admin/withdrawal/{r['id']}/reject>Reject</a></td></tr>"
    return render_template_string(BASE.format(c=h+"</table>"))

@admin_bp.route('/withdrawal/<int:wid>/<act>')
def adm_withdrawal_act(wid,act):
    if g:=guard(): return g
    con=db(); con.execute("UPDATE withdrawals SET status=? WHERE id=?",('approved' if act=='approve' else 'rejected',wid)); con.commit(); con.close()
    return redirect('/admin/withdrawals')

@admin_bp.route('/plans', methods=['GET','POST'])
def adm_plans_list():
    if g:=guard(): return g
    con=db(); con.execute("CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY, name TEXT, min_amt REAL, max_amt REAL, duration INTEGER, rate REAL, active INTEGER DEFAULT 1)")
    if request.method=='POST':
        con.execute("INSERT INTO plans(name,min_amt,max_amt,duration,rate) VALUES(?,?,?,?,?)",(request.form['name'],request.form['min'],request.form['max'],request.form['dur'],request.form['rate'])); con.commit()
    plans=con.execute("SELECT * FROM plans").fetchall(); con.close()
    h="<h2>Plans</h2><form method=post><input name=name placeholder=Name><input name=min placeholder=Min><input name=max placeholder=Max><input name=dur placeholder=Days><input name=rate placeholder='Rate %'><button>Create</button></form><table border=1>"
    for p in plans: h+=f"<tr><td>{p['name']}</td><td>{p['min_amt']}-{p['max_amt']}</td><td>{p['rate']}%</td><td><a href=/admin/plan/{p['id']}/toggle>Enable/Disable</a> <a href=/admin/plan/{p['id']}/delete>Delete</a></td></tr>"
    return render_template_string(BASE.format(c=h+"</table>"))

@admin_bp.route('/plan/<int:pid>/<act>')
def adm_plan_act(pid,act):
    if g:=guard(): return g
    con=db()
    if act=='delete': con.execute("DELETE FROM plans WHERE id=?",(pid,))
    else: con.execute("UPDATE plans SET active=CASE WHEN active=1 THEN 0 ELSE 1 END WHERE id=?",(pid,))
    con.commit(); con.close(); return redirect('/admin/plans')

@admin_bp.route('/rewards', methods=['GET','POST'])
def adm_rewards():
    if g:=guard(): return g
    if request.method=='POST':
        con=db(); con.execute("UPDATE users SET balance=balance+? WHERE id=?",(float(request.form['amt']),int(request.form['uid']))); con.commit(); con.close()
        return redirect('/admin/rewards')
    return render_template_string(BASE.format(c="<h2>Rewards</h2><form method=post><input name=uid placeholder=UserID><input name=amt placeholder=Amount><button>Credit Bonus</button></form><p>Daily check-in, referral, promo handled here.</p>"))

@admin_bp.route('/referrals')
def adm_referrals():
    if g:=guard(): return g
    con=db()
    try: rows=con.execute("SELECT referred_by, COUNT(*) c FROM users WHERE referred_by IS NOT NULL GROUP BY referred_by ORDER BY c DESC LIMIT 20").fetchall()
    except: rows=[]
    con.close()
    h="<h2>Top Referrers</h2><table border=1>"
    for r in rows: h+=f"<tr><td>{r['referred_by']}</td><td>{r['c']}</td></tr>"
    return render_template_string(BASE.format(c=h+"</table>"))

@admin_bp.route('/support')
def adm_support():
    if g:=guard(): return g
    return render_template_string(BASE.format(c="<h2>Support Tickets</h2><p>No open tickets. Live chat placeholder.</p>"))

@admin_bp.route('/announce', methods=['GET','POST'])
def adm_announce():
    if g:=guard(): return g
    con=db(); con.execute("CREATE TABLE IF NOT EXISTS announcements(id INTEGER PRIMARY KEY, msg TEXT, created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    if request.method=='POST': con.execute("INSERT INTO announcements(msg) VALUES(?)",(request.form['msg'],)); con.commit()
    rows=con.execute("SELECT * FROM announcements ORDER BY id DESC LIMIT 20").fetchall(); con.close()
    h="<h2>Announcements</h2><form method=post><input name=msg placeholder=Message><button>Publish</button></form>"
    for r in rows: h+=f"<p>{r['msg']}</p>"
    return render_template_string(BASE.format(c=h))

@admin_bp.route('/reports')
def adm_reports():
    if g:=guard(): return g
    return render_template_string(BASE.format(c="<h2>Reports</h2><p>Daily deposits, withdrawals, growth, revenue. Export CSV coming.</p><a href=/admin/reports/csv>Export CSV</a>"))

@admin_bp.route('/reports/csv')
def adm_reports_csv():
    if g:=guard(): return g
    con=db()
    try: rows=con.execute("SELECT * FROM deposits").fetchall()
    except: rows=[]
    con.close()
    csv="id,user_id,amount,status\n"+"\n".join(f"{r['id']},{r['user_id']},{r['amount']},{r['status']}" for r in rows)
    return (csv,200,{'Content-Type':'text/csv','Content-Disposition':'attachment;filename=report.csv'})

@admin_bp.route('/settings', methods=['GET','POST'])
def adm_settings():
    if g:=guard(): return g
    con=db(); con.execute("CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT)")
    if request.method=='POST':
        for k in ['platform_name','currency','min_withdraw','fee','maint_mode']:
            con.execute("INSERT OR REPLACE INTO settings(k,v) VALUES(?,?)",(k,request.form.get(k,'')))
        con.commit()
    rows=dict(con.execute("SELECT k,v FROM settings").fetchall()); con.close()
    def val(k): return rows.get(k,'')
    return render_template_string(BASE.format(c=f"<h2>Settings</h2><form method=post>Platform:<input name=platform_name value='{val('platform_name')}'><br>Currency:<input name=currency value='{val('currency')}'><br>MinWithdraw:<input name=min_withdraw value='{val('min_withdraw')}'><br>Fee:<input name=fee value='{val('fee')}'><br>Maint:<input name=maint_mode value='{val('maint_mode')}'><br><button>Save</button></form>"))

@admin_bp.route('/security')
def adm_security():
    if g:=guard(): return g
    return render_template_string(BASE.format(c="<h2>Security</h2><p>Admin activity log, login history, 2FA placeholder.</p><a href=/admin/logout>Logout all</a>"))
