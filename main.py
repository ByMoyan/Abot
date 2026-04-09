from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path="/usr/bin/chromium"
    )
    page = browser.new_page()
    page.goto("https://aternos.org/go/", wait_until="domcontentloaded")
    print("页面标题:", page.title())
    browser.close()
