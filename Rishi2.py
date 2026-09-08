import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run_instainsure_flow():
    def log(msg):
        print(f"[LOG] {msg}")

    async def ss(page, tag):
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        path = f"screenshots/{tag}_{int(time.time())}.png"
        await page.screenshot(path=path, full_page=True)
        log(f"📸 SS: {path}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        # ✅ Enable VIDEO recording (FULL FLOW)
        if not os.path.exists("videos"):
            os.makedirs("videos")

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir="videos",            # ✅ Video folder
            record_video_size={"width": 1280, "height": 800}  # ✅ HD recording
        )

        page = await context.new_page()

        # ✅ Load Homepage
        await page.goto(
            "https://instainsure.hdfclife.com/open-market/form/HBANKOM/WP",
            wait_until="domcontentloaded"
        )
        log("✅ Page Loaded")
        await ss(page, "homepage")

        # ✅ Fill Mobile Number
        await page.fill("xpath=(//input)[1]", "8318777920")
        await ss(page, "mobile_filled")

        # ✅ Fill DOB
        log("✅ Filling DOB...")
        await page.fill("input[name='day']", "")
        await page.type("input[name='day']", "02", delay=60)
        await page.fill("input[name='month']", "")
        await page.type("input[name='month']", "12", delay=60)
        await page.fill("input[name='year']", "")
        await page.type("input[name='year']", "1997", delay=60)
        await ss(page, "dob_filled")

        await page.click("body", position={"x": 5, "y": 5})
        await page.wait_for_timeout(200)

        # ✅ Consent Checkbox
        log("✅ Clicking Consent Checkbox…")
        await page.click("input[type='checkbox']", force=True)
        await ss(page, "checkbox_clicked")

        # ✅ NEXT Button
        log("✅ Clicking NEXT…")
        next_btn = page.locator('[data-testid="opmk-proceed-btn"]')
        await next_btn.scroll_into_view_if_needed()
        await next_btn.click()
        await ss(page, "after_next_click")

        # ✅ Loader Wait
        try:
            await page.wait_for_selector("text=Please Wait", timeout=6000)
            log("✅ Loader Appeared")
            await ss(page, "loader_visible")
        except:
            log("⚠ Loader Not Detected")

        try:
            await page.wait_for_selector("text=Please Wait", state="detached", timeout=15000)
            log("✅ Loader Closed")
        except:
            log("⚠ Loader Timeout")

        await ss(page, "after_loader")

        # ✅ Backend Rejection Check
        log("⏳ Checking if backend returned to Personal Details…")
        try:
            pd_heading = page.locator("text=Personal Details").first
            if await pd_heading.is_visible():
                log("❌ OTP NOT Triggered — Backend Returned to Personal Details")
                await ss(page, "backend_rejected")
                await browser.close()
                return
        except:
            log("✅ No Personal Details heading detected — continue OTP detection")

        # ✅ OTP Page Detection
        log("⏳ Waiting for OTP Page…")

        try:
            await page.wait_for_selector("text=Please enter the OTP sent to you", timeout=20000)
            await page.wait_for_selector('input[maxlength="1"]', timeout=20000)
            await page.wait_for_selector('button:has-text("VERIFY")', timeout=20000)
            log("✅ OTP Page Loaded Successfully")
            await ss(page, "otp_loaded")
        except Exception as e:
            log(f"❌ OTP PAGE FAILED: {e}")
            await ss(page, "otp_failed")

        # ✅ Close browser
        await browser.close()

        # ✅ Save video file path
        video_path = await page.video.path()
        log(f"🎥 Video Saved: {video_path}")

# Run
if __name__ == "__main__":
    asyncio.run(run_instainsure_flow())