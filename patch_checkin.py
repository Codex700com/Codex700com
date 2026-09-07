with open('app.py','r') as f:
    c=f.read()

# add checkin route
checkin_code = '''
@app.route("/daily-checkin")
def daily_checkin_page():
    return render_template("daily_checkin.html")

@app.route("/api/daily-checkin", methods=["POST"])
def api_daily_checkin():
    uid = session.get("uid") or session.get("user_id")
    if not uid:
        return jsonify({"ok": False, "msg": "Login first"})
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkins (user_id INTEGER PRIMARY KEY, last_claim TEXT, streak INTEGER DEFAULT 0)")
    row=con.execute("SELECT * FROM daily_checkins WHERE user_id=?",(uid,)).fetchone()
    now=datetime.utcnow()
    today=now.date().isoformat()
    if row:
        last_date=row["last_claim"][:10] if row["last_claim"] else ""
        if last_date==today:
            # already claimed today - calculate time left till tomorrow UTC
            tomorrow = datetime.combine(now.date()+timedelta(days=1), datetime.min.time())
            diff = tomorrow - now
            con.close()
            return jsonify({"ok": False, "msg": "Already claimed today", "next_in": int(diff.total_seconds()), "streak": row["streak"]})
        else:
            # check streak
            yesterday = (now.date()-timedelta(days=1)).isoformat()
            new_streak = row["streak"]+1 if last_date==yesterday else 1
            reward = 500 * new_streak  # 500 UGX per streak, change as you want
            con.execute("UPDATE daily_checkins SET last_claim=?, streak=? WHERE user_id=?",(now.isoformat(), new_streak, uid))
            con.execute("UPDATE users SET balance=balance+? WHERE id=?",(reward, uid))
            con.commit()
            con.close()
            return jsonify({"ok": True, "msg": f"Checked in! +{reward} UGX", "streak": new_streak, "reward": reward})
    else:
        con.execute("INSERT INTO daily_checkins (user_id, last_claim, streak) VALUES (?,?,?)",(uid, now.isoformat(), 1))
        con.execute("UPDATE users SET balance=balance+? WHERE id=?",(500, uid))
        con.commit()
        con.close()
        return jsonify({"ok": True, "msg": "First check-in! +500 UGX", "streak": 1, "reward": 500})

@app.route("/api/daily-status")
def api_daily_status():
    uid = session.get("uid") or session.get("user_id")
    if not uid:
        return jsonify({"claimed": False})
    con=sqlite3.connect("codex700.db")
    con.row_factory=sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS daily_checkins (user_id INTEGER PRIMARY KEY, last_claim TEXT, streak INTEGER DEFAULT 0)")
    row=con.execute("SELECT * FROM daily_checkins WHERE user_id=?",(uid,)).fetchone()
    con.close()
    now=datetime.utcnow()
    if not row:
        return jsonify({"claimed": False, "streak": 0})
    today=now.date().isoformat()
    last_date=row["last_claim"][:10]
    if last_date==today:
        tomorrow = datetime.combine(now.date()+timedelta(days=1), datetime.min.time())
        diff = tomorrow - now
        return jsonify({"claimed": True, "next_in": int(diff.total_seconds()), "streak": row["streak"]})
    else:
        return jsonify({"claimed": False, "streak": row["streak"]})
'''

# insert before robot
if '/api/daily-checkin' not in c:
    c = c.replace('def robot_monitor():', checkin_code + '\n\ndef robot_monitor():')

with open('app.py','w') as f:
    f.write(c)
print("✅ Check-in patched")
