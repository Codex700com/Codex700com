from flask import Flask, request, redirect, session
from datetime import date
app = Flask(__name__)
app.secret_key="codex700secret"
users={}

def require_login(): return 'phone' in session

def base(body, active="home"):
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><style>
    *{{box-sizing:border-box}} body{{background:#000;color:#fff;font-family:Arial,sans-serif;margin:0;padding-bottom:75px}}
    a{{text-decoration:none;color:inherit}}
   .top{{display:flex;justify-content:space-between;align-items:center;padding:12px 15px}}
   .logo{{color:#FFD700;font-weight:900;font-size:22px}}.logo span{{color:#ff2222}}
   .banner{{margin:10px;border-radius:15px;overflow:hidden;position:relative;background:linear-gradient(90deg,#1a0000,#000);border:1px solid #FFD70044;min-height:160px;display:flex}}
   .banner-left{{padding:20px;flex:1}}.banner-left h4{{margin:0;font-size:14px}}.banner-left h2{{color:#ff2222;margin:5px 0}}
   .banner-right{{flex:1;background:url('https://images.unsplash.com/photo-1620121692029-d088224ddc74?w=400') center/cover;min-height:160px}}
   .btn-red{{background:#cc1111;color:#fff;border:none;padding:10px 20px;border-radius:8px;font-weight:bold}}
   .stats{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;padding:10px}}
   .stat{{background:#111;border:1px solid #222;border-radius:12px;padding:12px 5px;text-align:center}}
   .stat small{{font-size:11px;color:#ccc}}.stat b{{color:#ff2222;display:block;margin-top:5px;font-size:13px}}
   .check{{margin:10px;background:linear-gradient(90deg,#2a0a0a,#1a0a0a);border-radius:12px;padding:12px;display:flex;justify-content:space-between;align-items:center;border:1px solid #FFD70022}}
   .grid8{{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;padding:10px}}
   .icon{{background:#111;border:1px solid #222;border-radius:12px;padding:15px 5px;text-align:center;font-size:12px}}
   .raffle{{margin:10px;background:linear-gradient(90deg,#1a0a00,#000);border-radius:12px;padding:15px;display:flex;justify-content:space-between;align-items:center;border:1px solid #FFD70022}}
   .plans{{display:flex;gap:10px;overflow-x:auto;padding:10px}}
   .plan{{min-width:160px;background:#111;border-radius:12px;overflow:hidden;border:1px solid #222}}
   .plan-img{{height:80px;background:#333}}.plan-body{{padding:10px;font-size:12px}}
   .plan-body span{{color:#ff2222;float:right}}.plan-body b{{color:#fff}}
   .help{{margin:10px;background:#111;border-radius:12px;padding:15px;display:flex;justify-content:space-between;align-items:center}}
   .nav{{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px 5px;border-top:1px solid #222;z-index:99}}
   .nav a{{font-size:11px;color:#888;text-align:center}}.nav a.on{{color:#ff2222}}
    </style></head><body>
    <div class="top"><a href="/home2" style="font-size:24px">☰</a><div class="logo">🪙 <span>CODEX</span></div><div><a href="/notifications">🔔<sup style="background:red;border-radius:50%;padding:2px 5px">3</sup></a> <a href="/account">👤</a></div></div>
    {body}
    <div class="nav">
      <a href="/home" class="{'on' if active=='home' else ''}">🏠<br>Home</a>
      <a href="/invest" class="{'on' if active=='invest' else ''}">📈<br>Invest</a>
      <a href="/transactions" class="{'on' if active=='trans' else ''}">🔄<br>Transactions</a>
      <a href="/referrals" class="{'on' if active=='ref' else ''}">👥<br>Referrals</a>
      <a href="/account" class="{'on' if active=='acc' else ''}">👤<br>Account</a>
    </div></body>"""

def card_wrap(t,b): return f'<div style="background:#111;border:1px solid #333;border-radius:12px;padding:15px;margin:10px"><h2>{t}</h2>{b}</div>'

@app.route('/')
def root(): return redirect('/home' if require_login() else '/register')
@app.route('/register', methods=['GET','POST'])
def register():
    msg="";ref=request.args.get('ref','')
    if request.method=='POST':
        name=request.form.get('name','').strip();pr=request.form.get('phone','').strip()
        phone=pr.replace('+','').replace(' ','').replace('-','')
        pw=request.form.get('password','').strip();cpw=request.form.get('confirm','').strip()
        if not name or not phone.isdigit() or len(phone)<9 or pw!=cpw or len(pw)<4 or phone in users:
            msg="Dear user,u have entered a wrong information"
        else:
            users[phone]={'name':name,'pw':pw,'phone':pr,'wallet':0,'invested':0,'income':0,'active':0,'tx':[],'notif':[],'last_checkin':'','referrals':0,'ref_earn':0,'investments':[]}
            session['phone']=phone;return redirect('/home')
    return f"<head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{background:#000;color:#FFD700;font-family:sans-serif;padding:20px}}.c{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff}}button{{width:100%;padding:15px;background:#FFD700;border:none;border-radius:12px;font-weight:900}}</style></head><body><div class='c'><h2 style='text-align:center'>REGISTER</h2><p style='color:red;text-align:center'>{msg}</p><form method='post'><input name='name' placeholder='Enter Name'><input name='phone' placeholder='Enter Phone number'><input type='password' name='password' placeholder='Enter Password'><input type='password' name='confirm' placeholder='Confirm Password'><input name='invite' value='{ref}' placeholder='Invitation code'><button>REGISTER</button></form><p style='text-align:center;color:#fff'>Have account? <a href='/login' style='color:#FFD700'>Login</a></p></div></body>"

@app.route('/login', methods=['GET','POST'])
def login():
    msg=""
    if request.method=='POST':
        pr=request.form.get('phone','').strip();phone=pr.replace('+','').replace(' ','').replace('-','');pw=request.form.get('password','').strip()
        if phone in users and users[phone]['pw']==pw: session['phone']=phone;return redirect('/home')
        msg="Dear user,u have entered a wrong information"
    return f"<head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{background:#000;color:#FFD700;font-family:sans-serif;padding:20px}}.c{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff}}button{{width:100%;padding:15px;background:#FFD700;border:none;border-radius:12px;font-weight:900}}</style></head><body><div class='c'><h2 style='text-align:center'>LOGIN</h2><p style='color:red;text-align:center'>{msg}</p><form method='post'><input name='phone' placeholder='Enter Phone number'><input type='password' name='password' placeholder='Enter Password'><button>LOGIN</button></form><p style='text-align:center;color:#fff'>No account? <a href='/register' style='color:#FFD700'>Register</a></p></div></body>"

@app.route('/home')
def home():
    if not require_login(): return redirect('/login')
    u=users[session['phone']]
    body=f"""
    <div class="banner"><div class="banner-left"><h4>WELCOME BACK,</h4><h2>{u['name'].upper()}</h2><p style="font-size:13px">Let's grow your wealth together</p><a href="/invest"><button class="btn-red">Invest Now</button></a></div><div class="banner-right"></div></div>
    <div class="stats">
      <div class="stat">💼<br><small>Wallet Balance</small><b>UGX {u['wallet']}</b>👁️</div>
      <div class="stat">📈<br><small>Total Invested</small><b>UGX {u['invested']}</b></div>
      <div class="stat">💰<br><small>Total Income</small><b>UGX {u['income']}</b></div>
      <div class="stat">💼<br><small>Active Plans</small><b>{u['active']}</b></div>
    </div>
    <div class="check"><div>🎁 <b>Daily Check-In Reward</b><br><small>Check in daily and get <span style="color:#ff2222">UGX 500</span></small></div><a href="/checkin"><button class="btn-red">Check In →</button></a></div>
    <div class="grid8">
      <a href="/invest"><div class="icon">📈<br>Invest</div></a>
      <a href="/deposit"><div class="icon">💰<br>Deposit</div></a>
      <a href="/withdraw"><div class="icon">🏧<br>Withdraw</div></a>
      <a href="/referrals"><div class="icon">👥<br>Referrals</div></a>
      <a href="/transactions"><div class="icon">📄<br>Transactions</div></a>
      <a href="/raffle"><div class="icon">🏆<br>Raffle</div></a>
      <a href="/support"><div class="icon">🎧<br>Support</div></a>
      <a href="/chat"><div class="icon">💬<br>Chat Manager</div></a>
    </div>
    <div class="raffle"><div>🏆<br><b style="color:#ff2222">RAFFLE DRAW</b><br><small>Win amazing prizes daily</small><br><a href="/raffle"><button class="btn-red" style="margin-top:8px">View Prizes →</button></a></div><div style="font-size:50px">🎁</div></div>
    <h4 style="color:#ff2222;padding:0 15px">📈 INVESTMENT PLANS <a href="/invest" style="float:right;font-size:12px;color:#ff2222">View All Plans ></a></h4>
    <div class="plans">
      <div class="plan"><div class="plan-img" style="background:linear-gradient(#4a3000,#000)"></div><div class="plan-body"><b>Starter Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 50,000</span><br><a href="/invest?plan=starter"><button class="btn-red" style="width:100%;margin-top:5px;padding:8px">Invest</button></a></div></div>
      <div class="plan"><div class="plan-img" style="background:linear-gradient(#555,#000)"></div><div class="plan-body"><b>Silver Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 250,000</span><br><a href="/invest?plan=silver"><button class="btn-red" style="width:100%;margin-top:5px;padding:8px">Invest</button></a></div></div>
      <div class="plan"><div class="plan-img" style="background:linear-gradient(#8a6d00,#000)"></div><div class="plan-body"><b>Gold Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 500,000</span><br><a href="/invest?plan=gold"><button class="btn-red" style="width:100%;margin-top:5px;padding:8px">Invest</button></a></div></div>
      <div class="plan"><div class="plan-img" style="background:linear-gradient(#888,#000)"></div><div class="plan-body"><b>Platinum Plan</b><br>Daily Return <span>20%</span><br>Duration <span style="color:#fff">30 Days</span><br>Min. Invest <span>UGX 1,000,000</span><br><a href="/invest?plan=platinum"><button class="btn-red" style="width:100%;margin-top:5px;padding:8px">Invest</button></a></div></div>
    </div>
    <div class="help"><div>🎧 <b>Need Help?</b><br><small>Our support team is always here for you.</small></div><a href="/support"><button class="btn-red">Contact Support</button></a></div>
    """
    return base(body,"home")

@app.route('/home2')
def home2():
    if not require_login(): return redirect('/login')
    items=[("My Investments","/investments","📈"),("Deposit","/deposit","💰"),("Withdraw","/withdraw","🏧"),("Transactions","/transactions","📄"),("Referrals","/referrals","👥"),("Raffle","/raffle","🏆"),("Daily Reward","/checkin","🎁"),("Support","/support","🎧"),("Chat Manager","/chat","💬"),("Account","/account","👤"),("Notifications","/notifications","🔔"),("Settings","/settings","⚙️")]
    cards="".join([f'<a href="{l}"><div class="icon" style="padding:25px 5px"><div style="font-size:28px">{i}</div><br>{n}</div></a>' for n,l,i in items])
    return base(f'<div style="text-align:center;padding:20px"><h2 style="color:#FFD700">CODEX</h2><p style="color:#ff2222">MORE FEATURES</p></div><div class="grid8" style="grid-template-columns:1fr 1fr">{cards}</div>',"home")

@app.route('/checkin', methods=['GET','POST'])
def checkin():
    if not require_login(): return redirect('/login')
    u=users[session['phone']];msg="";today=str(date.today())
    if request.method=='POST':
        if u['last_checkin']==today: msg="You have already claimed today's reward."
        else: u['last_checkin']=today;u['wallet']+=500;u['income']+=500;u['tx'].append({'date':today,'type':'Daily Reward','amount':500,'status':'Completed','ref':'CHECKIN'});msg="Congratulations! UGX 500 has been added to your wallet."
    return base(card_wrap("Daily Check-In Reward",f"<p>Claim your daily reward</p><h1 style='color:#FFD700'>UGX 500</h1><p style='color:#FFD700'>{msg}</p><form method='post'><button class='btn-red' style='width:100%'>CLAIM NOW</button></form>"))

@app.route('/deposit', methods=['GET','POST'])
def deposit():
    if not require_login(): return redirect('/login')
    u=users[session['phone']];msg=""
    if request.method=='POST':
        try: amt=int(request.form.get('amount',0))
        except: amt=0
        ref=request.form.get('ref','').strip()
        if amt<1000 or not ref: msg="Dear user,u have entered a wrong information"
        else: u['tx'].append({'date':str(date.today()),'type':'Deposit','amount':amt,'status':'Pending','ref':ref});u['notif'].append(f"Deposit UGX {amt} submitted");msg=f"Deposit UGX {amt} submitted."
    return base(card_wrap("Deposit",f"<p>Wallet: <b style='color:#FFD700'>UGX {u['wallet']}</b></p><p style='color:#FFD700'>{msg}</p><form method='post'><input name='amount' type='number' placeholder='Amount UGX' style='width:100%;padding:12px;margin:8px 0;background:#1a1a1a;border:1px solid #555;border-radius:10px;color:#fff'><input name='ref' placeholder='Transaction ID' style='width:100%;padding:12px;margin:8px 0;background:#1a1a1a;border:1px solid #555;border-radius:10px;color:#fff'><button class='btn-red' style='width:100%'>Submit Deposit</button></form>"))

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    if not require_login(): return redirect('/login')
    u=users[session['phone']];msg=""
    if request.method=='POST':
        try: amt=int(request.form.get('amount',0))
        except: amt=0
        mm=request.form.get('mm','').strip()
        if amt>u['wallet']: msg="Insufficient balance."
        elif amt<5000 or not mm: msg="Dear user,u have entered a wrong information"
        else: u['wallet']-=amt;u['tx'].append({'date':str(date.today()),'type':'Withdraw','amount':amt,'status':'Pending','ref':mm});msg="Withdrawal submitted."
    return base(card_wrap("Withdraw",f"<p>Available: <b style='color:#FFD700'>UGX {u['wallet']}</b></p><p style='color:red'>{msg}</p><form method='post'><input name='amount' type='number' placeholder='Amount' style='width:100%;padding:12px;margin:8px 0;background:#1a1a1a;border:1px solid #555;border-radius:10px;color:#fff'><input name='mm' placeholder='Mobile Money Number' style='width:100%;padding:12px;margin:8px 0;background:#1a1a1a;border:1px solid #555;border-radius:10px;color:#fff'><button class='btn-red' style='width:100%'>Submit Withdrawal</button></form>"))

@app.route('/invest')
def invest():
    if not require_login(): return redirect('/login')
    u=users[session['phone']]
    plan=request.args.get('plan','')
    msg=""
    plans_data={
      'starter':50000,'bronze':100000,'silver':250000,'gold':500000,
      'platinum':1000000,'diamond':2000000,'vip':5000000,'exclusive':10000000
    }
    if plan in plans_data:
        price=plans_data[plan]
        if u['wallet'] < price:
            msg=f"<p style='color:red;text-align:center'>Insufficient balance for {plan}. Please Deposit.</p>"
        else:
            u['wallet']-=price; u['invested']+=price; u['active']+=1
            u['investments'].append({'plan':plan,'amount':price,'status':'Active'})
            u['tx'].append({'date':str(date.today()),'type':'Invest '+plan,'amount':price,'status':'Active','ref':plan.upper()})
            msg=f"<p style='color:#00ff88;text-align:center'>Successfully invested in {plan.upper()}!</p>"
    def card(id_,name,price,daily,total,received,emoji):
        return f'''<div style="background:#0f0f0f;border:1px solid #FFD70044;border-radius:15px;overflow:hidden">
        <div style="position:relative;height:110px;background:linear-gradient(#3a2800,#000);display:flex;align-items:center;justify-content:center;font-size:50px">{emoji}
        <span style="position:absolute;top:8px;left:8px;background:#cc1111;color:#fff;font-size:11px;padding:3px 8px;border-radius:20px">🔥 HOT</span></div>
        <div style="padding:10px"><div style="color:#ff2222;font-weight:900">{name} 🔒</div>
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-top:8px"><div>PRICE<br><b style="color:#ff2222">UGX {price:,}</b><br>DAILY RETURN (20%)<br><b style="color:#ff2222">UGX {daily:,}</b></div><div style="text-align:right">DURATION<br><b style="color:#ff2222">30 Days</b><br>TOTAL RETURN<br><b style="color:#ff2222">UGX {total:,}</b></div></div>
        <div style="text-align:center;margin:10px 0;background:#1a0a0a;border-radius:8px;padding:8px"><small>TOTAL RECEIVED</small><br><b style="color:#ff2222;font-size:18px">UGX {received:,}</b></div>
        <a href="/invest?plan={id_}"><button style="width:100%;background:#cc1111;color:#fff;border:none;padding:12px;border-radius:10px;font-weight:bold">🛒 Invest Now</button></a></div></div>'''
    grid = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px">'
    grid+=card('starter','Starter Plan',50000,20000,600000,600000,'🪴')
    grid+=card('bronze','Bronze Plan',100000,50000,1500000,1500000,'🪙')
    grid+=card('silver','Silver Plan',250000,100000,3000000,3000000,'🧱')
    grid+=card('gold','Gold Plan',500000,100000,3000000,3000000,'🏆')
    grid+=card('platinum','Platinum Plan',1000000,200000,6000000,7000000,'👑')
    grid+=card('diamond','Diamond Plan',2000000,400000,12000000,14000000,'💎')
    grid+=card('vip','VIP Plan',5000000,1000000,30000000,35000000,'👑')
    grid+=card('exclusive','Exclusive Plan',10000000,2000000,60000000,70000000,'🔐')
    grid+='</div>'
    body=f'''<div style="padding:15px"><h2 style="color:#ff2222;margin:0">📈 INVESTMENT PLANS</h2><p style="color:#ff2222;font-size:13px">Choose a plan that suits you</p><p style="color:#fff">Wallet: <b style="color:#FFD700">UGX {u['wallet']:,}</b></p>{msg}</div>{grid}'''
    return base(body,"invest")

@app.route('/investments')
def investments():
    if not require_login(): return redirect('/login')
    u=users[session['phone']]
    invs="".join([f"<p>{x['plan']} - {x['amount']} - {x['status']}</p>" for x in u['investments']]) or "<p>No investments yet.</p>"
    return base(card_wrap("My Investments",invs))
@app.route('/referrals')
def referrals():
    if not require_login(): return redirect('/login')
    u=users[session['phone']];link=f"https://codex700com.onrender.com/register?ref={session['phone'][-6:]}"
    return base(card_wrap("Referrals",f"<input id='rl' value='{link}' readonly style='width:100%;padding:10px'><button class='btn-red' onclick=\"navigator.clipboard.writeText(document.getElementById('rl').value);alert('Referral link copied.')\">Copy</button><p>Total: {u['referrals']}</p>"),"ref")
@app.route('/transactions')
def transactions():
    if not require_login(): return redirect('/login')
    u=users[session['phone']];rows="".join([f"<p>{t['date']} | {t['type']} | UGX {t['amount']} | {t['status']}</p>" for t in u['tx']]) or "<p>No transactions.</p>"
    return base(card_wrap("Transactions",rows),"trans")
@app.route('/raffle')
def raffle():
    if not require_login(): return redirect('/login')
    return base(card_wrap("RAFFLE DRAW","<p>Win amazing prizes daily</p><button class='btn-red'>Join Raffle - UGX 5000</button>"))
@app.route('/support')
def support():
    if not require_login(): return redirect('/login')
    return base(card_wrap("Support","<a href='https://wa.me/256771234567'><button class='btn-red'>CONTACT SUPPORT</button></a>"))
@app.route('/notifications')
def notifications():
    if not require_login(): return redirect('/login')
    u=users[session['phone']];n="".join([f"<p>• {x}</p>" for x in u['notif']]) or "<p>No new notifications.</p>"
    return base(card_wrap("Notifications",n))
@app.route('/account')
def account():
    if not require_login(): return redirect('/login')
    u=users[session['phone']]
    return base(card_wrap("Account",f"<p>{u['name']}</p><p>{u['phone']}</p><p>Wallet: UGX {u['wallet']}</p><a href='/logout'><button class='btn-red'>Logout</button></a>"),"acc")
@app.route('/chat')
def chat():
    if not require_login(): return redirect('/login')
    return base(card_wrap("Chat Manager","<button class='btn-red'>Start Chat</button>"))
@app.route('/settings')
def settings():
    if not require_login(): return redirect('/login')
    return base(card_wrap("Settings","<p>Settings page</p>"))
@app.route('/logout')
def logout(): session.clear();return redirect('/login')
@app.route('/dashboard')
def dash(): return redirect('/home')
if __name__=='__main__': app.run(host='0.0.0.0',port=5000)
