@app.route('/account')
def account():
    u=cu()
    if not u:
        import flask
        return flask.redirect('/login')
    d=dict(u)
    wb=d.get('wallet_balance',0) or 0
    mid='CDX'+str(938475+d.get('id',0))
    import flask
    hide=flask.request.args.get('hide','0')=='1'
    hv='******' if hide else 'UGX '+str(int(wb))
    zv='******' if hide else 'UGX 0'
    toggle='0' if hide else '1'
    html=S+hdr()+"<title>My Account</title></head><body>"
    html+='<div style="padding:15px;max-width:500px;margin:auto">'
    html+='<div style="display:flex;align-items:center;gap:10px"><a href="javascript:history.back()" style="font-size:22px">X</a><div class="logo">CODEX</div><a href="/notifications" style="margin-left:auto;font-size:20px">N</a></div>'
    html+='<h2>My Account</h2><p style="color:#aaa">Manage your profile and account settings</p>'
    html+='<a href="/profile"><div class="card" style="text-align:left"><b>'+d.get('name','')+'</b><br><small>Member ID: '+mid+'</small><br><small>'+d.get('email','')+'</small></div></a>'
    html+='<div class="card" style="text-align:left"><div style="display:flex;justify-content:space-between"><b class="gold" style="font-size:12px">WALLET OVERVIEW</b><a href="/account?hide='+toggle+'" style="font-size:12px">Hide Balance</a></div>'
    html+='<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px;text-align:left">'
    html+='<div><div style="color:#aaa;font-size:12px">Wallet Balance</div><div class="red"><b>'+hv+'</b></div></div>'
    html+='<div><div style="color:#aaa;font-size:12px">Total Invested</div><div class="red"><b>'+zv+'</b></div></div>'
    html+='<div><div style="color:#aaa;font-size:12px">Total Income</div><div class="red"><b>'+zv+'</b></div></div>'
    html+='<div><div style="color:#aaa;font-size:12px">Active Investments</div><div class="red"><b>0</b></div></div>'
    html+='</div></div>'
    html+='<div class="card" style="text-align:left"><b class="gold" style="font-size:12px">ACCOUNT MENU</b><br>'
    html+='<a href="/personal-info" class="btn" style="display:block;margin:6px 0;background:#111">Personal Information</a>'
    html+='<a href="/security" class="btn" style="display:block;margin:6px 0;background:#111">Security Settings</a>'
    html+='<a href="/payment" class="btn" style="display:block;margin:6px 0;background:#111">Bank / Payment Details</a>'
    html+='<a href="/kyc" class="btn" style="display:block;margin:6px 0;background:#111">KYC Verification</a>'
    html+='</div>'
    html+='<div class="card" style="text-align:left"><b class="gold" style="font-size:12px">ACCOUNT ACTIONS</b><br>'
    html+='<a href="/statement" class="btn" style="background:#111">Download Statement</a> '
    html+='<a href="/logout" class="btn" style="background:#111">Logout</a></div>'
    html+='</div>'+N+'</body></html>'
    return html

@app.route('/profile')
def profile():
    u=cu(); d=dict(u) if u else {}
    return S+hdr()+'<div class="card">'+d.get('name','')+'<br>'+d.get('email','')+'</div>'+N+'</body></html>'

@app.route('/kyc')
def kyc():
    return S+hdr()+'<div class="card">KYC verification is currently not required.</div>'+N+'</body></html>'

@app.route('/personal-info')
def personal_info():
    u=cu(); d=dict(u) if u else {}
    return S+hdr()+'<div class="card">'+d.get('name','')+'<br>'+d.get('email','')+'</div>'+N+'</body></html>'

@app.route('/security')
def security():
    return S+hdr()+'<div class="card">Change password coming soon</div>'+N+'</body></html>'

@app.route('/payment')
def payment():
    return S+hdr()+'<div class="card">Add payment details</div>'+N+'</body></html>'

@app.route('/statement')
def statement():
    return S+hdr()+'<div class="card">No transactions yet. Balance UGX 0</div>'+N+'</body></html>'

@app.route('/notifications')
def notifications():
    return S+hdr()+'<div class="card">No new notifications</div>'+N+'</body></html>'
