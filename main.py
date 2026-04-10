import hashlib
import time

def run_playwright():
    global current_url, current_title, last_error, page_text

    last_hash = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )

        page = browser.new_page()
        page.goto("https://aternos.org/go/", wait_until="domcontentloaded")

        while True:
            try:
                page.wait_for_timeout(1000)

                # 当前状态
                url = page.url
                title = page.title()

                try:
                    text = page.inner_text("body")
                except:
                    text = ""

                # 用 hash 判断页面是否变化
                h = hashlib.md5(text.encode("utf-8")).hexdigest()

                if h != last_hash:
                    last_hash = h

                    current_url = url
                    current_title = title
                    page_text = text[:800]

                    broadcast_state()

            except Exception as e:
                last_error = str(e)
                broadcast_state()
                time.sleep(1)
