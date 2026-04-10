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

USERNAME = "sohai_tim_bot"
PASSWORD = "aa123ben"

# ========= 网页 =========
@app.route("/")
def index():
    return render_template_string("""
    <h3>Aternos运行日志</h3>
    <pre id="log"></pre>

    <script>
        const ws = new WebSocket(`ws://${location.host}/ws`);
        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            document.getElementById("log").textContent += data.log + "\\n";
        };
    </script>
    """)

# ========= websocket =========
@sock.route("/ws")
def ws(ws):
    clients.add(ws)
    try:
        while ws.receive() is not None:
            pass
    finally:
        clients.remove(ws)

# ========= 推送日志 =========
def push(msg):
    print(msg, flush=True)
    for c in list(clients):
        try:
            c.send(json.dumps({"log": msg}))
        except:
            pass

# ========= Playwright =========
def run():
    push("启动Playwright")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        page = browser.new_page()

        # 1. 打开网站
        push("打开 Aternos")
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")

        # 2. 输入账号
        push("输入账号")
        page.fill("input.username", USERNAME)

        push("输入密码")
        page.fill("input.password", PASSWORD)

        # 3. 登录
        push("点击登录")
        page.click("button.login-button")

        # 4. 等待登录成功
        try:
            page.wait_for_selector("a.servercard", timeout=20000)
            push("登录成功")
        except:
            push("登录失败")
            browser.close()
            return

        # 5. 进入服务器列表
        push("进入服务器列表")
        page.goto("https://aternos.org/servers/", wait_until="domcontentloaded")

        # 6. 循环监控
        while True:
            try:
                push(f"运行中 | {page.url} | {page.title()}")
            except Exception as e:
                push("错误: " + str(e))

            time.sleep(5)

# ========= 启动线程 =========
if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
