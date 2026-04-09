from playwright.sync_api import sync_playwright
import time
import os

PORT = int(os.environ.get("PORT", 5000))

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
    last_url = page.url
    print(f"Listening on port {PORT}")
    print("页面标题:", page.title())

    while True:
        page.wait_for_load_state("load")
        current_url = page.url
        if current_url != last_url:
            print("页面标题:", page.title())
            last_url = current_url
        time.sleep(5)
