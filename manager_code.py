from flask import Blueprint, session, redirect
import html
from urllib.parse import quote

manager_bp=Blueprint("manager",__name__)

MANAGERS={
"joose":("JOOSE","0700880252","General Manager"),
"ellie":("Ellie","0708579380","Marketing Manager"),
"elia":("Elia","0740859668","Marketing Manager"),
"amelia":("Amelia","0789590432","Marketing Manager"),
"mary":("Mary","0749942060","Marketing Manager"),
"anna":("Anna","0724018143","Marketing Manager")
}

def setup(app,db,S):

    c=db()
    c.execute("""CREATE TABLE IF NOT EXISTS manager_assignments(
        uid INTEGER PRIMARY KEY,
        manager_name TEXT NOT NULL,
        manager_phone TEXT NOT NULL
    )""")
    c.commit()
    c.close()

    def manager_key(name):
        for k,v in MANAGERS.items():
            if v[0].lower()==name.lower():
                return k
        return ""

    @app.route("/manager")
    def manager():
        if "uid" not in session:
            return redirect("/login")

        c=db()
        a=c.execute(
            "SELECT manager_name,manager_phone FROM manager_assignments WHERE uid=?",
            (session["uid"],)
        ).fetchone()
        c.close()

        # User already has a manager: show ONLY that manager
        if a:
            key=manager_key(a["manager_name"])
            n=html.escape(a["manager_name"])
            ph=a["manager_phone"]
            wa="256"+ph.lstrip("0").replace("+","").replace(" ","")
            message=quote("Hello "+a["manager_name"]+", I would like to chat with you.")

            return S+f'''<style>
body{{margin:0;background:#000;color:#fff;font-family:Arial,sans-serif}}
.mp{{min-height:100vh;padding:18px 14px 90px;box-sizing:border-box}}
.head{{display:flex;align-items:center;gap:14px;border-bottom:1px solid #087fae;padding-bottom:18px}}
.back{{color:#00baff;text-decoration:none;font-size:38px}}
h1{{color:#00baff;font-size:25px;margin:0}}
.info{{color:#999;text-align:center;margin:28px 5px 18px}}
.card{{background:#020b11;border:1px solid #00baff;border-radius:24px;padding:30px 18px;text-align:center;max-width:380px;margin:auto;box-shadow:0 0 20px rgba(0,174,255,.12)}}
.pic{{width:95px;height:95px;border:3px solid #00baff;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:auto;color:#00baff;font-size:42px;font-weight:bold}}
.name{{color:#00baff;font-size:27px;font-weight:bold;margin-top:18px}}
.role{{color:#aaa;margin:8px 0 25px}}
.wa{{display:block;background:#19c463;color:#fff;text-decoration:none;padding:15px;border-radius:30px;font-size:17px;font-weight:bold}}
.status{{color:#20dc75;margin:18px 0;font-size:13px}}
</style>
<div class="mp">
<div class="head"><a class="back" href="/my">&lt;</a><h1>My Manager</h1></div>
<div class="info">Your manager is permanently selected.</div>
<div class="card">
<div class="pic">{n[0]}</div>
<div class="name">{n}</div>
<div class="role">{html.escape(a["manager_phone"])}</div>
<div class="status">● Your manager</div>
<a class="wa" href="https://wa.me/{wa}?text={message}">💬 Chat on WhatsApp</a>
</div>
</div>'''

        # No manager selected yet: show choices
        cards=""
        photos={'joose': 'https://randomuser.me/api/portraits/women/44.jpg', 'ellie': 'https://randomuser.me/api/portraits/women/32.jpg', 'elia': 'https://randomuser.me/api/portraits/women/65.jpg', 'amelia': 'https://randomuser.me/api/portraits/women/68.jpg', 'mary': 'https://randomuser.me/api/portraits/women/49.jpg', 'anna': 'https://randomuser.me/api/portraits/women/63.jpg'}
        for k,v in MANAGERS.items():
            wa="256"+v[1].lstrip("0").replace("+","").replace(" ","")
            cards+=f'''
            <div class="card">
              <img class="manager-photo" src="{photos.get(k, "")}" alt="{html.escape(v[0])}">
              <div class="pic">{html.escape(v[0][0])}</div>
              <div class="name">{html.escape(v[0])}</div>
              <div class="role">{html.escape(v[2])}</div>
              <form method="post" action="/manager/select/{k}">
                <button>Choose {html.escape(v[0])}</button>
              </form>
            </div>'''

        return S+f'''<style>
body{{margin:0;background:#000;color:#fff;font-family:Arial,sans-serif}}
.mp{{min-height:100vh;padding:18px 12px 90px;box-sizing:border-box}}
.head{{display:flex;align-items:center;gap:14px;border-bottom:1px solid #087fae;padding-bottom:18px}}
.back{{color:#00baff;text-decoration:none;font-size:38px}}
h1{{color:#00baff;font-size:24px;margin:0}}
.info{{color:#999;line-height:1.5;text-align:center;margin:20px 5px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:15px}}
.card{{background:#020b11;border:1px solid #087fae;border-radius:20px;padding:18px 7px;text-align:center}}
.manager-photo{{width:96px;height:96px;object-fit:cover;border:3px solid #00baff;border-radius:50%;display:block;margin:auto;box-shadow:0 0 18px rgba(0,174,255,.35)}}.pic{{display:none}}
.name{{color:#00baff;font-size:20px;font-weight:bold;margin-top:12px}}
.role{{color:#999;font-size:12px;margin:7px 0 15px}}
button{{background:#08baf0;color:#fff;border:0;border-radius:25px;padding:10px 14px;font-weight:bold}}
@media(max-width:360px){{.grid{{grid-template-columns:1fr}}}}
</style>
<div class="mp">
<div class="head"><a class="back" href="/my">&lt;</a><h1>Choose Manager</h1></div>
<div class="info">Choose one manager. Your choice will remain permanently.</div>
<div class="grid">{cards}</div>
</div>'''

    @app.post("/manager/select/<key>")
    def manager_select(key):
        if "uid" not in session:
            return redirect("/login")

        if key not in MANAGERS:
            return redirect("/manager")

        n,ph,t=MANAGERS[key]

        c=db()
        a=c.execute(
            "SELECT manager_name FROM manager_assignments WHERE uid=?",
            (session["uid"],)
        ).fetchone()

        if a:
            old=html.escape(a["manager_name"])
            c.close()
            return f'''<script>
alert("Your manager is {old}");
location="/manager";
</script>'''

        c.execute(
            "INSERT INTO manager_assignments(uid,manager_name,manager_phone) VALUES(?,?,?)",
            (session["uid"],n,ph)
        )
        c.commit()
        c.close()

        return redirect("/manager")

    return True
