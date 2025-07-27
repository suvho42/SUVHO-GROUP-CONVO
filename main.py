from flask import Flask, request, render_template_string, redirect, session
import threading
import requests
import time
import os
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "henry_secret_key"
ADMIN_PASSWORD = "1997"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('bot_manager.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bots (
            thread_key TEXT PRIMARY KEY,
            thread_id TEXT,
            token TEXT,
            prefix TEXT,
            bot_name TEXT,
            start_time TEXT,
            status TEXT,
            message_count INTEGER,
            last_message TEXT,
            session_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
active_threads = {}

def get_db():
    conn = sqlite3.connect('bot_manager.db')
    conn.row_factory = sqlite3.Row
    return conn

def message_sender(token, thread_id, prefix, delay, messages, thread_key, bot_name, session_id):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'referer': 'https://www.facebook.com/',
        'Origin': 'https://www.facebook.com'
    }

    conn = get_db()
    conn.execute('INSERT OR REPLACE INTO bots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
        thread_key, thread_id, token, prefix, bot_name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'running', 0, '', session_id
    ))
    conn.commit()
    conn.close()

    while active_threads.get(thread_key, False):
        for msg in messages:
            if not active_threads.get(thread_key, False):
                break
            try:
                full_message = f"{prefix} {msg}"
                url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                payload = {
                    'access_token': token,
                    'message': full_message,
                    'client': 'mercury'
                }
                requests.post(url, data=payload, headers=headers, timeout=30)

                conn = get_db()
                conn.execute('UPDATE bots SET message_count = message_count + 1, last_message = ? WHERE thread_key = ?',
                             (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), thread_key))
                conn.commit()
                conn.close()

                time.sleep(delay)
            except:
                time.sleep(30)

    conn = get_db()
    conn.execute('UPDATE bots SET status = "stopped" WHERE thread_key = ?', (thread_key,))
    conn.commit()
    conn.close()
    active_threads.pop(thread_key, None)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mode = request.form.get('mode')
        thread_id = request.form.get('threadId')
        prefix = request.form.get('kidx')
        bot_name = request.form.get('botName') or 'NightBot'
        delay = max(1, int(request.form.get('time')))
        session_id = session.get('sid') or str(random.randint(100000, 999999))
        session['sid'] = session_id
        messages = [m.strip() for m in request.files['txtFile'].read().decode().splitlines() if m.strip()]

        if mode == 'single':
            token = request.form.get('accessToken').strip()
            thread_key = f"{thread_id}_{random.randint(1000, 9999)}"
            active_threads[thread_key] = True
            threading.Thread(target=message_sender, args=(token, thread_id, prefix, delay, messages, thread_key, bot_name, session_id), daemon=True).start()

        elif mode == 'multi':
            tokens = request.files['tokenFile'].read().decode().splitlines()
            for token in tokens:
                thread_key = f"{thread_id}_{random.randint(1000, 9999)}"
                active_threads[thread_key] = True
                threading.Thread(target=message_sender, args=(token.strip(), thread_id, prefix, delay, messages, thread_key, bot_name, session_id), daemon=True).start()

        return redirect('/status')

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SERVER-2.0</title>
            <style>
                :root {
                    --bg: #708090;
                    --card: #111111;
                    --accent: #FF69B4;
                    --text: #f0f0f0;
                    --text-dim: #000000;
                    --danger: #ff3366;
                }
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }
                body {
                    background: var(--bg);
                    color: var(--text);
                    min-height: 100vh;
                    padding: 20px;
                    line-height: 1.6;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: #708090;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 0 20px rgba(127, 0, 255, 0.1);
                    border: 1px solid rgba(255,255,255,0.05);
                }
                h1 {
                    text-align: center;
                    margin-bottom: 25px;
                    color: var(--accent);
                    font-size: 28px;
                    letter-spacing: 1px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 8px;
                    color: var(--text-dim);
                    font-size: 14px;
                }
                input[type="text"],
                input[type="number"],
                input[type="password"],
                input[type="file"] {
                    width: 100%;
                    padding: 12px 15px;
                    background: rgba(0,0,0,0.3);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 6px;
                    color: var(--text);
                    font-size: 15px;
                    transition: all 0.3s;
                }
                input:focus {
                    outline: none;
                    border-color: var(--accent);
                    box-shadow: 0 0 0 3px rgba(127, 0, 255, 0.2);
                }
                .radio-group {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .radio-group label {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    cursor: pointer;
                }
                input[type="radio"] {
                    accent-color: var(--accent);
                }
                button {
                    width: 100%;
                    padding: 14px;
                    background: var(--accent);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s;
                    margin-top: 10px;
                    letter-spacing: 0.5px;
                }
                button:hover {
                    background: #6a00d4;
                    transform: translateY(-2px);
                }
                .file-input {
                    display: none;
                }
                .file-label {
                    display: block;
                    padding: 12px;
                    background: rgba(0,0,0,0.3);
                    border: 1px dashed rgba(255,255,255,0.2);
                    border-radius: 6px;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s;
                    margin-bottom: 15px;
                }
                .file-label:hover {
                    border-color: var(--accent);
                    background: rgba(127, 0, 255, 0.1);
                }
                .nav-links {
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    margin-top: 25px;
                }
                .nav-links a {
                    color: var(--text-dim);
                    text-decoration: none;
                    font-size: 14px;
                    transition: all 0.3s;
                    padding: 8px 12px;
                    border-radius: 4px;
                }
                .nav-links a:hover {
                    color: var(--accent);
                    background: rgba(127, 0, 255, 0.1);
                }
                .glow {
                    animation: glow 2s infinite alternate;
                }
                @keyframes glow {
                    from {
                        text-shadow: 0 0 5px rgba(127, 0, 255, 0.5);
                    }
                    to {
                        text-shadow: 0 0 10px rgba(127, 0, 255, 0.8);
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="glow">Server 2.0</h1>
                <form method="POST" enctype="multipart/form-data">
                    <div class="radio-group">
                        <label><input type="radio" name="mode" value="single" checked> Single Token</label>
                        <label><input type="radio" name="mode" value="multi"> Multi Token</label>
                    </div>
                    
                    <div class="form-group">
                        <label>ACCESS TOKEN</label>
                        <input type="text" name="accessToken" placeholder="Enter Facebook Token" required>
                    </div>
                    
                    <div class="form-group">
                        <label>TOKEN FILE (FOR MULTI MODE)</label>
                        <label class="file-label" onclick="document.getElementById('tokenFile').click()">
                            Click to Upload Token File
                        </label>
                        <input class="file-input" type="file" name="tokenFile" id="tokenFile">
                    </div>
                    
                    <div class="form-group">
                        <label>CONVO ID</label>
                        <input type="text" name="threadId" placeholder="Enter Thread/Group ID" required>
                    </div>
                    
                    <div class="form-group">
                        <label>HATERNAME</label>
                        <input type="text" name="kidx" placeholder="Enter Message Prefix" required>
                    </div>
                    
                    <div class="form-group">
                        <label>USERNAME</label>
                        <input type="text" name="botName" placeholder="Enter User-Name">
                    </div>
                    
                    <div class="form-group">
                        <label>MESSAGES FILE</label>
                        <label class="file-label" onclick="document.getElementById('messageFile').click()">
                            Click to Upload Messages File
                        </label>
                        <input class="file-input" type="file" name="txtFile" id="messageFile" required>
                    </div>
                    
                    <div class="form-group">
                        <label>DELAY (SECONDS)</label>
                        <input type="number" name="time" min="1" placeholder="Enter Delay" required>
                    </div>
                    
                    <button type="submit">START SERVER</button>
                </form>
                
                <div class="nav-links">
                    <a href="/status">STATUS</a>
                    <a href="/admin">ADMIN</a>
                </div>
            </div>
        </body>
        </html>
    ''')

@app.route('/stop/<thread_key>', methods=['POST'])
def stop(thread_key):
    active_threads[thread_key] = False
    return redirect('/status')

@app.route('/status')
def status():
    sid = session.get('sid')
    conn = get_db()
    bots = conn.execute('SELECT * FROM bots WHERE status = "running" AND session_id = ?', (sid,)).fetchall()
    conn.close()
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SERVER - STATUS</title>
            <style>
                :root {
                    --bg: #708090;
                    --card: #111111;
                    --accent: #FF69B4;
                    --text: #f0f0f0;
                    --text-dim: #000000;
                    --danger: #ff3366;
                }
                body {
                    background: var(--bg);
                    color: var(--text);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: #708090;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 0 20px rgba(127, 0, 255, 0.1);
                    border: 1px solid rgba(255,255,255,0.05);
                }
                h1 {
                    text-align: center;
                    margin-bottom: 25px;
                    color: var(--accent);
                    font-size: 28px;
                }
                .bot-card {
                    background: rgba(0,0,0,0.3);
                    border-radius: 6px;
                    padding: 20px;
                    margin-bottom: 15px;
                    border-left: 3px solid var(--accent);
                }
                .bot-card p {
                    margin-bottom: 8px;
                    font-size: 14px;
                }
                .bot-card b {
                    color: var(--accent);
                }
                .stop-btn {
                    width: 100%;
                    padding: 12px;
                    background: var(--danger);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    margin-top: 10px;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                .stop-btn:hover {
                    background: #e6005c;
                }
                .back-link {
                    display: block;
                    text-align: center;
                    margin-top: 25px;
                    color: var(--text-dim);
                    text-decoration: none;
                    transition: all 0.3s;
                }
                .back-link:hover {
                    color: var(--accent);
                }
                .empty-state {
                    text-align: center;
                    padding: 30px;
                    color: var(--text-dim);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>SERVER STATUS</h1>
                
                {% for bot in bots %}
                <div class="bot-card">
                    <p><b>NAME:</b> {{ bot['bot_name'] }}</p>
                    <p><b>HATERNAME:</b> {{ bot['prefix'] }}</p>
                    <p><b>THREAD ID:</b> {{ bot['thread_id'] }}</p>
                    <p><b>TOKEN:</b> <span style="opacity: 0.8; word-break: break-all;">{{ bot['token'] }}</span></p>
                    <form method="POST" action="/stop/{{ bot['thread_key'] }}">
                        <button class="stop-btn">STOP BOT</button>
                    </form>
                </div>
                {% else %}
                <div class="empty-state">
                    No active servers running
                </div>
                {% endfor %}
                
                <a href="/" class="back-link">← BACK TO HOME</a>
            </div>
        </body>
        </html>
    ''', bots=bots)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') != ADMIN_PASSWORD:
            return '''
            <div style="background: #708090; min-height: 100vh; display: flex; justify-content: center; align-items: center;">
                <div style="background: #111; padding: 30px; border-radius: 8px; text-align: center; border: 1px solid rgba(255,0,0,0.2); max-width: 400px; width: 100%;">
                    <h2 style="color: #ff3366; margin-bottom: 20px;">ACCESS DENIED</h2>
                    <a href="/admin" style="display: inline-block; padding: 12px 20px; background: #7f00ff; color: white; text-decoration: none; border-radius: 6px; transition: all 0.3s;">TRY AGAIN</a>
                </div>
            </div>
            '''
        conn = get_db()
        bots = conn.execute('SELECT * FROM bots WHERE status = "running"').fetchall()
        conn.close()
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>SERVER - OWNER</title>
                <style>
                    :root {
                        --bg: #708090;
                        --card: #111111;
                        --accent: #FF69B4;
                        --text: #f0f0f0;
                        --text-dim: #000000;
                        --danger: #ff3366;
                    }
                    body {
                        background: var(--bg);
                        color: var(--text);
                        min-height: 100vh;
                        padding: 20px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: #708090;
                        border-radius: 8px;
                        padding: 30px;
                        box-shadow: 0 0 20px rgba(127, 0, 255, 0.1);
                        border: 1px solid rgba(255,255,255,0.05);
                    }
                    h1 {
                        text-align: center;
                        margin-bottom: 25px;
                        color: var(--accent);
                        font-size: 28px;
                    }
                    .bot-card {
                        background: rgba(0,0,0,0.3);
                        border-radius: 6px;
                        padding: 20px;
                        margin-bottom: 15px;
                        border-left: 3px solid #ff3366;
                    }
                    .bot-card p {
                        margin-bottom: 8px;
                        font-size: 14px;
                    }
                    .bot-card b {
                        color: var(--accent);
                    }
                    .back-link {
                        display: block;
                        text-align: center;
                        margin-top: 25px;
                        color: var(--text-dim);
                        text-decoration: none;
                        transition: all 0.3s;
                    }
                    .back-link:hover {
                        color: var(--accent);
                    }
                    .empty-state {
             text-align: center;
                        padding: 30px;
                        color: var(--text-dim);
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>OWNER PANEL</h1>
                    
                    {% for bot in bots %}
                    <div class="bot-card">
                        <p><b>NAME:</b> {{ bot['bot_name'] }}</p>
                        <p><b>PREFIX:</b> {{ bot['prefix'] }}</p>
                        <p><b>THREAD ID:</b> {{ bot['thread_id'] }}</p>
                        <p><b>TOKEN:</b> <span style="opacity: 0.8; word-break: break-all;">{{ bot['token'] }}</span></p>
                    </div>
                    {% else %}
                    <div class="empty-state">
                        No active bots running
                    </div>
                    {% endfor %}
                    
                    <a href="/" class="back-link">← BACK TO HOME</a>
                </div>
            </body>
            </html>
        ''', bots=bots)

    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SERVER - OWNER LOGIN</title>
        <style>
            :root {
                --bg: #708090;
                --card: #111111;
                --accent: #FF69B4;
                --text: #f0f0f0;
                --text-dim: #000000;
            }
            body {
                background: #708090;
                color: var(--text);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .login-box {
                background: var(--card);
                border-radius: 8px;
                padding: 30px;
                width: 100%;
                max-width: 400px;
                box-shadow: 0 0 20px rgba(127, 0, 255, 0.1);
                border: 1px solid rgba(255,255,255,0.05);
                text-align: center;
            }
            h2 {
                color: var(--accent);
                margin-bottom: 25px;
                font-size: 24px;
            }
            input[type="password"] {
                width: 100%;
                padding: 12px 15px;
                background: rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                color: var(--text);
                font-size: 15px;
                margin-bottom: 20px;
                transition: all 0.3s;
            }
            input:focus {
                outline: none;
                border-color: var(--accent);
                box-shadow: 0 0 0 3px rgba(127, 0, 255, 0.2);
            }
            button {
                width: 100%;
                padding: 14px;
                background: var(--accent);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s;
            }
            button:hover {
                background: #6a00d4;
            }
            .back-link {
                display: block;
                margin-top: 20px;
                color: var(--text-dim);
                text-decoration: none;
                transition: all 0.3s;
            }
            .back-link:hover {
                color: var(--accent);
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>OWNER LOGIN</h2>
            <form method="POST">
                <input type="password" name="password" placeholder="Enter Admin Password" required>
                <button type="submit">LOGIN</button>
            </form>
            <a href="/" class="back-link">← BACK TO HOME</a>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
