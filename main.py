from flask import Flask, render_template_string
from flask_sock import Sock
from playwright.sync_api import sync_playwright
import threading
import json
import time

app = Flask(__name__)
sock = Sock(app)

clients = set()
logs = []

def push(msg):
    logs.append(msg)
    for ws in list(clients):
        try:
            ws.send(json.dumps({"log": msg}))
        except:
            pass

@app.route("/")
def index():
    return render_template_string("""
    <h3>运行日志</h3>
    <pre id="log"></pre>

    <script>
        const ws = new WebSocket(`wss://${location.host}/ws`);
        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            document.getElementById("log").textContent += data.log + "\\n";
        };
    </script>
    """)

@sock.route("/ws")
def ws_handler(ws):
    clients.add(ws)
    try:
        while ws.receive() is not None:
            pass
    finally:
        clients.remove(ws)

def run_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        push("打开 Aternos")
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")

        push("当前标题: " + page.title())
        push("当前URL: " + page.url)

        while True:
            try:
                title = page.title()
                url = page.url
                push(f"{title} | {url}")
            except Exception as e:
                push("错误: " + str(e))

            time.sleep(5)

threading.Thread(target=run_playwright, daemon=True).start()

app.run(host="0.0.0.0", port=5000)
