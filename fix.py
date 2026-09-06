open('admin_panel.py','w').write(open('admin_panel.py').read().split('BASE=')[0] + 'BASE="<h1>temp</h1>"\n')
print("truncated bad BASE")
