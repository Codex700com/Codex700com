from flask import Blueprint, session, redirect, request
import html

manager_bp=Blueprint("manager",__name__)

MANAGERS={
"joose":("JOOSE","0700880252","General Manager"),
"ellie":("Ellie","0708579380","Marketing Manager"),
"elia":("ELIA","","Marketing Manager"),
"anaa":("ANAA","","Marketing Manager"),
"amelia":("AMELIA","","Marketing Manager"),
"mary":("MARY","","Marketing Manager")
}

def setup(app,db,S):
    c=db()
    c.execute("CREATE TABLE IF NOT EXISTS manager_assignments(uid INTEGER PRIMARY KEY,manager_name TEXT NOT NULL,manager_phone TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS manager_messages(id INTEGER PRIMARY KEY AUTOINCREMENT,sender_uid INTEGER,sender_phone TEXT,recipient_uid INTEGER,recipient_phone TEXT,manager_name TEXT NOT NULL,body TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    c.commit()
    c.close()

    @app.route("/manager")
    def manager():
        if "uid" not in session:return redirect("/login")
        c=db()
        a=c.execute("SELECT manager_name FROM manager_assignments WHERE uid=?",(session["uid"],)).fetchone()
        c.close()
        cards=""
        for k,v in MANAGERS.items():
            cards+=f'<div class="card"><div class="pic">{v[0][0]}</div><h2>{v[0]}</h2><p>{v[2]}</p><form method="post" action="/manager/select/{k}"><button>Chat with me</button></form></div>'
        chosen=""
        if a:
            n=html.escape(a["manager_name"])
            chosen=f'<div class="chosen">YOUR MANAGER<br><b>{n}</b><small>Your choice is permanent.</small><a href="/manager/chat/{a["manager_name"].lower()}">Open Chat</a></div>'
        return S+f'''<style>
.mp{{min-height:100vh;background:#000;color:#fff;padding:18px 12px 90px;font-family:Georgia,serif}}
.head{{display:flex;gap:15px;align-items:center;border-bottom:1px solid #087fae;padding-bottom:18px}}
.back{{color:#00baff;font-size:38px;text-decoration:none}}h1{{color:#00baff;font-size:24px}}
.info{{color:#aaa;line-height:1.5;margin:20px 4px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.card{{background:#01080c;border:1px solid #087fae;border-radius:20px;padding:18px 7px;text-align:center}}
.pic{{width:90px;height:90px;border:2px solid #00baff;border-radius:50%;margin:auto;display:flex;align-items:center;justify-content:center;color:#00baff;font-size:40px;font-weight:bold}}
.card h2{{color:#00baff}}.card p{{color:#aaa}}button,.chosen a{{background:#08baf0;color:#fff;border:0;border-radius:25px;padding:11px 18px;font-weight:bold;text-decoration:none}}
.chosen{{border:1px solid #00baff;background:#03131c;border-radius:18px;padding:15px;text-align:center;color:#00baff;margin-bottom:20px}}
.chosen b{{display:block;color:#fff;font-size:27px;margin:7px}}.chosen small{{display:block;color:#aaa;margin-bottom:12px}}
</style><div class="mp"><div class="head"><a class="back" href="/my">&lt;</a><h1>Choose your manager</h1></div>
<div class="info">Pick the manager you want to chat with. Your choice is permanent — you will always talk to the same manager.</div>
{chosen}<div class="grid">{cards}</div></div>'''

    @app.post("/manager/select/<key>")
    def manager_select(key):
        if "uid" not in session:return redirect("/login")
        if key not in MANAGERS:return redirect("/manager")
        n,ph,t=MANAGERS[key]
        c=db()
        a=c.execute("SELECT manager_name FROM manager_assignments WHERE uid=?",(session["uid"],)).fetchone()
        if a:
            old=html.escape(a["manager_name"])
            c.close()
            return f'<script>alert("Your manager is {old}");location="/manager";</script>'
        c.execute("INSERT INTO manager_assignments(uid,manager_name,manager_phone) VALUES(?,?,?)",(session["uid"],n,ph))
        c.commit()
        c.close()
        return redirect("/manager/chat/"+key)

    @app.route("/manager/chat/<key>")
    def manager_chat(key):
        if "uid" not in session:return redirect("/login")
        if key not in MANAGERS:return redirect("/manager")
        n,ph,t=MANAGERS[key]
        c=db()
        a=c.execute("SELECT manager_name FROM manager_assignments WHERE uid=?",(session["uid"],)).fetchone()
        if not a:
            c.close()
            return redirect("/manager")
        if a["manager_name"].lower()!=n.lower():
            old=html.escape(a["manager_name"])
            c.close()
            return f'<script>alert("Your manager is {old}");location="/manager";</script>'
        rows=c.execute("SELECT sender_uid,body,created_at FROM manager_messages WHERE (sender_uid=? OR recipient_uid=?) AND manager_name=? ORDER BY id",(session["uid"],session["uid"],n)).fetchall()
        c.close()
        messages=""
        for r in rows:
            side="me" if r["sender_uid"]==session["uid"] else "them"
            messages+=f'<div class="msg {side}">{html.escape(r["body"])}<small>{r["created_at"]}</small></div>'
        if not messages:messages='<div class="empty">Hello! How can we help you?</div>'
        return S+f'''<style>
.cp{{min-height:100vh;background:#000;color:#fff;padding-bottom:80px;font-family:Arial}}
.top{{height:75px;border-bottom:1px solid #087fae;display:flex;align-items:center;gap:12px;padding:0 12px}}
.top a{{color:#00baff;font-size:38px;text-decoration:none}}.ava{{width:48px;height:48px;border:2px solid #00baff;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#00baff;font-size:22px}}
.name{{color:#00baff;font-size:20px;font-weight:bold}}.online{{color:#20dc75;font-size:12px}}
.body{{padding:15px;min-height:calc(100vh - 155px)}}.msg{{max-width:78%;padding:12px;border-radius:17px;margin:10px 0}}
.me{{margin-left:auto;background:#063f58;border:1px solid #00baff}}.them{{background:#071016;border:1px solid #174a61}}
small{{display:block;color:#78909c;font-size:10px;margin-top:5px}}.empty{{text-align:center;color:#888;margin-top:50px}}
.form{{position:fixed;bottom:0;left:0;right:0;background:#000;border-top:1px solid #123;padding:8px;display:flex;gap:7px}}
.form input{{flex:1;background:#071016;border:1px solid #07577a;border-radius:25px;padding:12px;color:#fff}}.form button{{width:60px;border:0;border-radius:25px;background:#08baf0;color:#fff}}
</style><div class="cp"><div class="top"><a href="/manager">&lt;</a><div class="ava">{n[0]}</div><div><div class="name">{n}</div><div class="online">● Online</div></div></div>
<div class="body">{messages}</div><form class="form" method="post" action="/manager/chat/send"><input type="hidden" name="manager" value="{n}"><input name="message" maxlength="1000" placeholder="Type your message..." required><button>Send</button></form></div>'''

    @app.post("/manager/chat/send")
    def manager_send():
        if "uid" not in session:return redirect("/login")
        msg=request.form.get("message","").strip()
        if not msg:return redirect("/manager")
        c=db()
        a=c.execute("SELECT manager_name,manager_phone FROM manager_assignments WHERE uid=?",(session["uid"],)).fetchone()
        if not a:
            c.close()
            return redirect("/manager")
        u=c.execute("SELECT phone FROM users WHERE id=?",(session["uid"],)).fetchone()
        r=c.execute("SELECT id FROM users WHERE phone=?",(a["manager_phone"],)).fetchone()
        c.execute("INSERT INTO manager_messages(sender_uid,sender_phone,recipient_uid,recipient_phone,manager_name,body) VALUES(?,?,?,?,?,?)",(session["uid"],u["phone"] if u else "",r["id"] if r else None,a["manager_phone"],a["manager_name"],msg))
        c.commit()
        c.close()
        return redirect("/manager/chat/"+a["manager_name"].lower())

    return True
