from flask import Flask, request, redirect, session
from datetime import date, datetime, timedelta
import time, uuid

app = Flask(__name__)
app.secret_key = "codex700-v2"
users = {}

PLANS = {
 "starter": {"name":"Starter Plan","price":50000,"daily":20000,"duration":30,"total":600000},
 "bronze": {"name":"Bronze Plan","price":100000,"daily":50000,"duration":30,"total":1500000},
 "silver": {"name":"Silver Plan","price":250000,"daily":100000,"duration":30,"total":3000000},
 "gold": {"name":"Gold Plan","price":500000,"daily":100000,"duration":30,"total":3000000},
 "platinum": {"name":"Platinum Plan","price":1000000,"daily":200000,"duration":30,"total":6000000},
 "diamond": {"name":"Diamond Plan","price":2000000,"daily":400000,"duration":30,"total":12000000},
 "vip": {"name":"VIP Plan","price":5000000,"daily":1000000,"duration":30,"total":30000000},
 "exclusive": {"name":"Exclusive Plan","price":10000000,"daily":2000000,"duration":30,"total":60000000},
}

STYLE = "<meta name='viewport' content='width=device-width,initial-scale=1'><style>body{background:#000;color:#FFD700;font-family:sans-serif;margin:0;padding:20px;padding-bottom:70px}.header{text-align:center;font-size:26px;font-weight:900;margin:15px 0;color:#FFD700}.card{background:#0a0a0a;border:2px solid #FFD700;border-radius:16px;padding:20px;max-width:440px;margin:auto}input{width:100%;padding:13px;margin:8px 0;background:#111;border:1px solid #FFD70088;border-radius:10px;color:#fff;box-sizing:border-box}button{width:100%;padding:14px;background:#FFD700;border:none;border-radius:10px;font-weight:900;cursor:pointer}.link{text-align:center;margin-top:12px;color:#fff}.link a{color:#FFD700}.err{color:#ff5555;text-align:center}</style>"

def credit_daily_returns(u):
    today = date.today()
    for inv in u.get("investments",[]):
        if inv["status"]!="ACTIVE": continue
        end = datetime.strptime(inv["end_date"],"%Y-%m-%d").date()
        if today > end:
            inv["status"]="COMPLETED"; continue
        start = datetime.strptime(inv["start_date"],"%Y-%m-%d").date()
        elapsed = (today-start).days
        for d in range(1, min(elapsed, inv["duration_days"])+1):
            period = str(start+timedelta(days=d))
            key=(inv["id"],period)
            if key in u.get("return_ledger",set()): continue
            u["return_ledger"].add(key)
            u["wallet"]+=inv["daily_return"]; u["income"]+=inv["daily_return"]
            inv["total_accrued"]+=inv["daily_return"]; inv["last_return_at"]=period
            u["tx"].append({"type":"DAILY RETURN","amount":inv["daily_return"],"plan":inv["plan_name"],"date":period,"ref":inv["id"][:8]})

def login_required():
    ph=session.get("phone")
    return ph and ph in users

@app.route('/')
def root(): return redirect('/home' if login_required() else '/register')

@app.route('/register', methods=['GET','POST'])
def register():
    err=""
    if request.method=='POST':
        name=request.form.get('name','').strip()
        phone=''.join(filter(str.isdigit,request.form.get('phone','')))
        pw=request.form.get('password',''); cpw=request.form.get('confirm','')
        if not name: err="Enter Name"
        elif len(phone)<9: err="Phone must be at least 9 digits"
        elif len(pw)<4: err="Password min 4"
        elif pw!=cpw: err="Passwords do not match"
        elif phone in users: err="Phone already registered"
        else:
            users[phone]={'name':name,'pw':pw,'wallet':0,'invested':0,'income':0,'active':0,'last_checkin':'','investments':[],'tx':[],'return_ledger':set()}
            session['phone']=phone; return redirect('/home')
    return "<head>"+STYLE+"</head><body><div class='header'>CODEX700</div><div class='card'><h2 style='text-align:center'>REGISTER</h2><div class='err'>"+err+"</div><form method='post'><input name='name' placeholder='Enter Name'><input name='phone' placeholder='Enter Phone'><input type='password' name='password' placeholder='Password'><input type='password' name='confirm' placeholder='Confirm'><button>REGISTER</button></form><div class='link'>Have account? <a href='/login'>Login</a></div></div></body>"

@app.route('/login', methods=['GET','POST'])
def login():
    err=""
    if request.method=='POST':
        phone=''.join(filter(str.isdigit,request.form.get('phone',''))); pw=request.form.get('password','')
        if phone in users and users[phone]['pw']==pw:
            session['phone']=phone; return redirect('/home')
        err="Wrong phone or password"
    return "<head>"+STYLE+"</head><body><div class='header'>CODEX700</div><div class='card'><h2 style='text-align:center'>LOGIN</h2><div class='err'>"+err+"</div><form method='post'><input name='phone' placeholder='Phone'><input type='password' name='password' placeholder='Password'><button>LOGIN</button></form><div class='link'>No account? <a href='/register'>Register</a></div></div></body>"

@app.route('/home')
def home():
    if not login_required(): return redirect('/login')
    u=users[session['phone']]; credit_daily_returns(u)
    return "<head>"+STYLE+"</head><body><div class='header'>CODEX700</div><div class='card'><h3>WELCOME "+u['name'].upper()+"</h3><p>Wallet: UGX "+f"{u['wallet']:,}"+"</p><p>Invested: UGX "+f"{u['invested']:,}"+" | Income: UGX "+f"{u['income']:,}"+"</p><a href='/invest'><button>INVEST NOW</button></a><div class='link'><a href='/investments'>My Investments</a> | <a href='/transactions'>Transactions</a> | <a href='/logout'>Logout</a></div></div><div style='text-align:center;margin:15px'><a href='/checkin' style='color:#FFD700'>Daily Check-In (+500)</a></div></body>"

@app.route('/checkin')
def checkin():
    if not login_required(): return redirect('/login')
    u=users[session['phone']]; t=str(date.today())
    if u['last_checkin']!=t:
        u['last_checkin']=t; u['wallet']+=500; u['income']+=500
        u['tx'].append({"type":"CHECKIN","amount":500,"plan":"Bonus","date":t,"ref":"chk"})
        msg="Checked in +500"
    else: msg="Already checked in"
    return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px'>"+msg+"<br><a href='/home' style='color:#FFD700'>Home</a></body>"

@app.route('/invest')
def invest():
    if not login_required(): return redirect('/login')
    u=users[session['phone']]; credit_daily_returns(u)
    cards=""
    for pid,p in PLANS.items():
        cards+="<div class='card' style='margin:10px auto'><b style='color:#ff3333'>HOT "+p['name']+"</b><p>Price: UGX "+f"{p['price']:,}"+" | Duration: "+str(p['duration'])+" Days</p><p>Daily: UGX "+f"{p['daily']:,}"+" | Total: UGX "+f"{p['total']:,}"+"</p><div style='display:flex;gap:8px'><a href='/invest/"+pid+"' style='flex:1'><button>Invest Now</button></a><a href='/invest/"+pid+"'><button style='width:60px'>-&gt;</button></a></div></div>"
    return "<head>"+STYLE+"</head><body><div class='header'>INVESTMENT PLANS</div>"+cards+"<div class='link'><a href='/home'>Home</a> | <a href='/investments'>My Investments</a></div><p style='color:#777;font-size:12px;text-align:center'>Configured Daily Return - Projected Total Return<br>Actual credits subject to platform rules.</p></body>"

@app.route('/invest/<pid>')
def invest_detail(pid):
    if not login_required(): return redirect('/login')
    if pid not in PLANS: return redirect('/invest')
    p=PLANS[pid]; u=users[session['phone']]
    s=str(date.today()); e=str(date.today()+timedelta(days=p['duration']))
    return "<head>"+STYLE+"</head><body><div class='header'>CODEX700</div><div class='card'><h2>"+p['name']+"</h2><p>Investment Amount: UGX "+f"{p['price']:,}"+"</p><p>Duration: "+str(p['duration'])+" Days</p><p>Configured Daily Return: UGX "+f"{p['daily']:,}"+"</p><p>Projected Total Return: UGX "+f"{p['total']:,}"+"</p><p>Wallet Balance: UGX "+f"{u['wallet']:,}"+"</p><p>Start: "+s+" End: "+e+"</p><form method='post' action='/invest/confirm'><input type='hidden' name='pid' value='"+pid+"'><button>CONFIRM INVESTMENT</button></form><div class='link'><a href='/invest'>CANCEL</a></div></div></body>"

@app.route('/invest/confirm', methods=['POST'])
def invest_confirm():
    if not login_required(): return redirect('/login')
    pid=request.form.get('pid','')
    if pid not in PLANS: return redirect('/invest')
    p=PLANS[pid]; u=users[session['phone']]
    now=time.time()
    if u.get("_lt") and now-u["_lt"]<5 and u.get("_lp")==pid: return redirect('/investments')
    if u["wallet"] < p["price"]:
        need=p["price"]-u["wallet"]
        return "<head>"+STYLE+"</head><body><div class='card'><h2 style='color:#ff4444;text-align:center'>INSUFFICIENT FUNDS</h2><p>You need UGX "+f"{p['price']:,}"+" to activate "+p['name']+".</p><p>Your balance is UGX "+f"{u['wallet']:,}"+"</p><p>Additional required: UGX "+f"{need:,}"+"</p><a href='/deposit'><button>DEPOSIT FUNDS</button></a><div class='link'><a href='/invest'>CANCEL</a></div></div></body>"
    u["wallet"]-=p["price"]
    if u["wallet"]<0:
        u["wallet"]+=p["price"]; return "Blocked: negative wallet"
    u["invested"]+=p["price"]; u["active"]+=1
    s=date.today(); e=s+timedelta(days=p["duration"])
    inv={"id":uuid.uuid4().hex,"user_id":session['phone'],"plan_id":pid,"plan_name":p["name"],"amount":p["price"],"daily_return":p["daily"],"duration_days":p["duration"],"start_date":str(s),"end_date":str(e),"status":"ACTIVE","total_accrued":0,"last_return_at":"","created_at":str(datetime.now())}
    u["investments"].append(inv)
    u["tx"].append({"type":"INVESTMENT","amount":-p["price"],"plan":p["name"],"date":str(s),"ref":inv["id"][:8]})
    u["_lt"]=now; u["_lp"]=pid
    return "<head>"+STYLE+"</head><body><div class='card'><h2>INVESTMENT ACTIVATED</h2><p>Plan: "+p['name']+"</p><p>Amount: UGX "+f"{p['price']:,}"+"</p><p>Start: "+str(s)+"</p><p>End: "+str(e)+"</p><p>Status: ACTIVE</p><a href='/investments'><button>VIEW MY INVESTMENT</button></a></div></body>"

@app.route('/investments')
def my_investments():
    if not login_required(): return redirect('/login')
    u=users[session['phone']]; credit_daily_returns(u)
    today=date.today(); cards=""
    for inv in u.get("investments",[]):
        end=datetime.strptime(inv["end_date"],"%Y-%m-%d").date()
        rem=max(0,(end-today).days)
        pct=int(100*(inv["duration_days"]-rem)/inv["duration_days"]) if inv["duration_days"] else 0
        cards+="<div class='card' style='margin:10px auto'><b>"+inv["plan_name"]+"</b> - "+inv["status"]+"<br>Amount: UGX "+f"{inv['amount']:,}"+" | Daily: UGX "+f"{inv['daily_return']:,}"+"<br>Start: "+inv["start_date"]+" End: "+inv["end_date"]+"<br>Accrued: UGX "+f"{inv['total_accrued']:,}"+" | Remaining: "+str(rem)+" days<div style='background:#222;border-radius:8px;margin:8px 0'><div style='width:"+str(pct)+"%;background:#FFD700;height:10px;border-radius:8px'></div></div><small>NEXT RETURN: <span class='cd'>23:59:59</span> (server-credited)</small></div>"
    if not cards: cards="<p style='color:#fff;text-align:center'>No investments yet</p>"
    return "<head>"+STYLE+"<script>setInterval(()=>document.querySelectorAll('.cd').forEach(e=>{let t=e.textContent.split(':').map(Number);let s=t[0]*3600+t[1]*60+t[2]-1;if(s<0)s=86399;e.textContent=[Math.floor(s/3600),Math.floor(s%3600/60),s%60].map(n=>String(n).padStart(2,'0')).join(':')}),1000)</script></head><body><div class='header'>MY INVESTMENTS</div>"+cards+"<div class='link'><a href='/invest'>Plans</a> | <a href='/home'>Home</a></div></body>"

@app.route('/transactions')
def transactions():
    if not login_required(): return redirect('/login')
    u=users[session['phone']]
    rows="".join(["<div class='card' style='margin:8px auto;padding:10px'>"+x['date']+" - "+x['type']+" - "+x['plan']+" - UGX "+f"{x['amount']:,}"+"</div>" for x in reversed(u.get("tx",[]))])
    if not rows: rows="<p style='color:#fff;text-align:center'>No transactions</p>"
    return "<head>"+STYLE+"</head><body><div class='header'>TRANSACTIONS</div>"+rows+"<div class='link'><a href='/home'>Home</a></div></body>"

@app.route('/deposit')
def deposit(): return "<head>"+STYLE+"</head><body><div class='card'><h2>Deposit</h2><p>Coming next</p><div class='link'><a href='/home'>Home</a></div></div></body>"
@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
