import sqlite3
from flask import Blueprint, request, redirect, url_for, session, render_template_string

safe_admin = Blueprint("safe_admin", __name__)

DB = "codex700.db"


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def is_admin():
    return bool(session.get("is_admin") or session.get("admin"))


def guard():
    if not is_admin():
        return redirect("/admin/login")
    return None


def ensure_columns():
    con = db()

    cols = [r[1] for r in con.execute("PRAGMA table_info(users)").fetchall()]

    if "is_admin" not in cols:
        con.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

    if "blocked" not in cols:
        con.execute("ALTER TABLE users ADD COLUMN blocked INTEGER DEFAULT 0")

    if "refcode" not in cols:
        con.execute("ALTER TABLE users ADD COLUMN refcode TEXT")

    con.execute("""
        CREATE TABLE IF NOT EXISTS platform_settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    defaults = {
        "site_name": "CODEX700",
        "primary_color": "#00aaff",
        "secondary_color": "#0066ff",
        "background_color": "#050b14",
        "card_color": "#0b1422",
        "text_color": "#ffffff",
        "muted_color": "#8fa3b8",
        "button_radius": "14",
        "font_size": "15",
    }

    for k, v in defaults.items():
        con.execute(
            "INSERT OR IGNORE INTO platform_settings(key,value) VALUES(?,?)",
            (k, v)
        )

    con.commit()
    con.close()


ensure_columns()


STYLE = """
<style>
*{box-sizing:border-box}
body{
    margin:0;
    background:#050b14;
    color:#fff;
    font-family:Arial,sans-serif;
}
.wrap{
    max-width:1100px;
    margin:auto;
    padding:18px;
}
.top{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:10px;
    margin-bottom:18px;
}
h1{font-size:24px;margin:0}
h2{font-size:19px}
.card{
    background:#0b1422;
    border:1px solid #12304d;
    border-radius:16px;
    padding:18px;
    margin-bottom:16px;
}
input,select{
    width:100%;
    padding:13px;
    margin:6px 0 10px;
    background:#07101c;
    color:white;
    border:1px solid #214564;
    border-radius:10px;
}
button,.btn{
    display:inline-block;
    border:0;
    border-radius:10px;
    padding:11px 15px;
    background:#078cff;
    color:white;
    text-decoration:none;
    cursor:pointer;
    margin:3px;
}
.red{background:#d92d3d}
.green{background:#12a86b}
.gray{background:#334155}
.yellow{background:#b77900}
.grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px;
}
.user{
    padding:14px;
    border:1px solid #173752;
    border-radius:12px;
    margin:8px 0;
}
.small{color:#8fa3b8;font-size:13px}
@media(max-width:650px){
    .grid{grid-template-columns:1fr}
    .top{align-items:flex-start;flex-direction:column}
}
</style>
"""


def settings_dict():
    con = db()
    rows = con.execute("SELECT key,value FROM platform_settings").fetchall()
    con.close()
    return {r["key"]: r["value"] for r in rows}


@safe_admin.route("/admin/users/manage")
def users_manage():
    x = guard()
    if x:
        return x

    q = request.args.get("q", "").strip()

    con = db()

    if q:
        users = con.execute("""
            SELECT id,name,phone,invite,refcode,balance,is_admin,blocked
            FROM users
            WHERE CAST(id AS TEXT)=?
               OR name LIKE ?
               OR phone LIKE ?
               OR refcode LIKE ?
               OR invite LIKE ?
            ORDER BY id DESC
        """, (q, f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    else:
        users = con.execute("""
            SELECT id,name,phone,invite,refcode,balance,is_admin,blocked
            FROM users
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    con.close()

    html = STYLE + """
    <div class="wrap">
      <div class="top">
        <h1>CODEX700 — User Management</h1>
        <a class="btn gray" href="/admin">Admin Dashboard</a>
      </div>

      <div class="card">
        <form method="get">
          <input name="q" value="{{q}}" placeholder="Search name, phone, ID or referral code">
          <button>Search Users</button>
        </form>
      </div>

      <div class="card">
        <h2>Users</h2>
        {% for u in users %}
        <div class="user">
          <b>{{u['name'] or 'Unnamed User'}}</b>
          <div class="small">
            ID: {{u['id']}} · Phone: {{u['phone']}}
          </div>
          <div class="small">
            Balance: {{u['balance'] or 0}} ·
            Referral: {{u['refcode'] or 'Not set'}}
          </div>

          <div style="margin-top:10px">
            {% if u['is_admin'] %}
              <span class="btn yellow">ADMIN</span>
            {% else %}
              <span class="btn gray">USER</span>
            {% endif %}

            {% if u['blocked'] %}
              <span class="btn red">BLOCKED</span>
            {% endif %}
          </div>

          <div style="margin-top:8px">
            <a class="btn" href="/admin/users/manage/{{u['id']}}">Manage</a>

            {% if u['id'] != 1 %}
              {% if u['is_admin'] %}
              <form method="post" action="/admin/users/toggle-admin/{{u['id']}}" style="display:inline">
                <button class="yellow">Remove Admin</button>
              </form>
              {% else %}
              <form method="post" action="/admin/users/toggle-admin/{{u['id']}}" style="display:inline">
                <button class="green">Make Admin</button>
              </form>
              {% endif %}

              {% if u['blocked'] %}
              <form method="post" action="/admin/users/toggle-block/{{u['id']}}" style="display:inline">
                <button class="green">Unblock</button>
              </form>
              {% else %}
              <form method="post" action="/admin/users/toggle-block/{{u['id']}}" style="display:inline">
                <button class="red">Block</button>
              </form>
              {% endif %}
            {% endif %}
          </div>
        </div>
        {% else %}
        <p>No users found.</p>
        {% endfor %}
      </div>
    </div>
    """

    return render_template_string(html, users=users, q=q)


@safe_admin.route("/admin/users/manage/<int:uid>")
def user_manage(uid):
    x = guard()
    if x:
        return x

    con = db()
    u = con.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()
    con.close()

    if not u:
        return "User not found", 404

    return render_template_string(STYLE + """
    <div class="wrap">
      <div class="top">
        <h1>User #{{u['id']}}</h1>
        <a class="btn gray" href="/admin/users/manage">Back</a>
      </div>

      <div class="card">
        <h2>Account Details</h2>
        <p><b>Name:</b> {{u['name'] or ''}}</p>
        <p><b>Phone:</b> {{u['phone'] or ''}}</p>
        <p><b>Balance:</b> {{u['balance'] or 0}}</p>
        <p><b>Admin:</b> {{'Yes' if u['is_admin'] else 'No'}}</p>
        <p><b>Blocked:</b> {{'Yes' if u['blocked'] else 'No'}}</p>
      </div>

      <div class="card">
        <h2>Referral / Invitation Code</h2>
        <form method="post" action="/admin/users/refcode/{{u['id']}}">
          <input name="refcode" value="{{u['refcode'] or ''}}" placeholder="Referral code">
          <button>Save Referral Code</button>
        </form>
      </div>

      <div class="card">
        <h2>Reset Password</h2>
        <p class="small">
          Existing passwords are never displayed. Enter a new password to reset the account.
        </p>
        <form method="post" action="/admin/users/reset-password/{{u['id']}}">
          <input type="password" name="password" minlength="6" placeholder="New password" required>
          <input type="password" name="password2" minlength="6" placeholder="Confirm new password" required>
          <button>Reset Password</button>
        </form>
      </div>
    </div>
    """, u=u)


@safe_admin.route("/admin/users/toggle-admin/<int:uid>", methods=["POST"])
def toggle_admin(uid):
    x = guard()
    if x:
        return x

    if uid == 1:
        return "The primary administrator cannot be removed.", 400

    con = db()
    row = con.execute(
        "SELECT is_admin FROM users WHERE id=?",
        (uid,)
    ).fetchone()

    if not row:
        con.close()
        return "User not found", 404

    new_value = 0 if row["is_admin"] else 1

    con.execute(
        "UPDATE users SET is_admin=? WHERE id=?",
        (new_value, uid)
    )
    con.commit()
    con.close()

    return redirect(request.referrer or "/admin/users/manage")


@safe_admin.route("/admin/users/toggle-block/<int:uid>", methods=["POST"])
def toggle_block(uid):
    x = guard()
    if x:
        return x

    if uid == 1:
        return "The primary administrator cannot be blocked.", 400

    con = db()
    row = con.execute(
        "SELECT blocked FROM users WHERE id=?",
        (uid,)
    ).fetchone()

    if not row:
        con.close()
        return "User not found", 404

    new_value = 0 if row["blocked"] else 1

    con.execute(
        "UPDATE users SET blocked=? WHERE id=?",
        (new_value, uid)
    )
    con.commit()
    con.close()

    return redirect(request.referrer or "/admin/users/manage")


@safe_admin.route("/admin/users/refcode/<int:uid>", methods=["POST"])
def edit_refcode(uid):
    x = guard()
    if x:
        return x

    code = request.form.get("refcode", "").strip()

    if len(code) > 50:
        return "Referral code is too long.", 400

    con = db()

    exists = con.execute(
        "SELECT id FROM users WHERE refcode=? AND id!=?",
        (code, uid)
    ).fetchone() if code else None

    if exists:
        con.close()
        return "That referral code is already in use.", 400

    con.execute(
        "UPDATE users SET refcode=? WHERE id=?",
        (code or None, uid)
    )
    con.commit()
    con.close()

    return redirect(request.referrer or "/admin/users/manage")


@safe_admin.route("/admin/users/reset-password/<int:uid>", methods=["POST"])
def reset_password(uid):
    x = guard()
    if x:
        return x

    p1 = request.form.get("password", "")
    p2 = request.form.get("password2", "")

    if len(p1) < 6:
        return "Password must contain at least 6 characters.", 400

    if p1 != p2:
        return "Passwords do not match.", 400

    con = db()

    if not con.execute(
        "SELECT id FROM users WHERE id=?",
        (uid,)
    ).fetchone():
        con.close()
        return "User not found", 404

    # Keep compatibility with the current CODEX login system.
    # Do not display the stored password.
    con.execute(
        "UPDATE users SET password=? WHERE id=?",
        (p1, uid)
    )

    con.commit()
    con.close()

    return redirect(request.referrer or "/admin/users/manage")


@safe_admin.route("/admin/settings")
def settings():
    x = guard()
    if x:
        return x

    s = settings_dict()

    return render_template_string(STYLE + """
    <div class="wrap">
      <div class="top">
        <h1>Platform Appearance</h1>
        <a class="btn gray" href="/admin">Admin Dashboard</a>
      </div>

      <div class="card">
        <p class="small">
          These controls change the appearance settings stored for the platform.
          They do not change financial product calculations.
        </p>

        <form method="post" action="/admin/settings/save">
          <div class="grid">
            <div>
              <label>Platform Name</label>
              <input name="site_name" value="{{s['site_name']}}">
            </div>

            <div>
              <label>Font Size</label>
              <input name="font_size" value="{{s['font_size']}}">
            </div>

            <div>
              <label>Primary Color</label>
              <input type="color" name="primary_color" value="{{s['primary_color']}}">
            </div>

            <div>
              <label>Secondary Color</label>
              <input type="color" name="secondary_color" value="{{s['secondary_color']}}">
            </div>

            <div>
              <label>Background Color</label>
              <input type="color" name="background_color" value="{{s['background_color']}}">
            </div>

            <div>
              <label>Card Color</label>
              <input type="color" name="card_color" value="{{s['card_color']}}">
            </div>

            <div>
              <label>Text Color</label>
              <input type="color" name="text_color" value="{{s['text_color']}}">
            </div>

            <div>
              <label>Muted Text Color</label>
              <input type="color" name="muted_color" value="{{s['muted_color']}}">
            </div>

            <div>
              <label>Button Radius (px)</label>
              <input name="button_radius" value="{{s['button_radius']}}">
            </div>
          </div>

          <button>Save Appearance</button>
        </form>
      </div>
    </div>
    """, s=s)


@safe_admin.route("/admin/settings/save", methods=["POST"])
def settings_save():
    x = guard()
    if x:
        return x

    keys = [
        "site_name",
        "primary_color",
        "secondary_color",
        "background_color",
        "card_color",
        "text_color",
        "muted_color",
        "button_radius",
        "font_size",
    ]

    con = db()

    for key in keys:
        value = request.form.get(key, "").strip()

        if len(value) > 100:
            value = value[:100]

        con.execute("""
            INSERT INTO platform_settings(key,value)
            VALUES(?,?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, value))

    con.commit()
    con.close()

    return redirect("/admin/settings")


@safe_admin.route("/admin/platform")
def platform():
    return redirect("/admin/settings")
