from flask import Blueprint, request, redirect, session, render_template_string
import sqlite3, datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
DB = "codex700.db"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def guard():
    if not session.get("is_admin"):
        return redirect("/admin/login")
    return None

TOP = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CODEX Admin</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#020817;color:#e6f7ff;
 font-family:Arial,sans-serif;min-height:100vh
}
.sidebar{
 width:250px;position:fixed;left:0;top:0;bottom:0;
 background:linear-gradient(180deg,#06152d,#020817);
 border-right:1px solid rgba(0,190,255,.22);
 padding:20px 14px;z-index:20
}
.brand{display:flex;align-items:center;gap:10px;margin-bottom:28px}
.logo{
 width:44px;height:44px;border-radius:13px;
 display:flex;align-items:center;justify-content:center;
 background:linear-gradient(135deg,#006dff,#00d9ff);
 color:#00111f;font-size:22px;font-weight:900
}
.brand h2{margin:0;font-size:19px;color:#fff}
.brand small{color:#52cfff;font-size:9px;letter-spacing:2px}

.nav a{
 display:block;text-decoration:none;color:#8ca7ba;
 padding:13px 14px;margin:5px 0;border-radius:11px;
 font-size:14px
}
.nav a:hover{
 background:rgba(0,170,255,.12);color:#00d9ff
}
.nav .danger{color:#ff6680}

.main{margin-left:250px;padding:22px;min-height:100vh}
.top{
 display:flex;justify-content:space-between;
 align-items:center;margin-bottom:22px
}
.top h1{margin:0;font-size:24px;color:#fff}
.top p{margin:5px 0;color:#6e94ad;font-size:13px}

.cards{
 display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
 gap:14px
}
.card,.panel{
 background:linear-gradient(145deg,#07162c,#030b17);
 border:1px solid rgba(0,190,255,.18);
 border-radius:17px;padding:17px;
 box-shadow:0 8px 30px rgba(0,0,0,.22)
}
.card small{color:#7394aa}
.card h2{margin:9px 0 0;color:#00e5ff;font-size:23px}
.panel{margin-top:16px}
.panel h3{margin-top:0;color:#fff}

table{
 width:100%;border-collapse:collapse;
 font-size:13px;min-width:650px
}
.table-wrap{overflow-x:auto}
th{
 color:#63859b;font-size:10px;text-transform:uppercase;
 text-align:left;padding:12px;border-bottom:1px solid #15334c
}
td{padding:13px;border-bottom:1px solid #0d2235;color:#d9efff}

input,textarea{
 width:100%;background:#020a15;color:#fff;
 border:1px solid #17425f;border-radius:10px;
 padding:12px;margin:6px 0
}
textarea{min-height:90px}

.btn{
 display:inline-block;text-decoration:none;
 border:0;cursor:pointer;padding:10px 14px;
 border-radius:10px;font-weight:800;
 background:linear-gradient(90deg,#0077ff,#00d9ff);
 color:#00111f
}
.btn-red{
 background:#c92c45;color:#fff
}
.btn-green{
 background:#00a86b;color:#00150d
}
.badge{
 padding:5px 9px;border-radius:20px;
 font-size:10px;font-weight:bold
}
.pending{background:#2b2307;color:#ffd75c}
.approved{background:#062d22;color:#00ff91}
.rejected{background:#330d15;color:#ff7187}

.mobilebar{display:none}

@media(max-width:768px){
 .sidebar{
  transform:translateX(-100%);
  transition:.25s
 }
 .sidebar.open{transform:translateX(0)}
 .main{margin-left:0;padding:14px}
 .mobilebar{
  display:flex;align-items:center;justify-content:space-between;
  background:#06152d;border-bottom:1px solid #12334b;
  padding:13px 15px;position:sticky;top:0;z-index:10
 }
 .hamburger{
  background:none;border:0;color:#00d9ff;font-size:25px
 }
 .overlay{
  display:none;position:fixed;inset:0;
  background:rgba(0,0,0,.6);z-index:15
 }
 .overlay.show{display:block}
}
</style>
</head>
<body>

<div class="mobilebar">
 <b>CODEX ADMIN</b>
 <button class="hamburger" onclick="toggleMenu()">☰</button>
</div>

<div class="overlay" onclick="toggleMenu()"></div>

<div class="sidebar">
 <div class="brand">
  <div class="logo">C</div>
  <div>
   <h2>CODEX</h2>
   <small>CONTROL CENTER</small>
  </div>
 </div>

 <div class="nav">
  <a href="/admin/">🏠 Dashboard</a>
  <a href="/admin/users">👥 Users</a>
  <a href="/admin/deposits">💰 Deposits</a>
  <a href="/admin/withdrawals">💸 Withdrawals</a>
  <a href="/admin/plans2">📈 Investment Plans</a>
  <a href="/admin/notify">🔔 Notifications</a>
  <a href="/admin/chats">💬 User Chats</a>
  <a href="/admin/logout" class="danger">🚪 Logout</a>
 </div>
</div>

<div class="main">
"""

BOT = """
</div>
<script>
function toggleMenu(){
 document.querySelector(".sidebar").classList.toggle("open");
 document.querySelector(".overlay").classList.toggle("show");
}
</script>
</body>
</html>
"""

def page(content, title="Admin Dashboard"):
    return render_template_string(
        TOP + f'<div class="top"><div><h1>{title}</h1><p>CODEX Management Control Center</p></div></div>' + content + BOT
    )

@admin_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("u","").strip()
        p = request.form.get("p","")

        con = db()
        r = con.execute(
            "SELECT * FROM users WHERE (name=? OR phone=?) AND password=?",
            (u,u,p)
        ).fetchone()
        con.close()

        if r and (r["id"] == 1 or ("is_admin" in r.keys() and r["is_admin"] == 1)):
            session["is_admin"] = True
            session["admin"] = True
            session["uid"] = r["id"]
            return redirect("/admin/")

        return render_template_string("""
        <body style="background:#020817;color:white;font-family:Arial;padding:30px">
        <h2>CODEX Admin Login</h2>
        <form method="post">
        <input name="u" placeholder="Username or phone"><br><br>
        <input name="p" type="password" placeholder="Password"><br><br>
        <button>Login</button>
        </form><p style="color:#ff7187">Login failed.</p>
        </body>
        """)

    return render_template_string("""
    <body style="background:#020817;color:white;font-family:Arial;padding:30px">
    <h2>CODEX Admin Login</h2>
    <form method="post">
    <input name="u" placeholder="Username or phone"><br><br>
    <input name="p" type="password" placeholder="Password"><br><br>
    <button>Login</button>
    </form>
    </body>
    """)

@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/admin/login")

@admin_bp.route("/")
def dashboard():
    g = guard()
    if g: return g

    con = db()

    users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    try:
        deposits = con.execute(
            "SELECT COALESCE(SUM(amount),0) FROM deposits WHERE lower(status)='approved'"
        ).fetchone()[0]
    except:
        deposits = 0

    try:
        withdrawals = con.execute(
            "SELECT COALESCE(SUM(amount),0) FROM withdrawals WHERE lower(status)='approved'"
        ).fetchone()[0]
    except:
        withdrawals = 0

    try:
        active = con.execute(
            "SELECT COUNT(*) FROM investments WHERE active=1"
        ).fetchone()[0]
    except:
        active = 0

    con.close()

    c = '<div class="cards">'
    c += f'<div class="card"><small>👥 TOTAL USERS</small><h2>{users}</h2></div>'
    c += f'<div class="card"><small>💰 APPROVED DEPOSITS</small><h2>UGX {deposits:,}</h2></div>'
    c += f'<div class="card"><small>💸 APPROVED WITHDRAWALS</small><h2>UGX {withdrawals:,}</h2></div>'
    c += f'<div class="card"><small>📈 ACTIVE INVESTMENTS</small><h2>{active}</h2></div>'
    c += '</div>'

    c += """
    <div class="panel">
    <h3>🔔 Send Notification to All Users</h3>
    <form action="/admin/notify" method="post">
    <input name="title" placeholder="Notification title">
    <textarea name="msg" placeholder="Write notification message"></textarea>
    <button class="btn">Send Notification</button>
    </form>
    </div>

    <div class="panel">
    <h3>🔎 Search Users</h3>
    <form action="/admin/users" method="get">
    <input name="q" placeholder="Search by name or phone">
    <button class="btn">Search User</button>
    </form>
    </div>
    """

    return page(c, "Dashboard")

@admin_bp.route("/users")
def users():
    g = guard()
    if g: return g

    q = request.args.get("q","").strip()
    con = db()

    try:
        con.execute("ALTER TABLE users ADD COLUMN blocked INTEGER DEFAULT 0")
        con.commit()
    except:
        pass

    if q:
        rows = con.execute(
            "SELECT * FROM users WHERE name LIKE ? OR phone LIKE ? ORDER BY id DESC LIMIT 200",
            ("%"+q+"%","%"+q+"%")
        ).fetchall()
    else:
        rows = con.execute(
            "SELECT * FROM users ORDER BY id DESC LIMIT 200"
        ).fetchall()

    con.close()

    h = """
    <div class="panel">
    <form method="get">
    <input name="q" value="{{q}}" placeholder="Search name or phone">
    <button class="btn">Search</button>
    </form>
    <div class="table-wrap">
    <table>
    <tr><th>ID</th><th>User</th><th>Phone</th><th>Balance</th><th>Status</th><th>Action</th></tr>
    """

    for r in rows:
        blocked = r["blocked"] if "blocked" in r.keys() else 0
        status = "BLOCKED" if blocked else "ACTIVE"
        cls = "rejected" if blocked else "approved"
        action = "Unblock" if blocked else "Block"

        h += f"""
        <tr>
        <td>{r["id"]}</td>
        <td>{r["name"] or "-"}</td>
        <td>{r["phone"] or "-"}</td>
        <td>UGX {int(r["balance"] or 0):,}</td>
        <td><span class="badge {cls}">{status}</span></td>
        <td><a class="btn {'btn-green' if blocked else 'btn-red'}"
        href="/admin/user_block/{r["id"]}">{action}</a></td>
        </tr>
        """

    h += "</table></div></div>"
    return page(h, "Users")

@admin_bp.route("/user_block/<int:uid>")
def user_block(uid):
    g = guard()
    if g: return g

    con = db()

    try:
        con.execute("ALTER TABLE users ADD COLUMN blocked INTEGER DEFAULT 0")
    except:
        pass

    r = con.execute(
        "SELECT blocked FROM users WHERE id=?",(uid,)
    ).fetchone()

    if r:
        new_status = 0 if r["blocked"] else 1
        con.execute(
            "UPDATE users SET blocked=? WHERE id=?",
            (new_status,uid)
        )

    con.commit()
    con.close()
    return redirect("/admin/users")

@admin_bp.route("/deposits")
def deposits():
    g = guard()
    if g: return g

    con = db()

    try:
        rows = con.execute("""
        SELECT d.*, u.name, u.phone
        FROM deposits d
        LEFT JOIN users u ON u.id=d.user_id
        ORDER BY d.id DESC LIMIT 200
        """).fetchall()
    except:
        rows = []

    con.close()

    h = '<div class="panel"><div class="table-wrap"><table>'
    h += '<tr><th>ID</th><th>User</th><th>Phone</th><th>Amount</th><th>TxID</th><th>Screenshot</th><th>Status</th><th>Action</th></tr>'

    for r in rows:
        status = (r["status"] or "pending").lower()
        cls = "approved" if status=="approved" else ("rejected" if status=="rejected" else "pending")

        image = "-"
        if r["screenshot"]:
            image = f'<a class="btn" href="/static/uploads/{r["screenshot"]}" target="_blank">View</a>'

        actions = "-"
        if status == "pending":
            actions = f'''
            <a class="btn btn-green" href="/admin/dep_ok/{r["id"]}">Approve</a>
            <a class="btn btn-red" href="/admin/dep_no/{r["id"]}">Reject</a>
            '''

        h += f"""
        <tr>
        <td>{r["id"]}</td>
        <td>{r["name"] or "User-"+str(r["user_id"])}</td>
        <td>{r["phone"] or r["airtel"] or "-"}</td>
        <td>UGX {int(r["amount"] or 0):,}</td>
        <td>{r["txid"] or "-"}</td>
        <td>{image}</td>
        <td><span class="badge {cls}">{status.upper()}</span></td>
        <td>{actions}</td>
        </tr>
        """

    h += "</table></div></div>"
    return page(h, "Deposit Requests")

@admin_bp.route("/dep_ok/<int:i>")
def dep_ok(i):
    g = guard()
    if g: return g

    con = db()
    r = con.execute(
        "SELECT * FROM deposits WHERE id=?",(i,)
    ).fetchone()

    if r and (r["status"] or "").lower() == "pending":
        con.execute(
            "UPDATE deposits SET status='approved' WHERE id=?",(i,)
        )
        con.execute(
            "UPDATE users SET balance=balance+? WHERE id=?",
            (r["amount"],r["user_id"])
        )
        con.execute(
            "INSERT INTO transactions(user_id,type,amount,status,date,ref) VALUES(?,?,?,?,?,?)",
            (
                r["user_id"],
                "deposit",
                r["amount"],
                "approved",
                datetime.datetime.now().isoformat(),
                r["txid"]
            )
        )

    con.commit()
    con.close()
    return redirect("/admin/deposits")

@admin_bp.route("/dep_no/<int:i>")
def dep_no(i):
    g = guard()
    if g: return g

    con = db()
    con.execute(
        "UPDATE deposits SET status='rejected' WHERE id=? AND lower(status)='pending'",
        (i,)
    )
    con.commit()
    con.close()
    return redirect("/admin/deposits")

@admin_bp.route("/withdrawals")
def withdrawals():
    g = guard()
    if g: return g

    con = db()

    try:
        rows = con.execute("""
        SELECT w.*, u.name, u.phone
        FROM withdrawals w
        LEFT JOIN users u ON u.id=w.user_id
        ORDER BY w.id DESC LIMIT 200
        """).fetchall()
    except:
        rows = []

    con.close()

    h = '<div class="panel"><div class="table-wrap"><table>'
    h += '<tr><th>ID</th><th>User</th><th>Phone</th><th>Amount</th><th>Status</th><th>Action</th></tr>'

    for r in rows:
        status = (r["status"] or "pending").lower()
        cls = "approved" if status=="approved" else ("rejected" if status=="rejected" else "pending")

        actions = "-"
        if status == "pending":
            actions = f'''
            <a class="btn btn-green" href="/admin/wd_ok/{r["id"]}">Approve</a>
            <a class="btn btn-red" href="/admin/wd_no/{r["id"]}">Reject</a>
            '''

        h += f"""
        <tr>
        <td>{r["id"]}</td>
        <td>{r["name"] or "User-"+str(r["user_id"])}</td>
        <td>{r["phone"] or "-"}</td>
        <td>UGX {int(r["amount"] or 0):,}</td>
        <td><span class="badge {cls}">{status.upper()}</span></td>
        <td>{actions}</td>
        </tr>
        """

    h += "</table></div></div>"
    return page(h, "Withdrawal Requests")

@admin_bp.route("/wd_ok/<int:i>")
def wd_ok(i):
    g = guard()
    if g: return g

    con = db()

    try:
        r = con.execute(
            "SELECT * FROM withdrawals WHERE id=?",(i,)
        ).fetchone()

        if r and (r["status"] or "").lower() == "pending":
            con.execute(
                "UPDATE withdrawals SET status='approved' WHERE id=?",(i,)
            )

            con.execute(
                "INSERT INTO transactions(user_id,type,amount,status,date,ref) VALUES(?,?,?,?,?,?)",
                (
                    r["user_id"],
                    "withdraw",
                    r["amount"],
                    "approved",
                    datetime.datetime.now().isoformat(),
                    r["phone"] or ""
                )
            )

        con.commit()
    except:
        pass

    con.close()
    return redirect("/admin/withdrawals")

@admin_bp.route("/wd_no/<int:i>")
def wd_no(i):
    g = guard()
    if g: return g

    con = db()

    try:
        r = con.execute(
            "SELECT * FROM withdrawals WHERE id=?",(i,)
        ).fetchone()

        if r and (r["status"] or "").lower() == "pending":
            con.execute(
                "UPDATE withdrawals SET status='rejected' WHERE id=?",(i,)
            )

            con.execute(
                "UPDATE users SET balance=balance+? WHERE id=?",
                (r["amount"],r["user_id"])
            )

        con.commit()
    except:
        pass

    con.close()
    return redirect("/admin/withdrawals")

@admin_bp.route("/notify", methods=["GET","POST"])
def notify():
    g = guard()
    if g: return g

    if request.method == "POST":
        title = request.form.get("title","").strip()
        msg = request.form.get("msg","").strip()
        full = (title + " - " + msg).strip(" -")

        con = db()
        users = con.execute("SELECT id FROM users").fetchall()
        now = datetime.datetime.now().isoformat()

        for u in users:
            con.execute(
                "INSERT INTO notifications(user_id,msg,date) VALUES(?,?,?)",
                (u["id"],full,now)
            )

        con.commit()
        con.close()

        return redirect("/admin/")

    return page("""
    <div class="panel">
    <h3>Send Notification</h3>
    <form method="post">
    <input name="title" placeholder="Notification title">
    <textarea name="msg" placeholder="Message"></textarea>
    <button class="btn">Send to All Users</button>
    </form>
    </div>
    ""","Notifications")

def ensure_plans():
    con = db()
    con.execute("""
    CREATE TABLE IF NOT EXISTS plans(
        id INTEGER PRIMARY KEY,
        name TEXT,
        min_amount INTEGER,
        return_pct INTEGER,
        duration_days INTEGER
    )
    """)
    con.commit()
    con.close()

ensure_plans()

@admin_bp.route("/plans2")
def plans2():
    g = guard()
    if g: return g

    con = db()
    rows = con.execute(
        "SELECT * FROM plans ORDER BY min_amount"
    ).fetchall()
    con.close()

    h = '<div class="panel"><a class="btn" href="/admin/plans_add">+ Add Plan</a><div class="table-wrap"><table>'
    h += '<tr><th>Name</th><th>Minimum</th><th>Return</th><th>Days</th><th>Action</th></tr>'

    for r in rows:
        h += f"""
        <tr>
        <td>{r["name"]}</td>
        <td>UGX {int(r["min_amount"]):,}</td>
        <td>{r["return_pct"]}%</td>
        <td>{r["duration_days"]}</td>
        <td>
        <a class="btn" href="/admin/plans_edit/{r["id"]}">Edit</a>
        <a class="btn btn-red" href="/admin/plans_del/{r["id"]}">Delete</a>
        </td>
        </tr>
        """

    h += '</table></div></div>'
    return page(h,"Investment Plans")

@admin_bp.route("/plans_add", methods=["GET","POST"])
def plans_add():
    g = guard()
    if g: return g

    if request.method == "POST":
        con = db()
        con.execute(
            "INSERT INTO plans(name,min_amount,return_pct,duration_days) VALUES(?,?,?,?)",
            (
                request.form.get("name"),
                int(request.form.get("min",0)),
                int(request.form.get("pct",0)),
                int(request.form.get("days",0))
            )
        )
        con.commit()
        con.close()
        return redirect("/admin/plans2")

    return page("""
    <div class="panel">
    <h3>Add Investment Plan</h3>
    <form method="post">
    <input name="name" placeholder="Plan name">
    <input name="min" type="number" placeholder="Minimum amount">
    <input name="pct" type="number" placeholder="Return percentage">
    <input name="days" type="number" placeholder="Duration in days">
    <button class="btn">Save Plan</button>
    </form>
    </div>
    ""","Add Plan")

@admin_bp.route("/plans_edit/<int:pid>", methods=["GET","POST"])
def plans_edit(pid):
    g = guard()
    if g: return g

    con = db()

    if request.method == "POST":
        con.execute(
            "UPDATE plans SET name=?,min_amount=?,return_pct=?,duration_days=? WHERE id=?",
            (
                request.form.get("name"),
                int(request.form.get("min",0)),
                int(request.form.get("pct",0)),
                int(request.form.get("days",0)),
                pid
            )
        )
        con.commit()
        con.close()
        return redirect("/admin/plans2")

    r = con.execute(
        "SELECT * FROM plans WHERE id=?",(pid,)
    ).fetchone()
    con.close()

    if not r:
        return redirect("/admin/plans2")

    return page(f"""
    <div class="panel">
    <h3>Edit {r["name"]}</h3>
    <form method="post">
    <input name="name" value="{r["name"]}">
    <input name="min" type="number" value="{r["min_amount"]}">
    <input name="pct" type="number" value="{r["return_pct"]}">
    <input name="days" type="number" value="{r["duration_days"]}">
    <button class="btn">Update Plan</button>
    </form>
    </div>
    ""","Edit Plan")

@admin_bp.route("/plans_del/<int:pid>")
def plans_del(pid):
    g = guard()
    if g: return g

    con = db()
    con.execute("DELETE FROM plans WHERE id=?",(pid,))
    con.commit()
    con.close()
    return redirect("/admin/plans2")

@admin_bp.route("/chats")
def chats():
    g = guard()
    if g: return g

    con = db()
    con.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        admin_reply TEXT,
        image TEXT,
        created_at TEXT
    )
    """)

    rows = con.execute("""
    SELECT m.*, COALESCE(u.name,u.phone,'User-'||m.user_id) AS name
    FROM messages m
    LEFT JOIN users u ON u.id=m.user_id
    ORDER BY m.id DESC LIMIT 200
    """).fetchall()

    con.close()

    h = '<div class="panel"><div class="table-wrap"><table>'
    h += '<tr><th>User</th><th>Message</th><th>Image</th><th>Time</th><th>Reply</th></tr>'

    for r in rows:
        image = "-"
        if r["image"]:
            image = f'<a class="btn" target="_blank" href="/{r["image"]}">View</a>'

        h += f"""
        <tr>
        <td>{r["name"]}</td>
        <td>{r["message"] or ""}</td>
        <td>{image}</td>
        <td>{r["created_at"] or ""}</td>
        <td>
        <form method="post" action="/admin/reply/{r["id"]}">
        <input name="reply" value="{r["admin_reply"] or ""}" placeholder="Reply">
        <button class="btn">Send</button>
        </form>
        </td>
        </tr>
        """

    h += "</table></div></div>"
    return page(h,"User Chats")

@admin_bp.route("/reply/<int:mid>", methods=["POST"])
@admin_bp.route("/reply_chat/<int:mid>", methods=["POST"])
def reply_chat(mid):
    g = guard()
    if g: return g

    reply = request.form.get("reply","").strip()

    con = db()
    con.execute(
        "UPDATE messages SET admin_reply=? WHERE id=?",
        (reply,mid)
    )
    con.commit()
    con.close()

    return redirect("/admin/chats")
