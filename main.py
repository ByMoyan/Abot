from playwright.sync_api import sync_playwright
from flask import Flask
import threading
import time
import os

PORT = int(os.environ.get("PORT", 5000))
app = Flask(__name__)

current_url = "尚未访问"
current_title = "尚未访问"

@app.route("/")
def index():
    return f"当前URL: {current_url}<br>页面标题: {current_title}"

def run_server():
    app.run(host="0.0.0.0", port=PORT)

def run_playwright():
    global current_url, current_title
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
        page = browser.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")
        current_url = page.url
        current_title = page.title()
        print(f"Listening on port {PORT}")
        print("页面标题:", current_title)

        while True:
            try:
                page.wait_for_load_state("load", timeout=10000)
                if page.url != current_url:
                    current_url = page.url
                    current_title = page.title()
                    print("页面标题:", current_title)
            except Exception as e:
                print(f"页面加载出错: {e}")
            time.sleep(5)

threading.Thread(target=run_server, daemon=True).start()
run_playwright()
