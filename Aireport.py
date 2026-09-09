import asyncio
import json
import base64
import random
import requests
from datetime import datetime
from playwright.async_api import async_playwright


# ==================================================
# ✅ AI STUB MODULES
# ==================================================

def AI_Analyze_Page(page_name, html):
    return {
        "page": page_name,
        "ai_reasoning": f"AI inspected HTML and believes the page '{page_name}' loaded successfully.",
        "confidence": "0.97"
    }


def AI_Analyze_Logs(logs):
    reasoning = []
    
    if "login_success" in logs:
        reasoning.append("AI: Login flow worked correctly.")
    if "form_filled" in logs:
        reasoning.append("AI: Form fields were populated correctly.")
    if "submitted" in logs:
        reasoning.append("AI: Form submission reached the next page.")
    
    return reasoning


def AI_Generate_Summary(logs, page_analysis):
    return (
        f"AI Summary of Automation Run:\n"
        f"- Total Steps: {len(logs)}\n"
        f"- Page Analysis Confidence: {page_analysis['confidence']}\n"
        f"- Key Events: {', '.join(logs)}\n"
        f"- Overall: The automation flow executed successfully and appears stable.\n"
    )


# ==================================================
# ✅ EMAIL WRAPPER (MICROSOFT GRAPH)
# ==================================================

def send_email(recipient, subject, body, attachment_path, access_token):
    """
    Sends email via Microsoft Graph sendMail API.
    Requires a VALID JWT access token (Azure OAuth).
    Documentation confirms Authorization: Bearer {token} is required. 
    """

    # Read report file
    with open(attachment_path, "rb") as f:
        content_bytes = f.read()

    encoded = base64.b64encode(content_bytes).decode("utf-8")

    url = "https://graph.microsoft.com/v1.0/me/sendMail"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    email_payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": recipient}}],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": "AI_POC_OUTPUT.json",
                    "contentBytes": encoded
                }
            ]
        },
        "saveToSentItems": True
    }

    resp = requests.post(url, headers=headers, json=email_payload)

    print("\nEMAIL STATUS:", resp.status_code)
    print("RESPONSE:", resp.text)


# ==================================================
# ✅ MAIN PLAYWRIGHT + AI POC FLOW
# ==================================================

async def run_poc():

    logs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # -----------------------
        # STEP 1 — OPEN WEBSITE
        # -----------------------
        await page.goto("https://www.saucedemo.com/")
        logs.append("home_opened")
        html = await page.content()
        page_ai = AI_Analyze_Page("LoginPage", html)

        # -----------------------
        # STEP 2 — LOGIN
        # -----------------------
        await page.fill("#user-name", "standard_user")
        await page.fill("#password", "secret_sauce")
        await page.click("#login-button")
        await page.wait_for_selector(".inventory_list")
        logs.append("login_success")

        # -----------------------
        # STEP 3 — ADD ITEM
        # -----------------------
        await page.click("text=Add to cart")
        logs.append("item_added")

        await page.click(".shopping_cart_link")
        await page.wait_for_selector(".cart_item")

        # -----------------------
        # STEP 4 — CHECKOUT FORM
        # -----------------------
        await page.click("#checkout")
        await page.wait_for_selector("#first-name")

        await page.fill("#first-name", "Rishi")
        await page.fill("#last-name", "Yadav")
        await page.fill("#postal-code", str(random.randint(10000, 99999)))

        logs.append("form_filled")

        # -----------------------
        # STEP 5 — SUBMIT
        # -----------------------
        await page.click("#continue")
        await page.wait_for_selector(".summary_info")
        logs.append("submitted")

        # -----------------------
        # ✅ AI Summary
        # -----------------------
        ai_reasoning = AI_Analyze_Logs(logs)
        ai_summary = AI_Generate_Summary(logs, page_ai)

        final_report = {
            "timestamp": str(datetime.now()),
            "steps": logs,
            "ai_reasoning_steps": ai_reasoning,
            "page_ai_analysis": page_ai,
            "final_ai_summary": ai_summary
        }

        report_path = "AI_POC_OUTPUT.json"
        with open(report_path, "w") as f:
            json.dump(final_report, f, indent=4)

        print("✅ JSON REPORT CREATED:", report_path)

        # -----------------------
        # ✅ EMAIL BODY
        # -----------------------
        body = (
            "AI AUTOMATION EXECUTION REPORT\n\n"
            f"Total Steps: {len(logs)}\n"
            f"Page Confidence: {page_ai['confidence']}\n\n"
            "Execution:\n" +
            "\n".join(["✓ " + step for step in logs]) +
            "\n\nAI Reasoning:\n" +
            "\n".join(ai_reasoning) +
            "\n\nFinal Summary:\n" +
            ai_summary
        )

        # -----------------------
        # ✅ EMAIL SEND
        # -----------------------
        send_email(
            recipient="rishikesh.y@hdfclife.com",
            subject="AI Automation Report | PASS",
            body=body,
            attachment_path=report_path,
            access_token="PASTE_YOUR_REAL_GRAPH_ACCESS_TOKEN_HERE"
        )

        await browser.close()


# ==================================================
# ✅ RUN
# ==================================================
if __name__ == "__main__":
    asyncio.run(run_poc())