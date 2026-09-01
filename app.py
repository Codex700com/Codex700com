from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{background:#000;color:#FFD700;font-family:sans-serif;text-align:center;padding:50px;margin:0}
    .card{border:1px solid #FFD700;border-radius:12px;padding:30px;max-width:500px;margin:auto}
    h1{margin:0 0 10px}
    p{color:#fff}
    a{color:#000;background:#FFD700;padding:12px 24px;text-decoration:none;border-radius:8px;font-weight:bold;display:inline-block;margin-top:15px}
    </style></head>
    <body>
        <div class="card">
            <h1>CODEX700</h1>
            <p>New platform live. Black & Gold edition.</p>
            <a href="/about">Enter Platform</a>
        </div>
    </body>
    """

@app.route('/about')
def about():
    return "<body style='background:#000;color:#FFD700;text-align:center;padding:50px;font-family:sans-serif'><h1>Welcome to Codex700</h1><a href='/' style='color:#FFD700'>Back</a></body>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
