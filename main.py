from playwright.sync_api import sync_playwright
from flask import Flask, render_template_string
from flask_sock import Sock
import threading
import time
import os
import json

PORT = int(os.environ.get("PORT", 5000))
app = Flask(__name__)
sock = Sock(app)

clients = set()

current_url = "尚未访问"
current_title = "尚未访问"
last_error = ""
page_text = ""

@app.route("/")
def index():
    return render_template_string("""
        <h2>Playwright 状态</h2>
        <div>当前 URL: <span id="url">{{ url }}</span></div>
        <div>页面标题: <span id="title">{{ title }}</span></div>
        <div>加载出错: <span id="error">{{ error }}</span></div>
        <div>页面内容: <pre id="text">{{ text }}</pre></div>

        <script>
        const ws = new WebSocket(`wss://${location.host}/ws`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            document.getElementById("url").textContent = data.url;
            document.getElementById("title").textContent = data.title;
            document.getElementById("error").textContent = data.error;
            document.getElementById("text").textContent = data.text;
        };
        </script>
    """, url=current_url, title=current_title, error=last_error, text=page_text)

@sock.route("/ws")
def websocket(ws):
    clients.add(ws)
    try:
        while True:
            msg = ws.receive()
            if msg is None:
                break
    finally:
        clients.remove(ws)

def broadcast_state():
    for ws in clients:
        try:
            ws.send(json.dumps({
                "url": current_url,
                "title": current_title,
                "error": last_error,
                "text": page_text
            }))
        except:
            pass

def run_server():
    app.run(host="0.0.0.0", port=PORT)

def run_playwright():
    global current_url, current_title, last_error, page_text
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
                "--no-zygote"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            locale="zh-TW",
            timezone_id="Asia/Taipei"
        )

        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")

        current_url = page.url
        current_title = page.title()
        page_text = page.text_content("body")[:500]
        broadcast_state()

        while True:
            try:
                page.wait_for_load_state("load", timeout=10000)

                new_url = page.url
                new_title = page.title()
                new_text = page.text_content("body")[:500]

                if new_url != current_url or new_title != current_title or new_text != page_text:
                    current_url = new_url
                    current_title = new_title
                    page_text = new_text
                    last_error = ""
                    broadcast_state()

            except Exception as e:
                last_error = str(e)
                broadcast_state()

            time.sleep(1)

threading.Thread(target=run_server, daemon=True).start()
run_playwright()
