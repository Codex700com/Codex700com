from flask import Flask, request, redirect, url_for, session
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash


# --- CHAT WITH MANAGER ---
import sqlite3, time
def chat_db():
    c = sqlite3.connect('codex700.db')
    c.execute('''CREATE TABLE IF NOT EXISTS chats
    (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, sender TEXT, msg TEXT, ts TEXT)''')
    return c

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
      <a href="#">📄<span>Transactions</span></a><a href="/raffle">🎁<span>Raffle</span></a><a href="#">🎧<span>Support</span></a><a href="#">💬<span>Chat Manager</span></a>
    </div>
    <div class="raffle">🏆 <b style="color:red">RAFFLE DRAW</b><br><small>Win amazing prizes daily</small><br><a href="/raffle#prizes">View Prizes →</a></div>
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


@app.route('/raffle')
def raffle():
    if 'uid' not in session: return redirect('/login')
    return """
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#000;color:#fff;font-family:Arial;padding-bottom:70px}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px}
.top a{color:#ffcc33;text-decoration:none;font-size:20px}
.top b{color:red;font-size:18px}
.banner{margin:10px;background:linear-gradient(90deg,#1a0d00,#3a2500);border:1px solid #664400;border-radius:12px;padding:15px;display:flex;gap:10px;align-items:center}
.banner h3{color:#ffaa00}
.btn-red{background:#cc0000;color:#fff;padding:8px 14px;border-radius:8px;text-decoration:none;display:inline-block;margin-top:8px;font-size:13px}
.info-bar{display:flex;justify-content:space-between;align-items:center;margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.info-bar b{color:red;font-size:20px}
.buy{border:1px solid red;color:#ffcc99;padding:8px 12px;border-radius:8px;text-decoration:none;background:#1a0000}
.prize-list{margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.prize-list h4{color:#ffaa00;margin-bottom:10px}
.prow{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #222;font-size:13px}
.winners{margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.wlist{display:flex;gap:8px;overflow-x:auto;margin-top:10px}
.wcard{min-width:130px;background:#111;border:1px solid #333;border-radius:10px;padding:10px;text-align:center;font-size:11px}
.wcard .av{width:50px;height:50px;border-radius:50%;background:#444;margin:0 auto 5px;display:flex;align-items:center;justify-content:center;font-size:24px}
.navbar{position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #333}
.navbar a{color:#ffcc33;text-decoration:none;font-size:11px;text-align:center}
</style>
<div class="top"><a href="/dashboard">←</a><b>RAFFLE DRAW</b><div>🔔👤</div></div>
<div class="banner"><div style="font-size:50px">🏆</div><div><h3>WIN AMAZING PRIZES</h3><small>Every ticket gives you a chance<br>to be a winner!</small><br><a class="btn-red" href="#prizes">View Prizes 🎁</a></div></div>
<div class="info-bar">
<div>🎟️<br><small>Your Tickets</small><br><b>0</b></div>
<div style="text-align:center">📅<br><small>Next Draw</small><br><b style="font-size:14px" id="drawdate">30 Sep 2026</b><br><small style="color:red" id="timer">00d : 00h : 00m : 00s</small></div>
<a class="buy" href="/raffle/buy">Buy Tickets 🛒</a>
</div>
<div style="margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px"><h4 style="color:#ffaa00;text-align:center">HOW IT WORKS</h4><p style="font-size:12px;text-align:center">1 Buy Tickets → 2 Wait for Draw → 3 Win Prizes</p></div>
<div class="prize-list" id="prizes"><h4>🎁 VIEW PRIZES - Grand Draw 30 Sep 2026</h4>
<div class="prow"><span>🚗 Toyota Corolla 2022</span><span style="color:red">Grand</span></div>
<div class="prow"><span>🚗 Suzuki Swift 2023</span><span style="color:red">2nd</span></div>
<div class="prow"><span>🏍️ Yamaha YBR 125</span><span style="color:red">3rd</span></div>
<div class="prow"><span>🏍️ Bajaj Boxer 150</span><span style="color:red">4th</span></div>
<div class="prow"><span>🚲 Mountain Bicycle</span><span>5th</span></div>
<div class="prow"><span>📱 iPhone 15 Pro Max 256GB</span><span>6th</span></div>
<div class="prow"><span>📱 Samsung S24 Ultra</span><span>7th</span></div>
<div class="prow"><span>📱 Samsung A55</span><span>8th</span></div>
<div class="prow"><span>💻 MacBook Air M2</span><span>9th</span></div>
<div class="prow"><span>💻 HP Pavilion 15 Laptop</span><span>10th</span></div>
<div style="margin-top:10px;font-size:12px">Total Tickets: <b style="color:red">10,000</b> | Ticket Price: <b style="color:red">UGX 5,000</b> | Draw Date: <b style="color:red">30 Sep 2026, 12:00 EAT Uganda</b></div>
<div style="text-align:center;margin-top:10px"><a class="btn-red" href="/raffle/buy">Buy Tickets Now</a></div>
</div>
<div class="winners"><h4 style="color:#ffaa00">PREVIOUS WINNERS</h4><div class="wlist">
<div class="wcard"><div class="av">👨🏾</div>Brian M.<br>Won Toyota Wish<br><b>28 Aug 2026</b><br><b>Draw #128</b></div>
<div class="wcard"><div class="av">👩🏾</div>Aisha K.<br>Won iPhone 14<br><b>25 Aug 2026</b><br><b>Draw #127</b></div>
<div class="wcard"><div class="av">👨🏾</div>Peter O.<br>Won Yamaha MT15<br><b>20 Aug 2026</b><br><b>Draw #126</b></div>
<div class="wcard"><div class="av">👩🏾</div>Grace A.<br>Won Samsung S23<br><b>15 Aug 2026</b><br><b>Draw #125</b></div>
<div class="wcard"><div class="av">👨🏾</div>John K.<br>Won UGX 500,000<br><b>10 Aug 2026</b><br><b>Draw #124</b></div>
<div class="wcard"><div class="av">👩🏾</div>Sarah N.<br>Won MacBook Pro<br><b>05 Aug 2026</b><br><b>Draw #123</b></div>
<div class="wcard"><div class="av">👨🏾</div>David M.<br>Won Bicycle<br><b>02 Sep 2026</b><br><b>Draw #129</b></div>
<div class="wcard"><div class="av">👩🏾</div>Faith T.<br>Won HP Laptop<br><b>01 Sep 2026</b><br><b>Draw #130</b></div>
</div></div>
<div class="navbar"><a href="/dashboard">🏠<br>Home</a><a href="/invest">📈<br>Invest</a><a href="#">⇄<br>Transactions</a><a href="#">👥<br>Referrals</a><a href="#">👤<br>Account</a></div>
<script>
// Next draw: 30 Sep 2026 12:00 Uganda time (EAT = UTC+3)
var draw = new Date('2026-09-30T12:00:00+03:00').getTime();
function tick(){
  var now = new Date().getTime();
  var d = draw - now;
  if(d<0) d=0;
  var days=Math.floor(d/86400000);
  var h=Math.floor(d%86400000/3600000);
  var m=Math.floor(d%3600000/60000);
  var s=Math.floor(d%60000/1000);
  document.getElementById('timer').innerHTML = days+'d : '+h+'h : '+m+'m : '+s+'s';
}
setInterval(tick,1000); tick();
</script>
"""
"""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#000;color:#fff;font-family:Arial;padding-bottom:70px}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px}
.top a{color:#ffcc33;text-decoration:none;font-size:20px}
.top b{color:red;font-size:18px}
.banner{margin:10px;background:linear-gradient(90deg,#1a0d00,#3a2500);border:1px solid #664400;border-radius:12px;padding:15px;display:flex;gap:10px;align-items:center}
.banner h3{color:#ffaa00}
.btn-red{background:#cc0000;color:#fff;padding:8px 14px;border-radius:8px;text-decoration:none;display:inline-block;margin-top:8px;font-size:13px}
.info-bar{display:flex;justify-content:space-between;align-items:center;margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.info-bar b{color:red;font-size:20px}
.info-bar small{color:#aaa}
.buy{border:1px solid red;color:#ffcc99;padding:8px 12px;border-radius:8px;text-decoration:none;background:#1a0000}
.how{margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.how h4{text-align:center;color:#ffaa00;margin-bottom:10px}
.steps{display:flex;gap:8px;align-items:center}
.step{flex:1;background:#111;border:1px solid #444;border-radius:10px;padding:10px;text-align:center;font-size:11px}
.step div{width:24px;height:24px;background:#ffaa00;color:#000;border-radius:50%;margin:0 auto 5px;font-weight:bold;line-height:24px}
.upcoming{margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.upcoming h4{color:#ffaa00;margin-bottom:10px}
.prize{display:flex;gap:10px}
.prize-img{width:110px;height:110px;background:radial-gradient(#332200,#000);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:50px}
.badge{background:red;color:#fff;font-size:10px;padding:3px 8px;border-radius:5px}
.meta{display:flex;gap:10px;margin-top:10px;font-size:11px}
.meta b{color:red;display:block}
.bar{height:8px;background:#333;border-radius:5px;margin-top:10px}
.bar div{height:8px;background:red;border-radius:5px;width:72%}
.winners{margin:10px;background:#0f0f0f;border:1px solid #333;border-radius:12px;padding:12px}
.winners h4{color:#ffaa00;display:flex;justify-content:space-between}
.winners h4 a{color:red;font-size:12px;text-decoration:none}
.wlist{display:flex;gap:8px;overflow-x:auto;margin-top:10px}
.wcard{min-width:110px;background:#111;border:1px solid #333;border-radius:10px;padding:10px;text-align:center;font-size:11px}
.wcard .av{width:50px;height:50px;border-radius:50%;background:#444;margin:0 auto 5px;display:flex;align-items:center;justify-content:center;font-size:24px}
.wcard b{color:red;font-size:10px}
.navbar{position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #333}
.navbar a{color:#ffcc33;text-decoration:none;font-size:11px;text-align:center}
.navbar span{display:block}
</style>
<div class="top"><a href="/dashboard">←</a><b>RAFFLE DRAW</b><div>🔔👤</div></div>

<div class="banner">
<div style="font-size:50px">🏆</div>
<div><h3>WIN AMAZING PRIZES</h3><small>Every ticket gives you a chance<br>to be a winner!</small><br><a class="btn-red" href="#prizes">View Prizes 🎁</a></div>
</div>

<div class="info-bar">
<div>🎟️<br><small>Your Tickets</small><br><b>12</b></div>
<div>📅<br><small>Next Draw</small><br><b style="font-size:14px">29 May 2025</b><br><small style="color:red">02d : 14h : 35m : 20s</small></div>
<a class="buy" href="/raffle/buy">Buy Tickets 🛒</a>
</div>

<div class="how"><h4>HOW IT WORKS</h4>
<div class="steps">
<div class="step"><div>1</div>🎟️<br><b>Buy Tickets</b><br>Choose the number of tickets you want to enter.</div><div>→</div>
<div class="step"><div>2</div>🎁<br><b>Wait for Draw</b><br>Stay tuned and wait for the draw date.</div><div>→</div>
<div class="step"><div>3</div>🏆<br><b>Win Prizes</b><br>Winners will be announced and prizes delivered.</div>
</div></div>

<div class="upcoming" id="prizes"><h4>UPCOMING RAFFLE</h4>
<div class="prize">
<div class="prize-img">📱</div>
<div><span class="badge">GRAND PRIZE</span><br><b style="color:#ffaa00">iPhone 15 Pro Max (256GB)</b><br><small>Be the next lucky winner!</small>
<div class="meta"><div>🎟️ Total Tickets<br><b>10,000</b></div><div>🎫 Ticket Price<br><b>UGX 5,000</b></div><div>📅 Draw Date<br><b>29 May 2025</b></div></div>
</div></div>
<div class="bar"><div></div></div>
<div style="display:flex;justify-content:space-between;font-size:12px;margin-top:5px"><span><span style="color:red">7,250</span> / 10,000 Tickets Sold</span><span style="color:red">72%</span></div>
<div style="text-align:center;margin-top:10px"><a class="btn-red" href="/raffle/buy">Buy Tickets Now</a></div>
</div>

<div class="winners"><h4>PREVIOUS WINNERS <a href="/raffle/winners">View All Winners ></a></h4>
<div class="wlist">
<a href="/raffle/winners" style="text-decoration:none;color:#fff"><div class="wcard"><div class="av">👨🏾</div>John K.<br><br>Won UGX 500,000<br><b>Draw #124</b></div></a>
<a href="/raffle/winners" style="text-decoration:none;color:#fff"><div class="wcard"><div class="av">👩🏾</div>Sarah N.<br><br>Won Samsung S24<br><b>Draw #123</b></div></a>
<a href="/raffle/winners" style="text-decoration:none;color:#fff"><div class="wcard"><div class="av">👨🏾</div>David M.<br><br>Won UGX 250,000<br><b>Draw #122</b></div></a>
<a href="/raffle/winners" style="text-decoration:none;color:#fff"><div class="wcard"><div class="av">👩🏾</div>Grace A.<br><br>Won AirPods Pro<br><b>Draw #121</b></div></a>
</div></div>

<div class="navbar">
<a href="/dashboard">🏠<span>Home</span></a>
<a href="/invest">📈<span>Invest</span></a>
<a href="#">⇄<span>Transactions</span></a>
<a href="#">👥<span>Referrals</span></a>
<a href="#">👤<span>Account</span></a>
</div>
"""
@app.route('/raffle/buy')
def raffle_buy():
    if 'uid' not in session: return redirect('/login')
    return '<div style="background:#000;color:#fff;padding:20px;font-family:Arial"><a href="/raffle" style="color:#ffcc33">← Back</a><h2>Buy Tickets</h2><p>Ticket: UGX 5,000</p><a href="/deposit" style="background:red;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none">Deposit to Buy</a></div>'
@app.route('/raffle/winners')
def raffle_winners():
    if 'uid' not in session: return redirect('/login')
    return '<div style="background:#000;color:#fff;padding:20px;font-family:Arial"><a href="/raffle" style="color:#ffcc33">← Back</a><h2>All Winners</h2><p>John K. - Draw #124<br>Sarah N. - Draw #123<br>David M. - Draw #122<br>Grace A. - Draw #121</p></div>'

@app.route('/invest')
def invest():
    if 'uid' not in session:
        return redirect('/login')
    return '''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
*{box-sizing:border-box;margin:0}body{background:#000;color:#fff;font-family:Arial;max-width:480px;margin:auto}
.header{background:#0a0a0a;padding:12px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #222}
.header .logo{width:36px;height:36px;border:1px solid gold;border-radius:50%;display:flex;align-items:center;justify-content:center}
.header h2{color:#ff0000;font-size:18px}.header small{color:#ff0000;font-size:12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:8px}
.card{background:#0f0f0f;border:1px solid #8a6d00;border-radius:12px;overflow:hidden}
.img{height:90px;background:radial-gradient(circle at 50% 30%, #ffdf6b, #8a6d00 70%);font-size:40px;display:flex;align-items:center;justify-content:center;position:relative}
.hot{position:absolute;top:6px;left:6px;background:red;color:#fff;font-size:10px;padding:3px 8px;border-radius:12px}
.heart{position:absolute;top:6px;right:6px;color:#ff5555;border:1px solid #ff5555;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:14px}
.body{padding:8px}.title{color:#ff0000;font-weight:bold;font-size:14px;margin:4px 0}
.row{display:flex;justify-content:space-between;margin:6px 0}.row small{color:#a00;font-size:9px}.row b{color:#ff0000;font-size:12px}
.total{background:#1a0f00;text-align:center;padding:6px;border-radius:8px;margin:6px 0}.total small{color:#a00;font-size:9px}.total b{color:#ff0000;font-size:15px}
.btnrow{display:flex;gap:6px}.invest{flex:1;background:linear-gradient(to bottom,#ff2222,#aa0000);color:#fff;text-align:center;padding:9px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:13px}
.arrow{background:#5a0000;color:#ff8888;width:36px;display:flex;align-items:center;justify-content:center;border-radius:10px;text-decoration:none}
.nav{position:sticky;bottom:0;background:#0a0a0a;display:flex;justify-content:space-around;padding:8px 0;border-top:1px solid #222;font-size:10px}
.nav a{color:#888;text-decoration:none;text-align:center}.nav a.active{color:#ff0000}
</style></head><body>
<div class="header"><div class="logo">📈</div><div><h2>INVESTMENT PLANS</h2><small>Choose a plan that suits you</small></div></div>
<div class="grid">
<div class="card">
<div class="img">🌱<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Starter Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 50,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 20,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 600,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 600,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">🪙<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Bronze Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 100,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 50,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 1,500,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 1,500,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">🥇<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Silver Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 250,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 100,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 3,000,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 3,000,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">💰<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Gold Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 500,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 100,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 3,000,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 3,000,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">🏆<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Platinum Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 1,000,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 200,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 6,000,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 7,000,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">💎<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Diamond Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 2,000,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 400,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 12,000,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 14,000,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">👑<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">VIP Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 5,000,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 1,000,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 30,000,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 35,000,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div>
<div class="card">
<div class="img">🏦<span class="hot">🔥 HOT</span><span class="heart">♡</span></div>
<div class="body">
<div class="title">Exclusive Plan <span>🔒</span></div>
<div class="row"><div><small>PRICE</small><br><b>UGX 10,000,000</b></div><div><small>DURATION</small><br><b>30 Days</b></div></div>
<div class="row"><div><small>DAILY RETURN (20%)</small><br><b>UGX 2,000,000</b></div><div><small>TOTAL RETURN</small><br><b>UGX 60,000,000</b></div></div>
<div class="total"><small>TOTAL RECEIVED</small><br><b>UGX 70,000,000</b></div>
<div class="btnrow"><a class="invest" href="#">🛒 Invest Now</a><a class="arrow" href="#">→</a></div>
</div></div></div>
<div class="nav"><a href="/dashboard">🏠<br>Home</a><a href="/invest" class="active">📊<br>Invest</a><a href="#">💱<br>Transactions</a><a href="#">👥<br>Referrals</a><a href="#">🎧<br>Support</a><a href="#">👤<br>Account</a></div>
</body></html>'''

@app.route('/support')
def support():
    if 'uid' not in session: return redirect('/login')
    uid = session['uid']
    c = chat_db(); cur = c.cursor()
    cur.execute("SELECT sender,msg,ts FROM chats WHERE uid=? ORDER BY id DESC LIMIT 20", (uid,))
    msgs = cur.fetchall()[::-1]
    c.close()
    msgs_html = "".join([f"<div style='margin:6px;padding:8px;border-radius:8px;background:{'#1a1a1a' if m[0]=='user' else '#3a0000'};text-align:{'right' if m[0]=='user' else 'left'}'><small>{m[0]}</small><br>{m[1]}<br><small style='color:#888'>{m[2]}</small></div>" for m in msgs])
    return '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>*{box-sizing:border-box}body{background:#000;color:#fff;font-family:Arial;max-width:480px;margin:auto}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px}.box{border:1px solid #8a6d00;border-radius:12px;padding:12px;margin:10px;display:flex;gap:12px;align-items:center}
.btn{background:linear-gradient(#ff2222,#aa0000);color:#fff;border:none;padding:10px 16px;border-radius:10px;font-weight:bold}
.conv{margin:10px}.chead{color:gold;font-size:12px;margin:10px}
#msgs{padding:10px;min-height:200px}
.send{display:flex;gap:6px;padding:10px;position:sticky;bottom:0;background:#000}input{flex:1;padding:10px;border-radius:10px;border:1px solid #444;background:#111;color:#fff}
</style></head><body>
<div class="top"><a href="/dashboard" style="color:gold;text-decoration:none">←</a><h3>Chat with Manager</h3><span>🎧</span></div>
<div class="box"><div style="width:60px;height:60px;border:1px solid gold;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px">💬</div>
<div>Our managers are here<br>to assist you 24/7.<br><br><button class="btn" onclick="document.getElementById('inp').focus()">+ New Conversation</button></div></div>
<div class="chead">MY CONVERSATIONS</div><div id="msgs">'''+msgs_html+'''</div>
<form class="send" method="POST" action="/support/send"><input id="inp" name="msg" placeholder="Type a message..." required><button class="btn">Send</button></form>
</body></html>'''

@app.route('/support/send', methods=['POST'])
def support_send():
    if 'uid' not in session: return redirect('/login')
    msg = request.form.get('msg','')[:500]
    if msg:
        c = chat_db(); c.execute("INSERT INTO chats (uid,sender,msg,ts) VALUES (?,?,?,?)",
        (session['uid'],'user',msg,time.strftime("%H:%M")))
        c.commit(); c.close()
    return redirect('/support')

@app.route('/admin/chats')
def admin_chats():
    # simple protect - change password check as you have
    c = chat_db(); cur=c.cursor()
    cur.execute("SELECT DISTINCT uid FROM chats ORDER BY id DESC")
    users = [r[0] for r in cur.fetchall()]; c.close()
    h="".join([f"<div style='padding:12px;border-bottom:1px solid #222'><a href='/admin/chat/{u}' style='color:gold;text-decoration:none'>{u}</a></div>" for u in users])
    return f"<body style='background:#000;color:#fff;font-family:Arial'><h3 style='color:gold;padding:12px'>Admin - User Chats</h3>{h}</body>"

@app.route('/admin/chat/<uid>')
def admin_chat(uid):
    c = chat_db(); cur=c.cursor()
    cur.execute("SELECT sender,msg,ts FROM chats WHERE uid=? ORDER BY id", (uid,))
    msgs = cur.fetchall(); c.close()
    mh="".join([f"<div style='margin:6px;padding:8px;background:#111;border-radius:8px'><b>{m[0]}:</b> {m[1]} <small style='color:#888'>{m[2]}</small></div>" for m in msgs])
    return f'''<body style="background:#000;color:#fff;font-family:Arial;max-width:600px;margin:auto">
    <a href="/admin/chats" style="color:gold">← Back</a><h3>Chat with {uid}</h3>{mh}
    <form method="POST" action="/admin/reply/{uid}" style="display:flex;gap:6px;margin-top:10px">
    <input name="msg" placeholder="Reply privately..." required style="flex:1;padding:10px;background:#111;color:#fff;border:1px solid #444;border-radius:8px">
    <button style="background:red;color:#fff;padding:10px;border:none;border-radius:8px">Reply</button></form></body>'''

@app.route('/admin/reply/<uid>', methods=['POST'])
def admin_reply(uid):
    msg = request.form.get('msg','')[:500]
    if msg:
        c = chat_db(); c.execute("INSERT INTO chats (uid,sender,msg,ts) VALUES (?,?,?,?)",
        (uid,'admin',msg,time.strftime("%H:%M")))
        c.commit(); c.close()
    return redirect(f'/admin/chat/{uid}')
# --- END CHAT ---

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
