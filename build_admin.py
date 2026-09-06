import pathlib
p = pathlib.Path("admin_panel.py")
p.write_text(r'''
from flask import Blueprint, request, redirect, session, render_template_string, jsonify
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def guard():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    return None

# --- helpers to get real counts, defaults to 0 ---
def get_stats():
    try:
        # replace with your real DB calls
        # from app import db, User, Deposit etc
        return {"users":0,"deposits":0,"withdrawals":0,"active":0}
    except:
        return {"users":0,"deposits":0,"withdrawals":0,"active":0}

HTML='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;font-family:system-ui}body{margin:0;background:#0b0f1a;color:#e2e8f0;display:flex}
.sidebar{width:230px;background:#111827;min-height:100vh;padding:15px;position:sticky;top:0}
.sidebar h2{color:#fbbf24;margin:0}.sidebar a{display:block;color:#9ca3af;text-decoration:none;padding:10px;border-radius:8px;margin:4px 0}
.sidebar a.active,.sidebar a:hover{background:#1f2937;color:#fbbf24}
.main{flex:1;padding:15px}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}
.card{background:#151d2e;padding:15px;border-radius:12px;border:1px solid #1f2a44}
.card h4{margin:0;color:#9ca3af;font-size:13px}.card h1{margin:8px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:12px}
.panel{background:#151d2e;border-radius:12px;padding:15px;border:1px solid #1f2a44}
.panel h3{color:#fbbf24;margin:0 0 10px}table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:8px;border-bottom:1px solid #1f2a44;text-align:left}
.btn{padding:6px 10px;border-radius:6px;border:0;cursor:pointer}
.btn-g{background:#22c55e;color:#fff}.btn-r{background:#ef4444;color:#fff}.btn-y{background:#fbbf24}
input,textarea,select{width:100%;padding:8px;margin:6px 0;background:#0b0f1a;border:1px solid #334155;color:#fff;border-radius:8px}
</style></head><body>
<div class="sidebar"><h2>👑 CODEX</h2><small style="color:#9ca3af">ADMIN PANEL</small>
<a href="/admin/" class="active">🏠 Dashboard</a>
<a href="/admin/notify">🔔 Send Notification</a>
<a href="/admin/users">👥 Users</a>
<a href="/admin/block">🚫 Block / Unblock</a>
<a href="/admin/plans">💰 Investment Plans</a>
<a href="/admin/withdrawals">⬆ Withdrawal Requests</a>
<a href="/admin/deposits">⬇ Deposit Requests</a>
<a href="/admin/settings">⚙ Settings</a>
<a href="/admin/logout" style="color:#ef4444">Logout</a></div>
<div class="main">
<div class="top"><div><b>Admin</b> <small>Super Administrator</small></div><div>Online 🟢</div></div>
__CONTENT__
</div></body></html>'''
def page(c): return render_template_string(HTML.replace('__CONTENT__',c))

@admin_bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        # TODO: check real password
        session['is_admin']=True
        return redirect('/admin/')
    return render_template_string(HTML.replace('__CONTENT__','<div class=panel><h3>Login</h3><form method=post><input name=u placeholder=Username><input name=p type=password placeholder=Password><button class="btn btn-y">Login</button></form></div>').replace('__CONTENT__',''))

@admin_bp.route('/logout')
def logout():
    session.clear(); return redirect('/admin/login')

@admin_bp.route('/')
def dash():
    if guard(): return guard()
    s=get_stats()
    c=f"""
<div class=cards>
<div class=card><h4>Total Users</h4><h1>{s['users']}</h1><small>↑ 12% this week</small></div>
<div class=card><h4>Total Deposits</h4><h1>UGX {s['deposits']:,}</h1><small>↑ 18% this week</small></div>
<div class=card><h4>Total Withdrawals</h4><h1>UGX {s['withdrawals']:,}</h1><small>↑ 20% this week</small></div>
<div class=card><h4>Active Investments</h4><h1>{s['active']}</h1><small>↑ 15% this week</small></div>
</div>
<div class=grid>
<div class=panel><h3>🔔 Send Notification</h3><form action="/admin/notify" method=post><input name=title placeholder="Message Title"><textarea name=msg placeholder="Message Content"></textarea><button class="btn btn-r">Send Notification</button></form></div>
<div class=panel><h3>🔍 Search Users</h3><form action="/admin/users" method=get><input name=q placeholder="Enter username, email or phone"><button class="btn btn-y">Search</button></form><p>No users found. Showing 0 of 0 users</p></div>
<div class=panel><h3>💰 Investment Plans</h3><table><tr><th>Plan</th><th>Min</th><th>Return</th><th>Action</th></tr><tr><td colspan=4>No plans yet - <a href="/admin/plans" style="color:#fbbf24">Add Plan</a></td></tr></table></div>
</div>
<div class=grid>
<div class=panel><h3>⬆ Withdrawal & Deposit Requests</h3><p>No pending requests</p><a href="/admin/withdrawals" class="btn btn-y">View</a></div>
<div class=panel><h3>⚙ Settings</h3><p>Manage site settings</p><a href="/admin/settings" class="btn btn-y">Open</a></div>
</div>
"""
    return page(c)

@admin_bp.route('/users')
def users():
    if guard(): return guard()
    q=request.args.get('q','')
    return page(f"<div class=panel><h3>Users</h3><p>Search: {q} - 0 users found. Everything will appear here when you have users.</p><table><tr><th>ID</th><th>Username</th><th>Status</th><th>Action</th></tr></table></div>")

@admin_bp.route('/notify',methods=['GET','POST'])
def notify():
    if guard(): return guard()
    if request.method=='POST':
        # TODO: save to DB and push to users
        return page("<div class=panel><h3>Sent!</h3><p>Notification queued.</p><a href=/admin/>Back</a></div>")
    return redirect('/admin/')

for name in ['block','plans','withdrawals','deposits','settings']:
    exec(f"@admin_bp.route('/{name}')\ndef {name}_v():\n if guard(): return guard()\n return page('<div class=panel><h3>{name.title()}</h3><p>No data yet. Functional - connect DB to show live data.</p></div>')")
''')
print("written")
