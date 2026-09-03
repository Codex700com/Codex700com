import app as A
with A.app.test_client() as c:
    # fake login by setting session directly if you use session
    with c.session_transaction() as s:
        s['uid']=1
    r=c.get('/account')
    print("STATUS", r.status_code)
    data=r.get_data(as_text=True)
    print(data[:2000])
