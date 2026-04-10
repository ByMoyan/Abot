from flask import Flask, render_template_string
from flask_sock import Sock
from playwright.sync_api import sync_playwright
import threading
import json
import time
import os

app = Flask(__name__)
sock = Sock(app)

clients = set()
logs = []

USERNAME = "sohai_tim_bot"
PASSWORD = "aa123ben"
SERVER_NAME = "87666test"
STATE_FILE = "state.json"

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

# ===== 登录判断 =====
def is_logged_in(page):
    push("检查登录状态...")
    page.goto("https://aternos.org/servers/", wait_until="domcontentloaded", timeout=30000)
    try:
        page.wait_for_selector("a.servercard", timeout=8000)
        push("已登录")
        return True
    except:
        push("未登录")
        return False

# ===== 登录流程 =====
def attempt_login(page, context):
    push("进入登录页")
    page.goto("https://aternos.org/go/", wait_until="domcontentloaded", timeout=30000)

    page.fill("input.username", USERNAME)
    time.sleep(1)

    page.fill("input.password", PASSWORD)
    time.sleep(1)

    push("点击登录")
    page.click("button.login-button")

    try:
        page.wait_for_selector("a.servercard", timeout=15000)
        context.storage_state(path=STATE_FILE)
        push("登录成功（已保存session）")
        return True
    except:
        push("登录失败")
        return False

# ===== 选择服务器 =====
def select_server(page):
    push("进入服务器列表")
    selector = f'a.servercard[title="{SERVER_NAME}"]'
    page.wait_for_selector(selector, timeout=15000)
    page.click(selector)
    push("已选择服务器")

# ===== 主逻辑 =====
def run_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
                "--no-zygote"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0",
            viewport={"width": 1280, "height": 720},
            locale="zh-TW",
            timezone_id="Asia/Taipei"
        )

        page = context.new_page()

        # ===== 1. 判断是否已登录 =====
        logged_in = False

        try:
            if os.path.exists(STATE_FILE):
                push("检测到本地session，尝试复用")
                context = browser.new_context(storage_state=STATE_FILE)
                page = context.new_page()

            logged_in = is_logged_in(page)
        except:
            logged_in = False

        # ===== 2. 未登录则登录 =====
        if not logged_in:
            push("开始登录")

            context = browser.new_context(
                user_agent="Mozilla/5.0",
                viewport={"width": 1280, "height": 720},
                locale="zh-TW",
                timezone_id="Asia/Taipei"
            )
            page = context.new_page()

            for i in range(3):
                if attempt_login(page, context):
                    logged_in = True
                    break
                push(f"尝试第{i+1}次登录")

        if not logged_in:
            push("登录失败")
            browser.close()
            return

        # ===== 3. 进入服务器列表前等待 =====
        push("进入伺服器选择页面")
        page.goto("https://aternos.org/servers/", wait_until="domcontentloaded", timeout=30000)

        page.wait_for_timeout(3000)
        push("选择服务器")

        # ===== 4. 选择服务器 =====
        select_server(page)

        push("流程结束")

        while True:
            time.sleep(5)
            push(f"运行中 | {page.title()} | {page.url}")

threading.Thread(target=run_playwright, daemon=True).start()

app.run(host="0.0.0.0", port=5000)
