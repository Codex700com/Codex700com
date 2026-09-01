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
            return redirect('/dashboard')
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


@app.route('/dashboard')
def dashboard():
    if 'uid' not in session:
        return redirect('/login')
    name = session.get('name','User').upper()
    return DASH_STYLE + f"""
    <div class="topbar"><div class="menu">☰</div><div class="logo">⬢ CODEX</div><div class="icons">🔔👤</div></div>
    <div class="welcome">
      <div><p>WELCOME BACK,</p><h2>{name}</h2><small>Let's grow your wealth together</small><br><a class="btn-red" href="/invest">Invest Now →</a></div>
    </div>
    <div class="stats">
      <div><small>Wallet Balance</small><b>UGX 0</b></div>
      <div><small>Total Invested</small><b>UGX 0</b></div>
      <div><small>Total Income</small><b>UGX 0</b></div>
      <div><small>Active Plans</small><b>0</b></div>
    </div>
    <div class="checkin"><div>🎁 <b>Daily Check-In Reward</b><br><small>Check in daily and get <span style="color:red">UGX 500</span></small></div><a href="#">Check In →</a></div>
    <div class="grid">
      <a href="/invest">📈<span>Invest</span></a><a href="/deposit">💰<span>Deposit</span></a><a href="/withdraw">🏧<span>Withdraw</span></a><a href="#">👥<span>Referrals</span></a>
      <a href="#">📄<span>Transactions</span></a><a href="#">🎁<span>Raffle</span></a><a href="#">🎧<span>Support</span></a><a href="#">💬<span>Chat Manager</span></a>
    </div>
    <div class="raffle">🏆 <b style="color:red">RAFFLE DRAW</b><br><small>Win amazing prizes daily</small><br><a href="#">View Prizes →</a></div>
    <h3 style="color:red;margin:15px 10px">📈 INVESTMENT PLANS <a href="/invest" style="float:right;font-size:12px;color:red">View All Plans ></a></h3>
    <div class="plans">
      <div class="plan"><b>Starter Plan</b><br><small>Daily Return <span style="color:red">20%</span></small><br><small>Duration 30 Days</small><br><small>Min. Invest <span style="color:red">UGX 50,000</span></small></div>
      <div class="plan"><b>Silver Plan</b><br><small>Daily Return <span style="color:red">20%</span></small><br><small>Duration 30 Days</small><br><small>Min. Invest <span style="color:red">UGX 250,000</span></small></div>
      <div class="plan"><b>Gold Plan</b><br><small>Daily Return <span style="color:red">20%</span></small><br><small>Duration 30 Days</small><br><small>Min. Invest <span style="color:red">UGX 500,000</span></small></div>
    </div>
    <div class="support"><div>🎧 <b>Need Help?</b><br><small>Our support team is always here for you.</small></div><a href="#">Contact Support</a></div>
    <div class="navbar"><a href="/dashboard" class="active">🏠<span>Home</span></a><a href="/invest">📊<span>Invest</span></a><a href="#">⇄<span>Transactions</span></a><a href="#">👥<span>Referrals</span></a><a href="#">👤<span>Account</span></a></div>
    """
DASH_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#000;color:#fff;font-family:Arial;padding-bottom:70px}
.topbar{display:flex;justify-content:space-between;padding:12px;background:#111;color:#ffcc33;font-weight:bold}
.welcome{background:linear-gradient(90deg,#1a0d00,#3a2200);margin:10px;border-radius:12px;padding:20px}
.welcome h2{color:red}
.btn-red{background:#cc0000;color:#fff;padding:8px 15px;border-radius:8px;text-decoration:none;display:inline-block;margin-top:10px}
.stats{display:flex;gap:8px;margin:10px}
.stats div{flex:1;background:#111;border:1px solid #333;border-radius:10px;padding:10px;text-align:center}
.stats b{color:red;font-size:13px}
.stats small{font-size:11px;color:#aaa}
.checkin{display:flex;justify-content:space-between;align-items:center;background:#1a0d00;margin:10px;padding:12px;border-radius:10px}
.checkin a{background:#cc0000;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:10px}
.grid a{background:#111;border:1px solid #333;border-radius:10px;padding:12px 5px;text-align:center;text-decoration:none;color:#ffcc33;font-size:20px}
.grid span{display:block;font-size:11px;color:#fff;margin-top:5px}
.raffle{background:#1a0d00;margin:10px;padding:15px;border-radius:12px;text-align:center}
.raffle a{background:#cc0000;color:#fff;padding:8px 15px;border-radius:8px;text-decoration:none;display:inline-block;margin-top:8px}
.plans{display:flex;gap:8px;overflow-x:auto;padding:10px}
.plan{min-width:150px;background:#111;border:1px solid #333;border-radius:10px;padding:12px;font-size:12px}
.support{display:flex;justify-content:space-between;background:#111;margin:10px;padding:12px;border-radius:10px;align-items:center}
.support a{border:1px solid red;color:red;padding:8px 12px;border-radius:8px;text-decoration:none}
.navbar{position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #333}
.navbar a{color:#aaa;text-decoration:none;font-size:12px;text-align:center}
.navbar a.active{color:red}
.navbar span{display:block}
</style>
"""

@app.route('/deposit', methods=['GET','POST'])
def deposit():
    if 'uid' not in session: return redirect('/login')
    msg=""
    if request.method=='POST':
        msg="Deposit submitted for review. You will be notified once approved."
    return """
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#fff;font-family:Arial;padding-bottom:20px}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px;background:#111}
.top a{color:#ffcc33;text-decoration:none;font-size:20px}
.top b{font-size:16px}
.warn{background:#2a0a0a;border:1px solid #ff3333;margin:10px;padding:10px;border-radius:10px;font-size:12px;color:#ff9999}
.card{margin:10px;background:#111;border:1px solid #333;border-radius:12px;padding:12px}
.card h4{color:#ffcc33;margin-bottom:10px;font-size:13px}
.sendto{display:flex;align-items:center;justify-content:space-between;background:#0a0a0a;border:1px dashed #ffcc33;padding:10px;border-radius:10px}
.sendto .info{flex:1;margin-left:10px}
.sendto b{color:#fff}
.sendto .num{color:#ffcc33;font-size:18px;font-weight:bold;user-select:all}
.copy{background:#222;color:#ffcc33;border:1px solid #ffcc33;padding:6px 10px;border-radius:8px;font-size:12px;cursor:pointer}
ol{margin:10px 0 10px 18px;font-size:13px;line-height:1.6;color:#ddd}
label{font-size:13px;margin:12px 0 5px;display:block}
input{width:100%;padding:12px;border-radius:10px;border:1px solid #444;background:#0a0a0a;color:#fff}
.upload{border:2px dashed #444;border-radius:12px;padding:20px;text-align:center;margin-top:5px;color:#aaa}
.note{background:#2a0a0a;margin:10px;padding:12px;border-radius:10px;font-size:12px;line-height:1.6}
.note b{color:#ff6666}
.btn{margin:10px;width:calc(100% - 20px);padding:15px;background:#cc0000;border:none;border-radius:12px;color:#fff;font-weight:bold;font-size:16px}
.msg{text-align:center;color:#00ff88;margin:10px}
</style>
<div class="top"><a href="/dashboard">←</a><b>Deposit Funds</b><a href="#">🧾</a></div>
<div class="warn">⚠️ <b style="color:red">IMPORTANT:</b> Send money only to the details below. Deposits to other numbers will not be accepted.</div>
<div class="card"><h4>SEND MONEY TO</h4>
<div class="sendto">
<div style="font-size:30px">👤</div>
<div class="info"><b>Shakira Nantongo</b><br><span class="num" id="num">0758878297</span><br><span style="color:red">airtel money</span></div>
<button class="copy" onclick="navigator.clipboard.writeText('0758878297');this.innerText='Copied!'">📋<br>Copy Number</button>
</div></div>
<div class="card"><h4>HOW TO DEPOSIT</h4>
<ol>
<li>Dial *185# on your Airtel line</li>
<li>Select Send Money</li>
<li>Send money to 0758878297</li>
<li>Enter the amount you wish to deposit</li>
<li>After sending, fill in the details below</li>
<li>Upload screenshot of successful transaction</li>
<li>Click "Confirm Deposit"</li>
</ol></div>
<div class="card"><h4>FILL IN YOUR DEPOSIT DETAILS</h4>
<div style="color:#00ff88;text-align:center">"""+msg+"""</div>
<form method="post" enctype="multipart/form-data">
<label>Airtel Number Used To Send</label><input name="sender" placeholder="Enter the Airtel number you used" required>
<label>Amount Deposited (UGX)</label><input name="amount" type="number" placeholder="Enter amount you deposited" required>
<label>Transaction ID / Reference</label><input name="txid" placeholder="Enter transaction ID" required>
<label>Upload Screenshot</label><div class="upload">☁️<br>Tap to upload screenshot<br><small>PNG, JPG, JPEG (Max 5MB)</small><br><input type="file" name="shot" accept="image/*" style="margin-top:10px"></div>
</form></div>
<div class="note"><b>Please Note</b><br>
• Minimum deposit: UGX 1,000<br>
• Maximum deposit: UGX 10,000,000<br>
• Your deposit will be reviewed and approved within a few minutes.<br>
• You will be notified once your deposit is approved.
</div>
<form method="post"><button class="btn">✈️ CONFIRM DEPOSIT</button></form>
<script>document.getElementById('num').onclick=()=>{navigator.clipboard.writeText('0758878297');alert('Number copied')}</script>
"""


@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    if 'uid' not in session: return redirect('/login')
    # TODO: replace 0 with real wallet balance from DB later
    balance = 0
    msg=""
    if request.method=='POST':
        msg="Withdrawal request submitted. Processing within 1-24 hours."
    return f"""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0a0a0a;color:#fff;font-family:Arial;padding-bottom:20px}}
.top{{display:flex;align-items:center;justify-content:space-between;padding:12px}}
.top a{{color:#ffcc33;text-decoration:none;font-size:20px}}
.bal{{margin:10px;border:1px solid #ffcc33;border-radius:12px;padding:15px;display:flex;align-items:center;justify-content:space-between;background:#111}}
.bal b{{color:red;font-size:20px}}
.card{{margin:10px;background:#111;border:1px solid #333;border-radius:12px;padding:12px}}
.card h4{{color:#ffcc33;font-size:13px;margin-bottom:10px}}
label{{font-size:13px;margin:10px 0 5px;display:block}}
input{{width:100%;padding:12px;border-radius:10px;border:1px solid #444;background:#0a0a0a;color:#fff}}
.pay{{display:flex;gap:8px;margin-top:8px}}
.pay div{{flex:1;border:1px solid #444;border-radius:10px;padding:10px;text-align:center;cursor:pointer}}
.pay .sel{{border-color:#ff3300;background:#1a0d00}}
.sum{{margin-top:10px}}
.sum div{{display:flex;justify-content:space-between;padding:6px 0;font-size:14px}}
.sum .recv{{color:red;font-weight:bold}}
.warn{{margin:10px;background:#2a0a0a;border:1px solid #662222;padding:12px;border-radius:10px;font-size:12px;line-height:1.6}}
.warn b{{color:red}}
.btn{{margin:10px;width:calc(100% - 20px);padding:15px;background:#cc0000;border:none;border-radius:12px;color:#fff;font-weight:bold;font-size:16px}}
.minmax{{font-size:12px;margin-top:5px;color:#aaa}}
.minmax span{{color:red}}
</style>
<div class="top"><a href="/dashboard">←</a><b>WITHDRAW</b><a href="#">🎧</a></div>
<div class="bal"><div>💼</div><div><small>Available Balance</small><br><b>UGX {balance:,}</b></div><div>👁️</div></div>
<div class="card"><h4>WITHDRAWAL DETAILS</h4>
<div style="color:#00ff88;text-align:center;font-size:13px">{msg}</div>
<form method="post" id="wf">
<label>Withdrawal Amount (UGX)</label>
<input id="amt" name="amount" type="number" placeholder="Enter amount to withdraw" oninput="upd()" required>
<div style="text-align:right;font-size:12px;color:#aaa;margin-top:-5px">UGX</div>
<div class="minmax">Minimum: <span>UGX 1,000</span> | Maximum: <span>UGX 10,000,000</span></div>
<label>Payment Method</label>
<div class="pay">
<div id="a" class="sel" onclick="setM('airtel')">🔴 Airtel Money ✓</div>
<div id="m" onclick="setM('mtn')">🟡 MTN Mobile Money ○</div>
</div>
<input type="hidden" name="method" id="method" value="airtel">
<label>Mobile Number</label><input name="mobile" placeholder="Enter mobile number (07xxxxxxxx)" required>
<label>Account Name</label><input name="accname" placeholder="Enter account name" required>
<div class="card sum"><h4>WITHDRAWAL SUMMARY</h4>
<div><span>Withdrawal Amount</span><span id="s1">UGX 0</span></div>
<div><span>Withdrawal Fee (9%)</span><span id="fee">UGX 0</span></div>
<div><span>You Will Receive</span><span class="recv" id="s2">UGX 0</span></div>
</div>
<div class="warn">⚠️ <b>IMPORTANT</b><br>
• Make sure your mobile money number is correct.<br>
• Withdrawals are processed within 1-24 hours.<br>
• You will be notified once your withdrawal is approved.
</div>
<button class="btn">✈️ CONFIRM WITHDRAWAL</button>
</form></div>
<script>
function setM(v){{document.getElementById('method').value=v;
document.getElementById('a').className=v=='airtel'?'sel':'';
document.getElementById('m').className=v=='mtn'?'sel':'';}}
function upd(){{let v=document.getElementById('amt').value||0;
let fee=Math.round(v*0.09);
let recv=v-fee;
document.getElementById('s1').innerText='UGX '+Number(v).toLocaleString();
document.getElementById('fee').innerText='UGX '+fee.toLocaleString();
document.getElementById('s2').innerText='UGX '+recv.toLocaleString();}}
</script>
"""

@app.route('/invest')
def invest():
    if 'uid' not in session: return redirect('/login')
    return "<h2 style='color:white;background:black;padding:20px'>Investment Plans coming next</h2><a href='/dashboard'>Back</a>"

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
