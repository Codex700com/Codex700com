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
            users[phone]={'name':name,'pw':pw,'wallet':0,'invested':0,'income':0,'active':0,'last_checkin':''}
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
            return redirect('/home')
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


@app.route('/home')
def home():
    ph=session.get('phone')
    if not ph or ph not in users: return redirect('/login')
    u=users[ph]
    return f"""<head>{STYLE}
<style>
.top{{display:flex;justify-content:space-between;align-items:center;padding:10px 5px}}
.banner{{background:linear-gradient(90deg,#1a0a0a,#3a1a00);border:1px solid #FFD70055;border-radius:16px;padding:20px;display:flex;justify-content:space-between;align-items:center}}
.stats{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin:12px 0}}
.stat{{background:#0a0a0a;border:1px solid #333;border-radius:12px;padding:12px 5px;text-align:center}}
.stat b{{color:#ff2222}}
.grid{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin:12px 0}}
.item{{background:#0a0a0a;border:1px solid #333;border-radius:12px;padding:15px 5px;text-align:center;color:#fff;text-decoration:none;display:block}}
.item a{{color:#fff;text-decoration:none}}
.checkin{{background:#2a0a0a;border:1px solid #ff444455;border-radius:12px;padding:15px;display:flex;justify-content:space-between;align-items:center;margin:12px 0}}
.btn-red{{background:#cc1111;color:#fff;padding:10px 20px;border-radius:10px;border:none;font-weight:700}}
.nav{{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;border-top:1px solid #333;display:flex;justify-content:space-around;padding:10px}}
body{{padding-bottom:70px}}
</style></head><body>
<div class='header' style='margin:10px 0'>👑 CODEX700 🔥</div>
<div class='top'><div style='color:#fff'>WELCOME BACK,<br><b style='color:#ff2222'>{u['name'].upper()}</b><br><small>Let's grow your wealth together</small></div>
<a href='/invest'><button class='btn-red'>Invest Now →</button></a></div>

<div class='stats'>
<div class='stat'><small style='color:#aaa'>Wallet Balance</small><br><b>UGX {u['wallet']:,}</b></div>
<div class='stat'><small style='color:#aaa'>Total Invested</small><br><b>UGX {u['invested']:,}</b></div>
<div class='stat'><small style='color:#aaa'>Total Income</small><br><b>UGX {u['income']:,}</b></div>
<div class='stat'><small style='color:#aaa'>Active Plans</small><br><b>{u['active']}</b></div>
</div>

<div class='checkin'><div><b style='color:#fff'>Daily Check-In Reward</b><br><small style='color:#aaa'>Check in daily and get <b style='color:#ff2222'>UGX 500</b></small></div>
<a href='/checkin'><button class='btn-red'>Check In →</button></a></div>

<div class='grid'>
<a class='item' href='/invest'>📈<br>Invest</a>
<a class='item' href='/deposit'>💰<br>Deposit</a>
<a class='item' href='/withdraw'>🏧<br>Withdraw</a>
<a class='item' href='/referrals'>👥<br>Referrals</a>
<a class='item' href='/transactions'>📄<br>Transactions</a>
<a class='item' href='/raffle'>🎁<br>Raffle</a>
<a class='item' href='/support'>🎧<br>Support</a>
<a class='item' href='/chat'>💬<br>Chat Manager</a>
</div>

<div class='checkin'><div><b style='color:#ff2222'>RAFFLE DRAW</b><br><small style='color:#aaa'>Win amazing prizes daily</small></div>
<a href='/raffle'><button class='btn-red'>View Prizes →</button></a></div>

<div class='nav'><a href='/home' style='color:#ff2222'>🏠<br><small>Home</small></a><a href='/invest' style='color:#aaa'>📈<br><small>Invest</small></a><a href='/transactions' style='color:#aaa'>⇄<br><small>Transactions</small></a><a href='/referrals' style='color:#aaa'>👥<br><small>Referrals</small></a><a href='/account' style='color:#aaa'>👤<br><small>Account</small></a></div>
</body>"""

@app.route('/checkin')
def checkin():
    from datetime import date
    ph=session.get('phone')
    if not ph or ph not in users: return redirect('/login')
    u=users[ph]; today=str(date.today())
    if u['last_checkin']!=today:
        u['last_checkin']=today; u['wallet']+=500; u['income']+=500
        msg="Checked in! +UGX 500"
    else: msg="Already checked in today"
    return f"<body style='background:#000;color:#FFD700;text-align:center;padding:50px;font-family:sans-serif'><h2>{msg}</h2><p>Wallet: UGX {u['wallet']:,}</p><a href='/home' style='color:#FFD700'>← Back to Home</a></body>"

@app.route('/deposit')
def deposit(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Deposit coming next - tell me to add</body><a href='/home'>Home</a>"
@app.route('/withdraw')
def withdraw(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Withdraw coming next</body><a href='/home'>Home</a>"
@app.route('/invest')
def invest(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Investment Plans coming next</body><a href='/home'>Home</a>"
@app.route('/transactions')
def transactions(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>No transactions yet</body><a href='/home'>Home</a>"
@app.route('/referrals')
def referrals(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Referral link: /register?ref="+session.get('phone','')+"</body><br><a href='/home'>Home</a>"
@app.route('/raffle')
def raffle(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Raffle coming soon</body><a href='/home'>Home</a>"
@app.route('/support')
def support(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Support: WhatsApp coming</body><a href='/home'>Home</a>"
@app.route('/chat')
def chat(): return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Chat Manager coming</body><a href='/home'>Home</a>"
@app.route('/account')
def account():
    ph=session.get('phone')
    if not ph: return redirect('/login')
    u=users[ph]
    return f"<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>Name: {u['name']}<br>Phone: {ph}<br><a href='/logout' style='color:#ff5555'>Logout</a><br><br><a href='/home'>Home</a></body>"
@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)
