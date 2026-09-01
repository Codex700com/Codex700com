from flask import Flask, request, redirect, session
app = Flask(__name__)
app.secret_key = "codex700secret"
users = {}

def auth_page(title, body, msg=""):
    color = "#ff4444" if "wrong" in msg.lower() else "#00ff88"
    m = f"<p style='color:{color};text-align:center;font-weight:bold'>{msg}</p>" if msg else ""
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    body{{background:#000;color:#FFD700;font-family:sans-serif;margin:0;padding:20px}}
   .top{{text-align:center;font-size:28px;font-weight:900;margin:20px 0}}
   .card{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}
    h2{{text-align:center}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff;box-sizing:border-box}}
    button{{width:100%;padding:15px;background:linear-gradient(#FFD700,#ff9900);border:none;border-radius:12px;font-weight:900;font-size:18px}}
   .link{{text-align:center;margin-top:15px;color:#fff}}.link a{{color:#FFD700}}
    </style></head><body><div class="top">👑 CODEX700 🔥</div><div class="card"><h2>{title}</h2>{m}{body}</div></body>"""

def dashboard_html(name):
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    body{{background:#000;color:#fff;font-family:sans-serif;margin:0;padding-bottom:80px}}
   .header{{display:flex;justify-content:space-between;align-items:center;padding:15px}}
   .logo{{color:#FFD700;font-weight:900;font-size:22px}}.logo span{{color:#ff2222}}
   .banner{{margin:10px;border:1px solid #FFD70055;border-radius:15px;padding:20px;background:linear-gradient(90deg,#1a0a0a,#000);position:relative;overflow:hidden}}
   .banner h3{{margin:0;color:#fff}}.banner h2{{color:#ff2222;margin:5px 0}}
   .btn{{background:#cc1111;color:#fff;padding:10px 20px;border-radius:8px;border:none;font-weight:bold}}
   .grid4{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;padding:10px}}
   .grid2{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;padding:10px}}
   .box{{background:#111;border:1px solid #333;border-radius:12px;padding:12px;text-align:center;font-size:12px}}
   .box b{{color:#ff2222;display:block;margin-top:5px}}
   .checkin{{margin:10px;background:#1a0a0a;border:1px solid #FFD70033;border-radius:12px;padding:15px;display:flex;justify-content:space-between;align-items:center}}
   .icon-grid{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;padding:10px}}
   .icon{{background:#111;border:1px solid #333;border-radius:12px;padding:15px 5px;text-align:center;font-size:12px}}
   .plans{{display:flex;gap:10px;overflow-x:auto;padding:10px}}
   .plan{{min-width:150px;background:#111;border:1px solid #333;border-radius:12px;padding:10px;font-size:12px}}
   .plan b{{color:#fff}}.plan span{{color:#ff2222;float:right}}
   .nav{{position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333}}
   .nav div{{text-align:center;font-size:11px;color:#888}}.nav.active{{color:#ff2222}}
    </style></head><body>
    <div class="header"><div class="logo">🪙 <span>CODEX</span></div><div>🔔 <span style="background:red;border-radius:50%;padding:2px 6px;font-size:12px">3</span> 👤</div></div>
    <div class="banner"><h3>WELCOME BACK,</h3><h2>{name.upper()}</h2><p>Let's grow your wealth together</p><button class="btn">Invest Now →</button></div>
    <div class="grid4">
      <div class="box">💼 Wallet Balance<b>UGX 0</b>👁️</div>
      <div class="box">📈 Total Invested<b>UGX 0</b></div>
      <div class="box">💰 Total Income<b>UGX 0</b></div>
      <div class="box">💼 Active Plans<b>0</b></div>
    </div>
    <div class="checkin"><div>🎁 <b>Daily Check-In Reward</b><br><small>Check in daily and get <span style="color:#ff2222">UGX 500</span></small></div><button class="btn">Check In →</button></div>
    <div class="icon-grid">
      <div class="icon">📈<br>Invest</div><div class="icon">💰<br>Deposit</div><div class="icon">🏧<br>Withdraw</div><div class="icon">👥<br>Referrals</div>
      <div class="icon">📄<br>Transactions</div><div class="icon">🎁<br>Raffle</div><div class="icon">🎧<br>Support</div><div class="icon">💬<br>Chat Manager</div>
    </div>
    <div class="checkin"><div>🏆 <b style="color:#ff2222">RAFFLE DRAW</b><br><small>Win amazing prizes daily</small><br><button class="btn" style="margin-top:8px">View Prizes →</button></div><div style="font-size:40px">🎁</div></div>
    <h4 style="color:#ff2222;padding:0 15px">📈 INVESTMENT PLANS <span style="float:right;font-size:12px">View All Plans ></span></h4>
    <div class="plans">
      <div class="plan"><b>Starter Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 50,000</span></div>
      <div class="plan"><b>Silver Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 250,000</span></div>
      <div class="plan"><b>Gold Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 500,000</span></div>
      <div class="plan"><b>Platinum Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 1,000,000</span></div>
    </div>
    <div class="nav"><div class="active">🏠<br>Home</div><div>📈<br>Invest</div><div>🔄<br>Transactions</div><div>👥<br>Referrals</div><div>👤<br>Account</div></div>
    </body>"""

@app.route('/')
def home(): return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register():
    msg=""; ref_code=request.args.get('ref','')
    if request.method=='POST':
        name=request.form.get('name','').strip()
        phone_raw=request.form.get('phone','').strip()
        phone=phone_raw.replace('+','').replace(' ','').replace('-','')
        pw=request.form.get('password','').strip()
        cpw=request.form.get('confirm','').strip()
        inv=request.form.get('invite','').strip() or ref_code
        if not name or not phone_raw or not pw or not cpw or not phone.isdigit() or len(phone)<9 or pw!=cpw or len(pw)<4:
            msg="Dear user,u have entered a wrong information"
        elif phone in users:
            msg="Dear user,u have entered a wrong information"
        else:
            users[phone]={'name':name,'pw':pw}
            session['user']=name
            session['msg']="Registration successful"
            return redirect('/dashboard')
    body=f"""<form method="post"><input name="name" placeholder="Enter Name"><input name="phone" placeholder="Enter Phone number">
    <input type="password" name="password" placeholder="Enter Password"><input type="password" name="confirm" placeholder="Confirm Password">
    <input name="invite" placeholder="Invitation code" value="{ref_code}"><button>REGISTER</button></form>
    <div class="link">Have account? <a href="/login">Login</a></div>"""
    return auth_page("REGISTER", body, msg)

@app.route('/login', methods=['GET','POST'])
def login():
    msg=""
    if request.method=='POST':
        phone_raw=request.form.get('phone','').strip()
        phone=phone_raw.replace('+','').replace(' ','').replace('-','')
        pw=request.form.get('password','').strip()
        if phone in users and users[phone]['pw']==pw:
            session['user']=users[phone]['name']
            session['msg']="Registration successful"
            return redirect('/dashboard')
        else:
            msg="Dear user,u have entered a wrong information"
    body="""<form method="post"><input name="phone" placeholder="Enter Phone number">
    <input type="password" name="password" placeholder="Enter Password"><button>LOGIN</button></form>
    <div class="link">No account? <a href="/register">Register</a></div>"""
    return auth_page("LOGIN", body, msg)

@app.route('/dashboard')
def dashboard():
    name=session.pop('user', None) or session.get('user_name', 'IMRAN PRINCE')
    # keep name for refresh
    if 'user' in session: session['user_name']=session['user']
    else: session['user']=name; session['user_name']=name
    msg=session.pop('msg', '')
    html=dashboard_html(name)
    if msg:
        html=html.replace('<body>', f"<body><p style='background:#00ff88;color:#000;text-align:center;padding:10px;font-weight:bold;margin:0'>{msg}</p>")
    return html

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
