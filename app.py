from flask import Flask, request, redirect, session
from datetime import date, datetime, timedelta
import uuid
app = Flask(__name__)
app.secret_key="codex700secret"
users={}
chats={} # phone -> list of {from, text, time}
ADMIN_PHONE="256700000000"
PLANS={
 'starter':{'name':'Starter Plan','price':50000,'daily':20000,'duration':30,'total':600000,'received':600000,'emoji':'🪴'},
 'bronze':{'name':'Bronze Plan','price':100000,'daily':50000,'duration':30,'total':1500000,'received':1500000,'emoji':'🪙'},
 'silver':{'name':'Silver Plan','price':250000,'daily':100000,'duration':30,'total':3000000,'received':3000000,'emoji':'🧱'},
 'gold':{'name':'Gold Plan','price':500000,'daily':100000,'duration':30,'total':3000000,'received':3000000,'emoji':'🏆'},
 'platinum':{'name':'Platinum Plan','price':1000000,'daily':200000,'duration':30,'total':6000000,'received':7000000,'emoji':'💎'},
 'diamond':{'name':'Diamond Plan','price':2000000,'daily':400000,'duration':30,'total':12000000,'received':14000000,'emoji':'💠'},
 'vip':{'name':'VIP Plan','price':5000000,'daily':1000000,'duration':30,'total':30000000,'received':35000000,'emoji':'👑'},
 'exclusive':{'name':'Exclusive Plan','price':10000000,'daily':2000000,'duration':30,'total':60000000,'received':70000000,'emoji':'🔐'},
}
def require_login(): return 'phone' in session
def get_user(): return users.get(session.get('phone'))
def credit_daily_returns(u):
    today=date.today()
    for inv in u['investments']:
        if inv['status']!='ACTIVE': continue
        # check end date
        end = datetime.strptime(inv['end_date'], "%Y-%m-%d").date()
        if today > end:
            inv['status']='COMPLETED'; continue
        # credit if last_return_at!= today (unique per day)
        if inv['last_return_at']==str(today): continue
        # only credit if at least 1 day since start and not future
        start = datetime.strptime(inv['start_date'], "%Y-%m-%d").date()
        if today <= start: continue
        # credit
        inv['last_return_at']=str(today)
        inv['total_accrued']+=inv['daily_return']
        u['wallet']+=inv['daily_return']
        u['income']+=inv['daily_return']
        rid=f"{inv['id']}_{today}"
        if rid not in u['return_ledger']:
            u['return_ledger'].add(rid)
            u['tx'].append({'date':str(today),'type':'Daily Return','amount':inv['daily_return'],'status':'Completed','ref':inv['id'][:8]})
def base(body, active="home"):
    return f"""<head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
    body{{background:#000;color:#fff;font-family:Arial;margin:0;padding-bottom:75px}}a{{text-decoration:none;color:inherit}}
  .top{{display:flex;justify-content:space-between;padding:12px 15px}}.logo{{color:#FFD700;font-weight:900;font-size:22px}}.logo span{{color:#ff2222}}
  .btn-red{{background:#cc1111;color:#fff;border:none;padding:12px 20px;border-radius:10px;font-weight:bold;width:100%}}
  .card{{background:#111;border:1px solid #333;border-radius:12px;padding:15px;margin:10px}}
  .nav{{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:10px;border-top:1px solid #222}}
  .nav a{{font-size:11px;color:#888;text-align:center}}.nav a.on{{color:#ff2222}}
    </style></head><body><div class="top"><a href="/home2">☰</a><div class="logo">🪙 <span>CODEX</span></div><div><a href="/notifications">🔔</a> <a href="/account">👤</a></div></div>{body}
    <div class="nav"><a href="/home" class="{'on' if active=='home' else ''}">🏠<br>Home</a><a href="/invest" class="{'on' if active=='invest' else ''}">📈<br>Invest</a><a href="/transactions">🔄<br>Transactions</a><a href="/referrals">👥<br>Referrals</a><a href="/account">👤<br>Account</a></div></body>"""
@app.route('/')
def root(): return redirect('/home' if require_login() else '/register')
@app.route('/register', methods=['GET','POST'])
def register():
    msg="";ref=request.args.get('ref','')
    if request.method=='POST':
        name=request.form.get('name','').strip();pr=request.form.get('phone','').strip()
        phone=''.join(filter(str.isdigit,pr))
        pw=request.form.get('password','').strip();cpw=request.form.get('confirm','').strip()
        if not name or len(phone)<9 or pw!=cpw or len(pw)<4 or phone in users: msg="Dear user,u have entered a wrong information"
        else:
            users[phone]={'name':name,'pw':pw,'phone':pr,'wallet':0,'invested':0,'income':0,'active':0,'tx':[],'notif':[],'last_checkin':'','referrals':0,'investments':[],'return_ledger':set()}
            session['phone']=phone;return redirect('/home')
    return f"<head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{background:#000;color:#FFD700;padding:20px;font-family:sans-serif}}.c{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff}}button{{width:100%;padding:15px;background:#FFD700;border:none;border-radius:12px;font-weight:900}}</style></head><body><div class='c'><h2 style='text-align:center'>REGISTER</h2><p style='color:red;text-align:center'>{msg}</p><form method='post'><input name='name' placeholder='Enter Name'><input name='phone' placeholder='Enter Phone'><input type='password' name='password' placeholder='Password'><input type='password' name='confirm' placeholder='Confirm'><input name='invite' value='{ref}' placeholder='Invite'><button>REGISTER</button></form><p style='text-align:center;color:#fff'>Have account? <a href='/login' style='color:#FFD700'>Login</a></p></div></body>"
@app.route('/login', methods=['GET','POST'])
def login():
    msg=""
    if request.method=='POST':
        pr=request.form.get('phone','').strip();phone=''.join(filter(str.isdigit,pr));pw=request.form.get('password','').strip()
        if phone in users and users[phone]['pw']==pw: session['phone']=phone;return redirect('/home')
        msg="Dear user,u have entered a wrong information"
    return f"<head><meta name='viewport' content='width=device-width,initial-scale=1'><style>body{{background:#000;color:#FFD700;padding:20px;font-family:sans-serif}}.c{{background:#0a0a0a;border:2px solid #FFD700;border-radius:20px;padding:25px;max-width:420px;margin:auto}}input{{width:100%;padding:14px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:12px;color:#fff}}button{{width:100%;padding:15px;background:#FFD700;border:none;border-radius:12px;font-weight:900}}</style></head><body><div class='c'><h2 style='text-align:center'>LOGIN</h2><p style='color:red;text-align:center'>{msg}</p><form method='post'><input name='phone' placeholder='Phone'><input type='password' name='password' placeholder='Password'><button>LOGIN</button></form></div></body>"
@app.route('/home')
def home():
    if not require_login(): return redirect('/login')
    u=get_user(); credit_daily_returns(u)
    body=f"""<div class="card"><h4>WELCOME BACK,</h4><h2 style="color:#ff2222">{u['name'].upper()}</h2><p>Wallet: <b style="color:#FFD700">UGX {u['wallet']:,}</b></p><a href="/deposit"><button class="btn-red">Deposit</button></a></div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;padding:10px"><div class="card" style="margin:0;text-align:center"><small>Wallet</small><br><b style="color:#ff2222">UGX {u['wallet']:,}</b></div><div class="card" style="margin:0;text-align:center"><small>Invested</small><br><b style="color:#ff2222">UGX {u['invested']:,}</b></div><div class="card" style="margin:0;text-align:center"><small>Income</small><br><b style="color:#ff2222">UGX {u['income']:,}</b></div><div class="card" style="margin:0;text-align:center"><small>Active</small><br><b style="color:#ff2222">{u['active']}</b></div></div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;padding:10px">
    <a href="/invest"><div class="card" style="margin:0;text-align:center">📈<br>Invest</div></a><a href="/deposit"><div class="card" style="margin:0;text-align:center">💰<br>Deposit</div></a><a href="/withdraw"><div class="card" style="margin:0;text-align:center">🏧<br>Withdraw</div></a><a href="/referrals"><div class="card" style="margin:0;text-align:center">👥<br>Referrals</div></a></div>
    <div class="card" style="text-align:center"><a href="/invest"><button class="btn-red">INVEST NOW</button></a></div>"""
    return base(body,"home")
@app.route('/home2')
def home2():
    if not require_login(): return redirect('/login')
    return base('<div class="card"><h2 style="color:#FFD700;text-align:center">MORE FEATURES</h2></div>',"home")
# INVEST SYSTEM
@app.route('/invest')
def invest():
    if not require_login(): return redirect('/login')
    u=get_user(); credit_daily_returns(u)
    def card(pid,p):
        return f'''<div style="background:#0f0f0f;border:1px solid #FFD70044;border-radius:15px;overflow:hidden">
        <div style="height:100px;background:#222;display:flex;align-items:center;justify-content:center;font-size:48px;position:relative">{p['emoji']}<span style="position:absolute;top:8px;left:8px;background:#cc1111;font-size:11px;padding:3px 8px;border-radius:20px">🔥 HOT</span></div>
        <div style="padding:10px"><div style="color:#ff2222;font-weight:900">{p['name']} 🔒</div>
        <div style="font-size:12px;margin:8px 0">PRICE <b style="color:#ff2222;float:right">UGX {p['price']:,}</b><br>DURATION <b style="color:#ff2222;float:right">30 Days</b><br>DAILY <b style="color:#ff2222;float:right">UGX {p['daily']:,}</b></div>
        <div style="text-align:center;background:#1a0a0a;padding:8px;border-radius:8px"><small>TOTAL RECEIVED</small><br><b style="color:#ff2222">UGX {p['received']:,}</b></div>
        <div style="display:flex;gap:5px;margin-top:8px"><a href="/invest/{pid}" style="flex:1"><button class="btn-red">🛒 Invest Now</button></a><a href="/invest/{pid}"><button class="btn-red" style="width:45px">→</button></a></div></div></div>'''
    grid=''.join([card(pid,PLANS[pid]) for pid in PLANS])
    body=f'<div style="padding:15px"><h2 style="color:#ff2222">INVESTMENT PLANS</h2><p>Wallet: <b style="color:#FFD700">UGX {u["wallet"]:,}</b></p></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px">{grid}</div><p style="padding:10px;font-size:11px;color:#888">Configured Daily Return. Projected Total Return. Actual credits are subject to platform rules.</p>'
    return base(body,"invest")
@app.route('/invest/<pid>')
def invest_detail(pid):
    if not require_login(): return redirect('/login')
    if pid not in PLANS: return redirect('/invest')
    u=get_user(); p=PLANS[pid]
    token=str(uuid.uuid4()); session['inv_token']=token
    start=str(date.today()); end=str(date.today()+timedelta(days=p['duration']))
    body=f'''<div class="card"><h2 style="color:#ff2222">{p['name']}</h2>
    <p>Investment Amount: <b>UGX {p['price']:,}</b></p><p>Duration: <b>{p['duration']} Days</b></p>
    <p>Configured Daily Return: <b style="color:#FFD700">UGX {p['daily']:,}</b></p>
    <p>Projected Total Return: <b style="color:#FFD700">UGX {p['received']:,}</b></p>
    <p>Current Wallet: <b>UGX {u['wallet']:,}</b></p><p>Start: {start} | End: {end}</p>
    <p style="font-size:12px;color:#888">Terms: Capital locked for duration. Actual credits subject to platform rules.</p>
    <form method="post" action="/invest/confirm"><input type="hidden" name="pid" value="{pid}"><input type="hidden" name="token" value="{token}"><button class="btn-red">CONFIRM INVESTMENT</button></form><br><a href="/invest"><button class="btn-red" style="background:#333">CANCEL</button></a></div>'''
    return base(body,"invest")
@app.route('/invest/confirm', methods=['POST'])
def invest_confirm():
    if not require_login(): return redirect('/login')
    u=get_user(); pid=request.form.get('pid',''); token=request.form.get('token','')
    if pid not in PLANS: return redirect('/invest')
    # prevent double submit
    if session.get('inv_token')!=token: return redirect('/investments')
    session.pop('inv_token',None)
    p=PLANS[pid]
    # server-side balance check
    if u['wallet'] < p['price']:
        need=p['price']-u['wallet']
        body=f'''<div class="card" style="text-align:center"><h2 style="color:red">INSUFFICIENT FUNDS</h2>
        <p>You need UGX {p['price']:,} to activate this investment.</p>
        <p>Your current wallet balance is UGX {u['wallet']:,}.</p><p>Additional funds required: UGX {need:,}.</p>
        <a href="/deposit"><button class="btn-red">DEPOSIT FUNDS</button></a><br><br><a href="/invest"><button class="btn-red" style="background:#333">CANCEL</button></a></div>'''
        return base(body,"invest")
    # deduct atomically
    u['wallet']-=p['price']; u['invested']+=p['price']; u['active']=len([x for x in u['investments'] if x['status']=='ACTIVE'])+1
    inv_id=str(uuid.uuid4())
    start=date.today(); end=start+timedelta(days=p['duration'])
    inv={'id':inv_id,'user_id':session['phone'],'plan_id':pid,'plan_name':p['name'],'amount':p['price'],'daily_return':p['daily'],'duration_days':p['duration'],'start_date':str(start),'end_date':str(end),'status':'ACTIVE','total_accrued':0,'last_return_at':'','created_at':str(datetime.now())}
    u['investments'].append(inv)
    u['tx'].append({'date':str(start),'type':'Investment','amount':p['price'],'status':'Active','ref':inv_id[:8]+' '+p['name']})
    u['active']=len([x for x in u['investments'] if x['status']=='ACTIVE'])
    body=f'''<div class="card" style="text-align:center"><h2 style="color:#00ff88">INVESTMENT ACTIVATED</h2>
    <p>Plan: {p['name']}</p><p>Amount: UGX {p['price']:,}</p><p>Start Date: {start}</p><p>End Date: {end}</p><p>Status: ACTIVE</p>
    <a href="/investments"><button class="btn-red">VIEW MY INVESTMENT</button></a></div>'''
    return base(body,"invest")
@app.route('/investments')
def investments():
    if not require_login(): return redirect('/login')
    u=get_user(); credit_daily_returns(u)
    cards=""
    for inv in u['investments']:
        s=datetime.strptime(inv['start_date'],"%Y-%m-%d").date(); e=datetime.strptime(inv['end_date'],"%Y-%m-%d").date()
        total_days=(e-s).days or 1; elapsed=(date.today()-s).days; elapsed=max(0,min(elapsed,total_days))
        pct=int(elapsed/total_days*100); remain=total_days-elapsed
        cards+=f'''<div class="card"><h3 style="color:#ff2222">{inv['plan_name']}</h3>
        <p>Amount: UGX {inv['amount']:,} | Status: {inv['status']}</p><p>Start: {inv['start_date']} | End: {inv['end_date']}</p>
        <p>Daily Return: UGX {inv['daily_return']:,} | Accrued: UGX {inv['total_accrued']:,}</p><p>Remaining: {remain} days</p>
        <div style="background:#222;border-radius:10px;height:12px"><div style="width:{pct}%;background:#cc1111;height:12px;border-radius:10px"></div></div>
        <p>START {"█"*int(pct/10)}{"░"*int(10-pct/10)} END</p><p>NEXT RETURN: <span class="cd">23:59:59</span></p></div>'''
    if not cards: cards='<div class="card"><p>No investments yet.</p></div>'
    return base(f'<div style="padding:15px"><h2>MY INVESTMENTS</h2></div>{cards}<script>setInterval(()=>{{document.querySelectorAll(".cd").forEach(e=>{{let t=e.textContent.split(":").map(Number);let s=t[0]*3600+t[1]*60+t[2]-1;if(s<0)s=86399;e.textContent=new Date(s*1000).toISOString().substr(11,8)}})}},1000)</script>',"invest")
# other simple routes
@app.route('/deposit', methods=['GET','POST'])
def deposit():
    if not require_login(): return redirect('/login')
    u=get_user();msg=""
    if request.method=='POST':
        try: amt=int(request.form.get('amount',0))
        except: amt=0
        ref=request.form.get('ref','').strip()
        if amt<1000 or not ref: msg="Dear user,u have entered a wrong information"
        else: u['tx'].append({'date':str(date.today()),'type':'Deposit','amount':amt,'status':'Pending','ref':ref});msg="Deposit submitted."
    return base(f'<div class="card"><h2>Deposit</h2><p>Wallet: UGX {u["wallet"]:,}</p><p>{msg}</p><form method="post"><input name="amount" type="number" placeholder="Amount" style="width:100%;padding:12px;margin:8px 0"><input name="ref" placeholder="Tx ID" style="width:100%;padding:12px;margin:8px 0"><button class="btn-red">Submit</button></form></div>')
@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    if not require_login(): return redirect('/login')
    u=get_user();msg=""
    if request.method=='POST':
        try: amt=int(request.form.get('amount',0))
        except: amt=0
        mm=request.form.get('mm','').strip()
        if amt>u['wallet']: msg="Insufficient balance."
        elif amt<5000: msg="Dear user,u have entered a wrong information"
        else: u['wallet']-=amt;u['tx'].append({'date':str(date.today()),'type':'Withdraw','amount':amt,'status':'Pending','ref':mm});msg="Submitted."
    return base(f'<div class="card"><h2>Withdraw</h2><p>UGX {u["wallet"]:,}</p><p style="color:red">{msg}</p><form method="post"><input name="amount" type="number" placeholder="Amount" style="width:100%;padding:12px"><input name="mm" placeholder="MM Number" style="width:100%;padding:12px;margin:8px 0"><button class="btn-red">Submit</button></form></div>')
@app.route('/transactions')
def transactions():
    if not require_login(): return redirect('/login')
    u=get_user();rows="".join([f"<p>{t['date']} | {t['type']} | UGX {t['amount']:,} | {t['status']} | {t['ref']}</p>" for t in u['tx']]) or "<p>No transactions</p>"
    return base(f'<div class="card"><h2>Transactions</h2>{rows}</div>')
@app.route('/referrals')
def referrals():
    if not require_login(): return redirect('/login')
    return base('<div class="card"><h2>Referrals</h2><p>Link copied feature</p></div>')
@app.route('/checkin', methods=['GET','POST'])
def checkin():
    if not require_login(): return redirect('/login')
    u=get_user();msg="";today=str(date.today())
    if request.method=='POST':
        if u['last_checkin']==today: msg="You have already claimed today's reward."
        else: u['last_checkin']=today;u['wallet']+=500;u['income']+=500;u['tx'].append({'date':today,'type':'Daily Reward','amount':500,'status':'Completed','ref':'CHECKIN'});msg="Congratulations! UGX 500 added."
    return base(f'<div class="card" style="text-align:center"><h2>Daily Reward</h2><h1 style="color:#FFD700">UGX 500</h1><p>{msg}</p><form method="post"><button class="btn-red">CLAIM NOW</button></form></div>')
@app.route('/raffle')
def raffle():
    if not require_login(): return redirect('/login')
    return base('<div class="card"><h2 style="color:#ff2222">RAFFLE DRAW</h2></div>')
@app.route('/support')
def support():
    if not require_login(): return redirect('/login')
    return base('<div class="card"><h2>Support</h2></div>')
@app.route('/notifications')
def notifications():
    if not require_login(): return redirect('/login')
    return base('<div class="card"><p>No new notifications.</p></div>')
@app.route('/account')
def account():
    if not require_login(): return redirect('/login')
    u=get_user()
    return base(f'<div class="card"><h2>{u["name"]}</h2><p>Wallet: UGX {u["wallet"]:,}</p><a href="/logout"><button class="btn-red">Logout</button></a></div>')
@app.route('/chat', methods=['GET','POST'])
def chat():
    if not require_login(): return redirect('/login')
    phone=session['phone']
    if phone not in chats: chats[phone]=[]
    if request.method=='POST':
        msg=request.form.get('msg','').strip()
        if msg:
            from datetime import datetime
            chats[phone].append({'from':'user','text':msg,'time':datetime.now().strftime("%H:%M")})
    msgs="".join([f"<div style='margin:8px;padding:10px;border-radius:10px;max-width:80%;{'background:#cc1111;margin-left:auto' if m['from']=='admin' else 'background:#222'}><small>{'Manager' if m['from']=='admin' else 'You'} {m['time']}</small><br>{m['text']}</div>" for m in chats[phone]])
    body=f"""<div class="card"><h2 style="color:#ff2222">💬 Chat Manager</h2><div style="height:300px;overflow-y:auto;background:#0a0a0a;border-radius:10px;padding:10px">{msgs or '<p style=color:#888>Start chatting with your manager...</p>'}</div><form method="post" style="display:flex;gap:8px;margin-top:10px"><input name="msg" placeholder="Type message..." style="flex:1;padding:12px;border-radius:10px;border:1px solid #333;background:#1a1a1a;color:#fff"><button class="btn-red" style="width:80px">Send</button></form></div>"""
    return base(body)
@app.route('/admin/chats')
def admin_chats():
    if not require_login(): return redirect('/login')
    # simple admin check - allow any logged user for now, shows all chats
    ll="".join([f"<a href='/admin/chat/{ph}'><div class='card'><b>{ph}</b> - {len(msgs)} msgs - {msgs[-1]['text'][:30] if msgs else 'no msgs'}</div></a>" for ph,msgs in chats.items()]) or "<div class='card'><p>No chats yet</p></div>"
    return base(f"<h2 style='padding:15px;color:#FFD700'>Admin Inbox</h2>{ll}")
@app.route('/admin/chat/<ph>', methods=['GET','POST'])
def admin_chat_detail(ph):
    if not require_login(): return redirect('/login')
    if ph not in chats: chats[ph]=[]
    if request.method=='POST':
        msg=request.form.get('msg','').strip()
        if msg:
            from datetime import datetime
            chats[ph].append({'from':'admin','text':msg,'time':datetime.now().strftime("%H:%M")})
    msgs="".join([f"<div style='margin:8px;padding:10px;border-radius:10px;max-width:80%;{'background:#FFD700;color:#000;margin-left:auto' if m['from']=='admin' else 'background:#222'}'}><small>{m['from']} {m['time']}</small><br>{m['text']}</div>" for m in chats[ph]])
    body=f"""<div class="card"><h3>Chat with {ph}</h3><div style="height:300px;overflow-y:auto;background:#0a0a0a;padding:10px;border-radius:10px">{msgs}</div><form method="post" style="display:flex;gap:8px;margin-top:10px"><input name="msg" placeholder="Reply privately..." style="flex:1;padding:12px;border-radius:10px;background:#1a1a1a;border:1px solid #333;color:#fff"><button class="btn-red" style="width:80px">Reply</button></form><br><a href="/admin/chats">← Back to inbox</a></div>"""
    return base(body)
@app.route('/logout')
def logout(): session.clear();return redirect('/login')
@app.route('/dashboard')
def dash(): return redirect('/home')
if __name__=='__main__': app.run(host='0.0.0.0',port=5000)
