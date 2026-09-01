from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = "codex700-fresh-v1"

users = {}

STYLE = """
<meta name='viewport' content='width=device-width,initial-scale=1'>
<style>
body{background:#000;color:#FFD700;font-family:sans-serif;margin:0;padding:20px}
.header{text-align:center;font-size:28px;font-weight:900;margin:30px 0 20px;color:#FFD700}
.card{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto;box-shadow:0 0 20px #FFD70055}
.card h2{text-align:center;color:#FFD700;margin-bottom:20px}
label{color:#FFD700;font-size:14px;margin-top:10px;display:block}
input{width:100%;padding:14px;margin:8px 0 12px;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff;box-sizing:border-box}
input::placeholder{color:#777}
button{width:100%;padding:15px;background:linear-gradient(#FFD700,#FFA500);border:none;border-radius:12px;font-weight:900;font-size:18px;margin-top:10px;cursor:pointer}
.link{text-align:center;margin-top:15px;color:#fff}
.link a{color:#FFD700}
.err{color:#ff5555;text-align:center;min-height:20px}
</style>
"""

def page(title, body_inner, err=""):
    return f"""<head>{STYLE}</head><body>
<div class='header'>👑 CODEX700 🔥</div>
<div class='card'><h2>{title}</h2><div class='err'>{err}</div>{body_inner}</div>
</body>"""

@app.route('/')
def root():
    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register():
    err=""
    if request.method=='POST':
        name=request.form.get('name','').strip()
        phone=''.join(filter(str.isdigit, request.form.get('phone','')))
        pw=request.form.get('password','')
        cpw=request.form.get('confirm','')
        invite=request.form.get('invite','').strip()
        if not name: err="Enter Name"
        elif len(phone)<9: err="Phone must be at least 9 digits"
        elif len(pw)<4: err="Password must be at least 4 characters"
        elif pw!=cpw: err="Passwords do not match"
        elif phone in users: err="Phone already registered, please login"
        else:
            users[phone]={'name':name,'pw':pw}
            session['phone']=phone
            return redirect('/login?ok=1')
    ref=request.args.get('ref','')
    form=f"""
<form method='post'>
<label>Name</label><input name='name' placeholder='Enter Name'>
<label>Phone number</label><input name='phone' placeholder='Enter Phone number'>
<label>Password</label><input type='password' name='password' placeholder='Enter Password'>
<label>Confirm password</label><input type='password' name='confirm' placeholder='Confirm Password'>
<label>Invitation code</label><input name='invite' value='{ref}' placeholder='Invitation code'>
<button>REGISTER</button>
</form>
<div class='link'>Have account? <a href='/login'>Login</a></div>
"""
    return page("REGISTER", form, err)

@app.route('/login', methods=['GET','POST'])
def login():
    err=""
    if request.method=='POST':
        phone=''.join(filter(str.isdigit, request.form.get('phone','')))
        pw=request.form.get('password','')
        if phone in users and users[phone]['pw']==pw:
            session['phone']=phone
            return f"<h2 style='color:#FFD700;text-align:center;margin-top:100px'>Welcome {users[phone]['name']} - Login OK</h2>"
        err="Wrong phone or password"
    ok = "<p style='color:#0f0;text-align:center'>Registered! Please login</p>" if request.args.get('ok') else ""
    form=f"""{ok}
<form method='post'>
<label>Phone number</label><input name='phone' placeholder='Enter Phone number'>
<label>Password</label><input type='password' name='password' placeholder='Enter Password'>
<button>LOGIN</button>
</form>
<div class='link'>No account? <a href='/register'>Register</a></div>
"""
    return page("LOGIN", form, err)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)
