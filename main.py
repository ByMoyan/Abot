from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path="/usr/bin/chromium",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    page.goto("https://aternos.org/go/", wait_until="domcontentloaded")
    print("页面标题:", page.title())
    browser.close()
