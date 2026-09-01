from flask import Flask, request, redirect, session
from datetime import date
app = Flask(__name__)
app.secret_key="codex700secret"
users={} # phone -> dict

def require_login():
    return 'phone' in session

def layout(title, body, active="home"):
    u = users.get(session.get('phone'), {})
    name = u.get('name','USER')
    bal = u.get('wallet',0)
    nav = f"""
    <div style="position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #333;z-index:99">
      <a href="/home" style="text-decoration:none;color:{'#ff2222' if active=='home' else '#888'};font-size:11px;text-align:center">🏠<br>HOME</a>
      <a href="/invest" style="text-decoration:none;color:{'#ff2222' if active=='invest' else '#888'};font-size:11px;text-align:center">📈<br>INVEST</a>
      <a href="/transactions" style="text-decoration:none;color:{'#ff2222' if active=='trans' else '#888'};font-size:11px;text-align:center">🔄<br>TRANSACTIONS</a>
      <a href="/referrals" style="text-decoration:none;color:{'#ff2222' if active=='ref' else '#888'};font-size:11px;text-align:center">👥<br>REFERRALS</a>
      <a href="/account" style="text-decoration:none;color:{'#ff2222' if active=='acc' else '#888'};font-size:11px;text-align:center">👤<br>ACCOUNT</a>
    </div>"""
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    body{{background:#000;color:#fff;font-family:sans-serif;margin:0;padding-bottom:80px}}
    a{{color:#FFD700}}.card{{background:#111;border:1px solid #333;border-radius:12px;padding:15px;margin:10px}}
   .btn{{background:#cc1111;color:#fff;padding:12px;border:none;border-radius:10px;font-weight:bold;width:100%}}
   .gold{{color:#FFD700}}.red{{color:#ff2222}}
   .grid{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;padding:10px}}
   .box{{background:#111;border:1px solid #333;border-radius:12px;padding:12px;text-align:center;font-size:12px}}
    input,select{{width:100%;padding:12px;margin:8px 0;background:#1a1a1a;border:1px solid #FFD70055;border-radius:10px;color:#fff;box-sizing:border-box}}
   .header{{display:flex;justify-content:space-between;align-items:center;padding:15px;background:#0a0a0a;border-bottom:1px solid #333}}
    </style></head><body>
    <div class="header"><a href="/home2" style="font-size:22px;text-decoration:none">☰</a>
    <div class="gold" style="font-weight:900;font-size:20px">🪙 <span class="red">CODEX</span></div>
    <div><a href="/notifications" style="text-decoration:none">🔔</a> <a href="/account" style="text-decoration:none">👤</a></div></div>
    {body}{nav}</body>"""

def login_required_page(body_fn):
    def wrapper(*a,**kw):
        if not require_login(): return redirect('/login')
        return body_fn(*a,**kw)
    wrapper.__name__=body_fn.__name__
    return wrapper

@app.route('/')
def root(): return redirect('/home' if require_login() else '/register')

@app.route('/register', methods=['GET','POST'])
def register():
    msg=""; ref=request.args.get('ref','')
    if request.method=='POST':
        name=request.form.get('name','').strip()
        pr=request.form.get('phone','').strip()
        phone=pr.replace('+','').replace(' ','').replace('-','')
        pw=request.form.get('password','').strip()
        cpw=request.form.get('confirm','').strip()
        if not name or not phone.isdigit() or len(phone)<9 or pw!=cpw or len(pw)<4 or phone in users:
            msg="Dear user,u have entered a wrong information"
        else:
            users[phone]={'name':name,'pw':pw,'phone':pr,'wallet':0,'invested':0,'income':0,'active':0,'tx':[],'notif':[],'last_checkin':'','referrals':0,'ref_earn':0,'investments':[]}
            session['phone']=phone
            return redirect('/home')
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{background:#000;color:#FFD700;font-family:sans-serif;padding:20px}}.card{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff;box-sizing:border-box}}button{{width:100%;padding:15px;background:linear-gradient(#FFD700,#ff9900);border:none;border-radius:12px;font-weight:900}}</style></head><body><div style="text-align:center;font-size:28px;font-weight:900;margin:20px">👑 CODEX700 🔥</div><div class="card"><h2 style="text-align:center">REGISTER</h2><p style="color:#ff4444;text-align:center">{msg}</p><form method="post"><input name="name" placeholder="Enter Name"><input name="phone" placeholder="Enter Phone number"><input type="password" name="password" placeholder="Enter Password"><input type="password" name="confirm" placeholder="Confirm Password"><input name="invite" value="{ref}" placeholder="Invitation code"><button>REGISTER</button></form><p style="text-align:center;color:#fff">Have account? <a href="/login" style="color:#FFD700">Login</a></p></div></body>"""

@app.route('/login', methods=['GET','POST'])
def login():
    msg=""
    if request.method=='POST':
        pr=request.form.get('phone','').strip()
        phone=pr.replace('+','').replace(' ','').replace('-','')
        pw=request.form.get('password','').strip()
        if phone in users and users[phone]['pw']==pw:
            session['phone']=phone
            return redirect('/home')
        msg="Dear user,u have entered a wrong information"
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{background:#000;color:#FFD700;font-family:sans-serif;padding:20px}}.card{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff;box-sizing:border-box}}button{{width:100%;padding:15px;background:linear-gradient(#FFD700,#ff9900);border:none;border-radius:12px;font-weight:900}}</style></head><body><div style="text-align:center;font-size:28px;font-weight:900;margin:20px">👑 CODEX700 🔥</div><div class="card"><h2 style="text-align:center">LOGIN</h2><p style="color:#ff4444;text-align:center">{msg}</p><form method="post"><input name="phone" placeholder="Enter Phone number"><input type="password" name="password" placeholder="Enter Password"><button>LOGIN</button></form><p style="text-align:center;color:#fff">No account? <a href="/register" style="color:#FFD700">Register</a></p></div></body>"""

@app.route('/home')
@login_required_page
def home():
    u=users[session['phone']]
    body=f"""
    <div class="card"><h3 class="gold">Welcome Back</h3><h2 class="red">{u['name'].upper()}</h2><p>VIP 1 | Wallet: <b class="gold">UGX {u['wallet']}</b></p><a href="/deposit"><button class="btn">Deposit</button></a></div>
    <div class="grid"><div class="box">Wallet<br><b class="red">UGX {u['wallet']}</b></div><div class="box">Invested<br><b class="red">UGX {u['invested']}</b></div><div class="box">Income<br><b class="red">UGX {u['income']}</b></div><div class="box">Active<br><b class="red">{u['active']}</b></div></div>
    <div class="card" style="text-align:center;background:linear-gradient(90deg,#2a0a0a,#000)"><h2 class="gold">GROW YOUR WEALTH WITH CODEX</h2><a href="/invest"><button class="btn" style="width:auto;padding:10px 30px">INVEST NOW</button></a></div>
    <div class="grid">
      <a href="/invest" style="text-decoration:none;color:#fff"><div class="box">📈<br>INVEST</div></a>
      <a href="/deposit" style="text-decoration:none;color:#fff"><div class="box">💰<br>DEPOSIT</div></a>
      <a href="/withdraw" style="text-decoration:none;color:#fff"><div class="box">🏧<br>WITHDRAW</div></a>
      <a href="/referrals" style="text-decoration:none;color:#fff"><div class="box">👥<br>REFERRALS</div></a>
      <a href="/checkin" style="text-decoration:none;color:#fff"><div class="box">🎁<br>DAILY REWARD</div></a>
      <a href="/raffle" style="text-decoration:none;color:#fff"><div class="box">🏆<br>RAFFLE</div></a>
      <a href="/transactions" style="text-decoration:none;color:#fff"><div class="box">📄<br>TRANSACTIONS</div></a>
      <a href="/support" style="text-decoration:none;color:#fff"><div class="box">🎧<br>SUPPORT</div></a>
    </div>
    <div class="card"><h3 class="red">INVESTMENT PLANS <a href="/invest" style="float:right;font-size:12px">VIEW ALL</a></h3>
      <p>Starter: UGX 50,000 | 20% daily | 30 Days <a href="/invest?plan=starter"><button class="btn">Invest Now</button></a></p>
      <p>Silver: UGX 250,000 | 20% daily | 30 Days <a href="/invest?plan=silver"><button class="btn">Invest Now</button></a></p>
      <p>Gold: UGX 500,000 | 20% daily | 30 Days <a href="/invest?plan=gold"><button class="btn">Invest Now</button></a></p>
    </div>
    <div class="card" style="text-align:center"><h3>NEED HELP?</h3><p>Contact our support team</p><a href="/support"><button class="btn">CONTACT SUPPORT</button></a></div>
    """
    return layout("Home", body, "home")

@app.route('/home2')
@login_required_page
def home2():
    items=[("My Investments","/investments","📈"),("Deposit","/deposit","💰"),("Withdraw","/withdraw","🏧"),("Transactions","/transactions","📄"),("Referrals","/referrals","👥"),("Raffle","/raffle","🏆"),("Daily Reward","/checkin","🎁"),("Support","/support","🎧"),("Chat Manager","/chat","💬"),("Account","/account","👤"),("Notifications","/notifications","🔔"),("Settings","/settings","⚙️")]
    cards="".join([f'<a href="{l}" style="text-decoration:none;color:#fff"><div class="box" style="padding:25px"><div style="font-size:30px">{i}</div><br>{n}</div></a>' for n,l,i in items])
    body=f'<div class="card" style="text-align:center"><h2 class="gold">CODEX</h2><p class="red">MORE FEATURES</p></div><div class="grid" style="grid-template-columns:1fr 1fr">{cards}</div>'
    return layout("More", body, "home")

@app.route('/checkin', methods=['GET','POST'])
@login_required_page
def checkin():
    u=users[session['phone']]; msg=""
    today=str(date.today())
    if request.method=='POST':
        if u['last_checkin']==today:
            msg="You have already claimed today's reward."
        else:
            u['last_checkin']=today; u['wallet']+=500; u['income']+=500
            u['tx'].append({'date':today,'type':'Daily Reward','amount':500,'status':'Completed','ref':'CHECKIN'})
            msg="Congratulations! UGX 500 has been added to your wallet."
    body=f'<div class="card" style="text-align:center"><h2>Daily Check-In Reward</h2><p>Claim your daily reward</p><h1 class="gold">UGX 500</h1><p class="gold">{msg}</p><form method="post"><button class="btn">CLAIM NOW</button></form></div>'
    return layout("Checkin", body)

@app.route('/deposit', methods=['GET','POST'])
@login_required_page
def deposit():
    u=users[session['phone']]; msg=""
    if request.method=='POST':
        try: amt=int(request.form.get('amount',0))
        except: amt=0
        ref=request.form.get('ref','').strip()
        if amt<1000 or not ref: msg="Dear user,u have entered a wrong information"
        else:
            u['tx'].append({'date':str(date.today()),'type':'Deposit','amount':amt,'status':'Pending','ref':ref})
            u['notif'].append(f"Deposit UGX {amt} submitted")
            msg=f"Deposit UGX {amt} submitted. Awaiting confirmation."
    body=f'<div class="card"><h2>Deposit</h2><p>Wallet: <b class="gold">UGX {u["wallet"]}</b></p><p class="gold">{msg}</p><form method="post"><input name="amount" placeholder="Amount UGX" type="number"><select><option>MTN Mobile Money</option><option>Airtel Money</option></select><p style="font-size:12px">Send to 0771234567 - Codex Ltd, then enter Tx ID below</p><input name="ref" placeholder="Transaction / Reference ID"><button class="btn">Submit Deposit</button></form></div>'
    return layout("Deposit", body)

@app.route('/withdraw', methods=['GET','POST'])
@login_required_page
def withdraw():
    u=users[session['phone']]; msg=""
    if request.method=='POST':
        try: amt=int(request.form.get('amount',0))
        except: amt=0
        phone=request.form.get('mm','').strip()
        if amt>u['wallet']: msg="Insufficient balance."
        elif amt<5000 or not phone: msg="Dear user,u have entered a wrong information"
        else:
            u['wallet']-=amt
            u['tx'].append({'date':str(date.today()),'type':'Withdraw','amount':amt,'status':'Pending','ref':phone})
            msg=f"Withdrawal UGX {amt} submitted."
    body=f'<div class="card"><h2>Withdraw</h2><p>Available: <b class="gold">UGX {u["wallet"]}</b></p><p class="red">{msg}</p><form method="post"><input name="amount" type="number" placeholder="Amount"><input name="mm" placeholder="Mobile Money Number"><button class="btn">Submit Withdrawal</button></form></div>'
    return layout("Withdraw", body)

@app.route('/invest')
@login_required_page
def invest():
    plan=request.args.get('plan','')
    msg=f"<p class='gold'>Selected plan: {plan}</p>" if plan else ""
    body=f'<div class="card"><h2 class="red">INVESTMENT PLANS</h2>{msg}<p>Starter - UGX 50,000 - 20% daily - 30 Days <a href="/invest?plan=starter"><button class="btn">Invest Now</button></a></p><p>Silver - UGX 250,000 - 20% daily - 30 Days <a href="/invest?plan=silver"><button class="btn">Invest Now</button></a></p><p>Gold - UGX 500,000 - 20% daily - 30 Days <a href="/invest?plan=gold"><button class="btn">Invest Now</button></a></p><p>Platinum - UGX 1,000,000 - 20% daily - 30 Days <a href="/invest?plan=platinum"><button class="btn">Invest Now</button></a></p></div>'
    return layout("Invest", body, "invest")

@app.route('/investments')
@login_required_page
def investments():
    u=users[session['phone']]
    invs="".join([f"<p>{x['plan']} - UGX {x['amount']} - {x['status']}</p>" for x in u['investments']]) or "<p>No investments yet.</p>"
    body=f'<div class="card"><h2>My Investments</h2><h3>Active</h3>{invs}<h3>Completed</h3><p>None</p></div>'
    return layout("Investments", body)

@app.route('/referrals')
@login_required_page
def referrals():
    u=users[session['phone']]
    link=f"https://codex700com.onrender.com/register?ref={session['phone'][-6:]}"
    body=f'''<div class="card"><h2>Referrals</h2><p>Link:</p><input id="rl" value="{link}" readonly><button class="btn" onclick="navigator.clipboard.writeText(document.getElementById('rl').value);alert('Referral link copied.')">Copy</button><p>Total: {u['referrals']} | Active: {u['referrals']} | Earnings: UGX {u['ref_earn']}</p></div>'''
    return layout("Referrals", body, "ref")

@app.route('/transactions')
@login_required_page
def transactions():
    u=users[session['phone']]
    rows="".join([f"<p>{t['date']} | {t['type']} | UGX {t['amount']} | {t['status']} | {t['ref']}</p>" for t in u['tx']]) or "<p>No transactions.</p>"
    body=f'<div class="card"><h2>Transactions</h2>{rows}</div>'
    return layout("Transactions", body, "trans")

@app.route('/raffle')
@login_required_page
def raffle():
    body='<div class="card" style="text-align:center"><h2 class="red">RAFFLE DRAW</h2><p>Win amazing prizes daily</p><p>🏆 Daily draw at 8PM EAT</p><button class="btn">Join Raffle - UGX 5000</button></div>'
    return layout("Raffle", body)

@app.route('/support')
@login_required_page
def support():
    body='<div class="card" style="text-align:center"><h2>NEED HELP?</h2><p>Contact our support team</p><a href="https://wa.me/256771234567"><button class="btn">CONTACT SUPPORT</button></a></div>'
    return layout("Support", body)

@app.route('/notifications')
@login_required_page
def notifications():
    u=users[session['phone']]
    n="".join([f"<p>• {x}</p>" for x in u['notif']]) or "<p>No new notifications.</p>"
    body=f'<div class="card"><h2>Notifications</h2>{n}</div>'
    return layout("Notif", body)

@app.route('/account')
@login_required_page
def account():
    u=users[session['phone']]
    body=f'<div class="card"><h2>Account</h2><p>Username: {u["name"]}</p><p>Phone: {u["phone"]}</p><p>Status: Active</p><p>Wallet: <b class="gold">UGX {u["wallet"]}</b></p><a href="/logout"><button class="btn">Logout</button></a></div>'
    return layout("Account", body, "acc")

@app.route('/chat')
@login_required_page
def chat():
    return layout("Chat", '<div class="card"><h2>Chat Manager</h2><p>Online 24/7</p><button class="btn">Start Chat</button></div>')

@app.route('/settings')
@login_required_page
def settings():
    return layout("Settings", '<div class="card"><h2>Settings</h2><p>Notifications: ON</p><p>Language: English</p></div>')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

# keep old dashboard redirect
@app.route('/dashboard')
def dash(): return redirect('/home')

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
