from flask import Flask, request, redirect, url_for, session
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "codex700-secret"
DB = "codex.db"

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT UNIQUE, password TEXT, invite TEXT
    )""")
    c.commit(); c.close()
init()

STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#000;color:#ffcc33;font-family:Arial;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:10px}
.header{text-align:center;font-size:22px;font-weight:bold;margin:10px 0;color:#ffcc33}
.card{width:100%;max-width:340px;background:#0a0a0a;border:2px solid #ffcc33;border-radius:16px;padding:20px 18px;box-shadow:0 0 15px #ffcc3388}
h2{text-align:center;color:#ffcc33;margin-bottom:15px;font-size:22px}
label{display:block;margin:10px 0 4px;color:#ffcc33;font-size:14px}
input{width:100%;padding:11px;border-radius:10px;border:1px solid #ffcc33;background:#111;color:#fff;font-size:14px}
input::placeholder{color:#777}
.btn{width:100%;margin-top:18px;padding:13px;border:none;border-radius:10px;background:linear-gradient(#ffdd44,#ff9900);font-weight:bold;font-size:16px;cursor:pointer}
.link{text-align:center;margin-top:12px;color:#fff;font-size:14px}
.link a{color:#ffcc33}
</style>
"""
HEADER = "<div class='header'>👑 CODEX700 🔥</div>"

@app.route('/')
def home(): return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register():
    msg=""
    if request.method=='POST':
        name=request.form.get('name','').strip()
        phone=request.form.get('phone','').strip()
        pw=request.form.get('password','')
        pw2=request.form.get('confirm','')
        invite=request.form.get('invite','').strip()
        if not name or not phone or not pw:
            msg="Fill all fields"
        elif pw!=pw2:
            msg="Passwords don't match"
        else:
            try:
                c=db()
                c.execute("INSERT INTO users(name,phone,password,invite) VALUES(?,?,?,?)",
                          (name,phone,generate_password_hash(pw),invite))
                c.commit(); c.close()
                return redirect('/login')
            except:
                msg="Phone already registered"
    return STYLE+HEADER+f"""
    <div class='card'><h2>REGISTER</h2>
    <div style='color:red;text-align:center'>{msg}</div>
    <form method='post'>
    <label>Name</label><input name='name' placeholder='Enter Name'>
    <label>Phone number</label><input name='phone' placeholder='Enter Phone number'>
    <label>Password</label><input type='password' name='password' placeholder='Enter Password'>
    <label>Confirm password</label><input type='password' name='confirm' placeholder='Confirm Password'>
    <label>Invitation code</label><input name='invite' placeholder='Invitation code'>
    <button class='btn'>REGISTER</button>
    </form><div class='link'>Have account? <a href='/login'>Login</a></div></div>
    """

@app.route('/login', methods=['GET','POST'])
def login():
    msg=""
    if request.method=='POST':
        phone=request.form.get('phone','').strip()
        pw=request.form.get('password','')
        c=db(); u=c.execute("SELECT * FROM users WHERE phone=?",(phone,)).fetchone(); c.close()
        if u and check_password_hash(u['password'],pw):
            session['uid']=u['id']; session['name']=u['name']
            return "Logged in as "+u['name']+" (dashboard comes next)"
        else:
            msg="Invalid login"
    return STYLE+HEADER+f"""
    <div class='card'><h2>LOGIN</h2>
    <div style='color:red;text-align:center'>{msg}</div>
    <form method='post'>
    <label>Phone number</label><input name='phone' placeholder='Enter Phone number'>
    <label>Password</label><input type='password' name='password' placeholder='Enter Password'>
    <button class='btn'>LOGIN</button>
    </form><div class='link'>No account? <a href='/register'>Register</a></div></div>
    """

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
