import asyncio
import time
import os
from playwright.async_api import async_playwright, TimeoutError

# ==========================================
# ✅ LOG UTILS
# ==========================================
def log(msg):
    print(f"[LOG] {msg}")

# ==========================================
# ✅ SCREENSHOT (saves to /screenshots folder)
# ==========================================
async def take_ss(page, name):
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    ts = int(time.time())
    filename = f"screenshots/{name}_{ts}.png"
    await page.screenshot(path=filename, full_page=True)
    log(f"📸 Screenshot saved: {filename}")

# ==========================================
# ✅ SAFE CLICK
# ==========================================
async def safe_click(page, selector, timeout=15000):
    try:
        await page.click(selector, timeout=timeout)
        log(f"✅ Clicked: {selector}")
    except:
        log(f"❌ Click failed, retry: {selector}")
        await page.wait_for_timeout(2000)
        await page.click(selector)

# ==========================================
# ✅ SAFE FILL
# ==========================================
async def safe_fill(page, selector, value, timeout=15000):
    try:
        await page.fill(selector, value, timeout=timeout)
        log(f"✅ Filled {selector}")
    except:
        log(f"❌ Fill failed, retry: {selector}")
        await page.wait_for_timeout(2000)
        await page.fill(selector, value)

# ==========================================
# ✅ WAIT FOR LOAD
# ==========================================
async def wait_page_load(page):
    try:
        await page.wait_for_load_state("networkidle", timeout=20000)
    except:
        log("⚠ networkidle timeout, continue…")

# ==========================================
# ✅ FIXED DOB FUNCTION (elementHandle + JS)
# ==========================================
async def fill_dob(page, dob_value):
    log("✅ Using JS-based DOB fill…")

    dob_el = await page.query_selector("input[placeholder*='--/--/----']")

    if not dob_el:
        dob_el = await page.query_selector("xpath=(//input)[2]")

    if not dob_el:
        raise Exception("❌ DOB input not found")

    await dob_el.click()
    await page.wait_for_timeout(200)

    await page.evaluate("(el) => el.value = ''", dob_el)
    await page.wait_for_timeout(200)

    for ch in dob_value:
        await page.evaluate("(el, ch) => el.value = el.value + ch", dob_el, ch)
        await page.wait_for_timeout(80)

    log(f"✅ DOB entered: {dob_value}")
    await take_ss(page, "dob_filled_js")
async def fill_personal_details(page):
    log("⏳ Loading Personal Details page…")
    await wait_page_load(page)
    await take_ss(page, "personal_page_loaded")

    # ✅ Mobile
    await safe_fill(page, "xpath=(//input)[1]", "8318777920")
    await take_ss(page, "mobile_filled")

    # ✅ DOB
    log("✅ Filling DOB...")
    await page.fill("input[name='day']", "")
    await page.type("input[name='day']", "02", delay=80)

    await page.fill("input[name='month']", "")
    await page.type("input[name='month']", "12", delay=80)

    await page.fill("input[name='year']", "")
    await page.type("input[name='year']", "1997", delay=80)

    await take_ss(page, "dob_filled_correct")

    # ✅ Close calendar
    await page.click("body", position={'x': 10, 'y': 10})
    await page.wait_for_timeout(300)

    # ✅ Consent
    log("✅ Clicking consent checkbox…")
    try:
        await page.click("xpath=(//input[@type='checkbox'])[1]", force=True)
        log("✅ Consent checkbox clicked")
    except Exception as e:
        log(f"❌ Consent checkbox failed: {e}")
        await take_ss(page, "checkbox_click_failed")
        return

    await take_ss(page, "consent_checked")

    # ✅ NEXT BUTTON — REAL USER GESTURE CLICK (FIXED)
    log("✅ Clicking NEXT with real user events…")

    next_btn = page.locator('[data-testid="opmk-proceed-btn"]')

    await next_btn.dispatch_event("pointerdown")
    await next_btn.dispatch_event("mousedown")
    await next_btn.dispatch_event("mouseup")
    await next_btn.dispatch_event("pointerup")
    await next_btn.click(force=True)

    await take_ss(page, "after_next_click_fixed")

    # ✅ WAIT for OTP API to trigger (REAL backend delay)
    log("⏳ Waiting for OTP API & UI render…")
    await page.wait_for_timeout(10000)
    await take_ss(page, "after_api_wait")

    # ✅ OTP DETECTION (layout-based)
    log("⏳ Checking OTP component on same URL (layout-based)…")

    try:
        # Step indicator always present outside shadow DOM
        await page.wait_for_selector('text="Step 1/2"', timeout=15000)

        # Buttons guaranteed in OTP DOM
        await page.wait_for_selector('button:has-text("SUBMIT")', timeout=15000)
        await page.wait_for_selector('button:has-text("BACK")', timeout=15000)

        # OTP container
        await page.wait_for_selector('div[class*="OTP"]', timeout=15000)

        log("✅ OTP page successfully loaded!")
        await take_ss(page, "otp_page_loaded")

    except Exception as e:
        log(f"❌ OTP component NOT loaded: {e}")
        await take_ss(page, "otp_not_loaded")
        raise
# ==========================================
# ✅ STEP 1 – PERSONAL DETAILS
# ==========================================
# ==========================================
# ✅ STEP 2 – CHECKBOX PAGE
# ==========================================
# ==========================================
# ✅ STEP 3 — EXTRA DETAILS
# ==========================================

# ==========================================
# ✅ MAIN FLOW
# ==========================================
#async def main():
async def main():
    async with async_playwright() as p:

        # ✅ FIX: Codespaces requires headless=True (no GUI available)
        browser = await p.chromium.launch(
            headless=True,      # ✅ must be true in Codespaces
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--start-maximized"
            ]
        )

        # ✅ Keep your old viewport context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        # ✅ Open Instainsure landing page
        await page.goto(
            "https://instainsure.hdfclife.com/open-market/form/HBANKOM/WP",
            wait_until="domcontentloaded"
        )

        await take_ss(page, "homepage_loaded")

        # ✅ Call your personal details function
        await fill_personal_details(page)
        # await fill_second_page(page)
        # await fill_extra_details(page)

        log("✅✅✅ ALL STEPS COMPLETED ✅✅✅")

        await browser.close()
# ==========================================
if __name__ == "__main__":
    asyncio.run(main())