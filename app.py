from flask import Flask, request, redirect
app = Flask(__name__)
users = {}
def page(title, body, msg=""):
    color = "#ff4444" if "wrong" in msg.lower() else "#00ff88"
    msg_html = f"<p style='color:{color};text-align:center;font-weight:bold'>{msg}</p>" if msg else ""
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{{background:#000;color:#FFD700;font-family:sans-serif;margin:0;padding:20px}}
   .top{{text-align:center;font-size:28px;font-weight:900;margin:20px 0}}
   .card{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto;box-shadow:0 0 20px #FFD70055}}
    h2{{text-align:center;color:#FFD700}}label{{color:#FFD700;font-size:14px}}
    input{{width:100%;padding:14px;margin:8px 0 16px;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff;box-sizing:border-box}}
    button{{width:100%;padding:15px;background:linear-gradient(#FFD700,#ff9900);border:none;border-radius:12px;font-weight:900;font-size:18px}}
   .link{{text-align:center;margin-top:15px;color:#fff}}.link a{{color:#FFD700}}
    </style></head><body><div class="top">👑 CODEX700 🔥</div><div class="card"><h2>{title}</h2>{msg_html}{body}</div></body>"""
@app.route('/')
def home(): return redirect('/register')
@app.route('/register', methods=['GET','POST'])
def register():
    msg=""
    ref_code = request.args.get('ref','')
    if request.method=='POST':
        name=request.form.get('name','').strip()
        phone=request.form.get('phone','').strip()
        pw=request.form.get('password','')
        cpw=request.form.get('confirm','')
        inv=request.form.get('invite','').strip()
        if not name or not phone or not pw or not cpw or not inv:
            msg="Dear user,u have entered a wrong information"
        elif not phone.isdigit() or len(phone)<10:
            msg="Dear user,u have entered a wrong information"
        elif pw!=cpw or len(pw)<4:
            msg="Dear user,u have entered a wrong information"
        elif phone in users:
            msg="Dear user,u have entered a wrong information"
        else:
            users[phone]={'name':name,'pw':pw}
            return page("REGISTER", f"<p style='text-align:center;color:#fff'>Welcome {name}!</p><div class='link'>Have account? <a href='/login'>Login</a></div>", "Registration successful")
    body=f"""
    <form method="post">
    <label>Name</label><input name="name" placeholder="Enter Name">
    <label>Phone number</label><input name="phone" placeholder="Enter Phone number">
    <label>Password</label><input type="password" name="password" placeholder="Enter Password">
    <label>Confirm password</label><input type="password" name="confirm" placeholder="Confirm Password">
    <label>Invitation code</label><input name="invite" placeholder="Invitation code" value="{ref_code}">
    <button>REGISTER</button>
    </form><div class="link">Have account? <a href="/login">Login</a></div>
    """
    return page("REGISTER", body, msg)
@app.route('/login', methods=['GET','POST'])
def login():
    msg=""
    if request.method=='POST':
        phone=request.form.get('phone','').strip()
        pw=request.form.get('password','')
        if phone in users and users[phone]['pw']==pw:
            return page("LOGIN", f"<p style='text-align:center;color:#fff'>Welcome back!</p>", "Registration successful")
        else:
            msg="Dear user,u have entered a wrong information"
    body="""<form method="post"><label>Phone number</label><input name="phone" placeholder="Enter Phone number">
    <label>Password</label><input type="password" name="password" placeholder="Enter Password">
    <button>LOGIN</button></form><div class="link">No account? <a href="/register">Register</a></div>"""
    return page("LOGIN", body, msg)
if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
