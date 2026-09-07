import re
with open('app.py','r') as f:
    content=f.read()
open('app_backup.py','w').write(content)
if 'PLANS' not in content:
    content = content.replace('app = Flask(__name__)', 'app = Flask(__name__)\n\nPLANS = {\n    "A1": {"price": 20000, "daily_pct": 20, "days": 7, "total": 140},\n    "A2": {"price": 50000, "daily_pct": 22, "days": 15, "total": 330},\n    "A3": {"price": 100000, "daily_pct": 25, "days": 30, "total": 750},\n    "J1": {"price": 200000, "daily_pct": 18, "days": 30, "total": 540},\n    "J2": {"price": 1000000, "daily_pct": 20, "days": 45, "total": 900},\n    "J3": {"price": 5000000, "daily_pct": 25, "days": 60, "total": 1500},\n}')
if 'import threading' not in content:
    content = content.replace('import sqlite3', 'import sqlite3, threading, time\nfrom datetime import datetime, timedelta')
new_route = '''
@app.route("/invest/<plan_id>")
def invest_plan(plan_id):
    uid = session.get("uid") or session.get("user_id")
    if not uid:
        return redirect("/login")
    plan = PLANS.get(plan_id)
    if not plan:
        price = int(request.args.get("price", 20000))
        daily = int(request.args.get("daily", 20))
        days = int(request.args.get("days", 7))
        plan = {"price": price, "daily_pct": daily, "days": days, "total": daily*days}
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    user=con.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
    if not user:
        con.close()
        return redirect("/login")
    balance=user["balance"]
    if balance < plan["price"]:
        con.close()
        return render_template("invest_fail.html", plan_name=plan_id, amount=plan["price"], daily_pct=plan["daily_pct"], duration_days=plan["days"], total_return=plan["daily_pct"]*plan["days"], current_balance=balance)
    else:
        new_bal=balance-plan["price"]
        con.execute("UPDATE users SET balance=? WHERE id=?",(new_bal, uid))
        start=datetime.utcnow()
        end=start+timedelta(days=plan["days"])
        con.execute("CREATE TABLE IF NOT EXISTS investments (id INTEGER PRIMARY KEY, user_id INT, plan_name TEXT, amount INT, daily_pct INT, duration_days INT, start_time TEXT, end_time TEXT, last_credit TEXT, status TEXT DEFAULT 'active')")
        con.execute("INSERT INTO investments (user_id, plan_name, amount, daily_pct, duration_days, start_time, end_time, last_credit, status) VALUES (?,?,?,?,?,?,?,?,?)",(uid, plan_id, plan["price"], plan["daily_pct"], plan["days"], start.isoformat(), end.isoformat(), start.isoformat(), 'active'))
        con.commit()
        con.close()
        return render_template("invest_success.html", plan_name=plan_id, amount=plan["price"], daily_pct=plan["daily_pct"], duration_days=plan["days"], total_return=plan["daily_pct"]*plan["days"])

@app.route("/my-investments")
def my_investments_page():
    uid = session.get("uid") or session.get("user_id")
    if not uid:
        return redirect("/login")
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS investments (id INTEGER PRIMARY KEY, user_id INT, plan_name TEXT, amount INT, daily_pct INT, duration_days INT, start_time TEXT, end_time TEXT, last_credit TEXT, status TEXT DEFAULT 'active')")
    invs=con.execute("SELECT * FROM investments WHERE user_id=? ORDER BY id DESC",(uid,)).fetchall()
    con.close()
    return render_template("my_investments.html", investments=invs)

def robot_monitor():
    while True:
        try:
            con=sqlite3.connect("codex700.db")
            con.row_factory=sqlite3.Row
            now=datetime.utcnow()
            invs=con.execute("SELECT * FROM investments WHERE status='active'").fetchall()
            for inv in invs:
                try:
                    last=datetime.fromisoformat(inv["last_credit"])
                    end=datetime.fromisoformat(inv["end_time"])
                except:
                    continue
                if now >= last + timedelta(hours=24):
                    if now < end:
                        income=inv["amount"]*inv["daily_pct"]//100
                        con.execute("UPDATE users SET balance=balance+? WHERE id=?",(income, inv["user_id"]))
                        con.execute("UPDATE investments SET last_credit=? WHERE id=?",(now.isoformat(), inv["id"]))
                        con.commit()
                        print(f"Robot credited {income} to {inv['user_id']}")
                    else:
                        con.execute("UPDATE investments SET status='completed' WHERE id=?",(inv["id"],))
                        con.commit()
            con.close()
            time.sleep(3600)
        except Exception as e:
            print(f"Robot error: {e}")
            time.sleep(60)

if not hasattr(app, 'robot_started'):
    t=threading.Thread(target=robot_monitor, daemon=True)
    t.start()
    app.robot_started=True
'''
content = re.sub(r'def invest_plan.*?(?=@app\.route|if __name__)', '', content, flags=re.DOTALL)
content = re.sub(r'def my_investments.*?(?=@app\.route|if __name__)', '', content, flags=re.DOTALL)
if 'def robot_monitor' not in content:
    content = content.replace('if __name__', new_route + '\nif __name__')
with open('app.py','w') as f:
    f.write(content)
print("✅ Patched!")
