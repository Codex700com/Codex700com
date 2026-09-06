import pathlib
p = pathlib.Path("admin_panel.py")
t = p.read_text()

# find BASE line
import re
new_base = 'BASE = """<style>body{font-family:system-ui;background:#0f172a;color:#fff;margin:0}.nav{background:#1e293b;padding:12px;display:flex;gap:10px;flex-wrap:wrap}.nav a{color:#94a3b8;text-decoration:none;padding:8px}.wrap{padding:20px;max-width:1000px;margin:auto}.card{background:#1e293b;padding:16px;border-radius:10px;margin:10px 0}</style><div class=nav><a href=/admin>Dashboard</a> <a href=/admin/users>Users</a> <a href=/admin/deposits>Deposits</a> <a href=/admin/withdrawals>Withdrawals</a></div><div class=wrap>{c}</div>"\"\"'

# replace first BASE=... line (single line version from f835e19)
t2 = re.sub(r'BASE=.*', 'BASE = "<div>{c}</div>"', t, count=1)
# Actually insert our styled base
t2 = re.sub(r'BASE = "<div>\{c\}</div>"', new_base, t2)

# The file uses .format or replace? check
if "{c}" in t:
    print("found placeholder")
    p.write_text(t2)
    print("upgraded")
else:
    print("placeholder not found")
