from flask import Blueprint, request, redirect, session, render_template_string
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
def guard():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    return None
def get_stats():
    return {"users":0,"deposits":0,"withdrawals":0,"active":0}
BASE_TOP = """<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1"><style>
body{margin:0;background:#0b0f1a;color:#e2e8f0;display:flex;font-family:system-ui}
.sidebar{width:230px;background:#111827;min-height:100vh;padding:15px}
.sidebar a{display:block;color:#9ca3af;text-decoration:none;padding:10px;border-radius:8px}
.sidebar a:hover{background:#1f2937;color:#fbbf24}
.main{flex:1;padding:15px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.card{background:#151d2e;padding:15px;border-radius:12px;border:1px solid #1f2a44}
.panel{background:#151d2e;border-radius:12px;padding:15px;border:1px solid #1f2a44;margin-top:12px}
.btn{padding:8px 12px;border-radius:6px;border:0;cursor:pointer}
</style></head><body>
<div class=sidebar><h2 style="color:#fbbf24">CODEX</h2><small>ADMIN PANEL</small>
<a href=/admin/>Dashboard</a><a href=/admin/users>Users</a><a href=/admin/deposits>Deposits</a><a href=/admin/withdrawals>Withdrawals</a><a href=/admin/plans>Plans</a><a href=/admin/settings>Settings</a><a href=/admin/logout>Logout</a></div><div class=main>"""
BASE_BOT = "</div></body></html>"
def page(c):
    return render_template_string(BASE_TOP + c + BASE_BOT)
@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['is_admin'] = True
        return redirect('/admin/')
    return page("<div class=panel><h3>Login</h3><form method=post><input name=u placeholder=Username style='width:100%;padding:8px;margin:5px 0'><input name=p type=password placeholder=Password style='width:100%;padding:8px'><button class=btn>Login</button></form></div>")
@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/admin/login')
@admin_bp.route('/')
def dash():
    g = guard()
    if g: return g
    s = get_stats()
    html = "<div class=cards>"
    html += "<div class=card><h4>Total Users</h4><h1>" + str(s['users']) + "</h1></div>"
    html += "<div class=card><h4>Total Deposits</h4><h1>UGX " + str(s['deposits']) + "</h1></div>"
    html += "<div class=card><h4>Total Withdrawals</h4><h1>UGX " + str(s['withdrawals']) + "</h1></div>"
    html += "<div class=card><h4>Active Investments</h4><h1>" + str(s['active']) + "</h1></div>"
    html += "</div>"
    html += "<div class=panel><h3>Send Notification</h3><form action=/admin/notify method=post><input name=title placeholder='Title' style='width:100%;padding:8px'><textarea name=msg placeholder='Message' style='width:100%;padding:8px'></textarea><button class=btn>Send</button></form></div>"
    html += "<div class=panel><h3>Search Users</h3><p>Showing 0 of 0 users - no data yet</p></div>"
    return page(html)
@admin_bp.route('/users')
def users():
    g = guard()
    if g: return g
    return page("<div class=panel><h3>Users - 0 found</h3><p>Will list real users when you have them.</p></div>")
@admin_bp.route('/notify', methods=['POST'])
def notify():
    g = guard()
    if g: return g
    return page("<div class=panel><h3>Sent</h3><a href=/admin/>Back</a></div>")
@admin_bp.route('/deposits')
def dep():
    g = guard()
    if g: return g
    return page("<div class=panel><h3>Deposits - 0</h3></div>")
@admin_bp.route('/withdrawals')
def wd():
    g = guard()
    if g: return g
    return page("<div class=panel><h3>Withdrawals - 0</h3></div>")
@admin_bp.route('/plans')
def plans():
    g = guard()
    if g: return g
    return page("<div class=panel><h3>Plans</h3><p>No plans yet</p></div>")
@admin_bp.route('/settings')
def settings():
    g = guard()
    if g: return g
    return page("<div class=panel><h3>Settings</h3></div>")
