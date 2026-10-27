import asyncio
import os
import httpx
from playwright.async_api import async_playwright

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCREENSHOTS_DIR = os.path.join(ROOT_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

async def get_or_create_auth_token():
    email = "abhijith.candidate@example.com"
    password = "SecurePassword123!"
    full_name = "Abhijith AT"
    
    async with httpx.AsyncClient(base_url=BACKEND_URL) as client:
        # Try login first
        login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
        if login_resp.status_code == 200:
            return login_resp.json()["access_token"], login_resp.json().get("refresh_token", "")
        
        # Try register
        reg_resp = await client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "full_name": full_name
        })
        if reg_resp.status_code == 201:
            return reg_resp.json()["access_token"], reg_resp.json().get("refresh_token", "")
        
        # Fallback to random test user if needed
        import uuid
        rnd_email = f"user.{uuid.uuid4().hex[:6]}@example.com"
        reg_resp2 = await client.post("/api/v1/auth/register", json={
            "email": rnd_email,
            "password": password,
            "full_name": full_name
        })
        return reg_resp2.json()["access_token"], reg_resp2.json().get("refresh_token", "")

async def capture_all_views():
    access_token, refresh_token = await get_or_create_auth_token()
    print(f"Obtained auth token successfully.")

    # Initialize agent profile and test data
    async with httpx.AsyncClient(base_url=BACKEND_URL) as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        await client.get("/api/v1/agent/profile", headers=headers)
        await client.get("/api/v1/profile", headers=headers)
        try:
            # Trigger quick run so discovered jobs & briefing are full of data
            run_res = await client.post("/api/v1/agent/run-now?max_applications=2", headers=headers, timeout=60.0)
            print(f"Agent run completed: {run_res.status_code}")
        except Exception as e:
            print(f"Agent pre-run skipped: {e}")

    views_to_capture = [
        ("01_landing_page.png", f"{FRONTEND_URL}/?view=landing", False),
        ("02_auth_page.png", f"{FRONTEND_URL}/?view=auth", False),
        ("03_overview_dashboard.png", f"{FRONTEND_URL}/?view=dashboard", True),
        ("04_candidate_profile.png", f"{FRONTEND_URL}/?view=profile", True),
        ("05_autonomous_agent.png", f"{FRONTEND_URL}/?view=agent", True),
        ("06_target_jobs.png", f"{FRONTEND_URL}/?view=add-job", True),
        ("07_cv_editor_and_versions.png", f"{FRONTEND_URL}/?view=cv-editor", True),
        ("08_cover_letter_studio.png", f"{FRONTEND_URL}/?view=cover-email", True),
        ("09_applications_tracker.png", f"{FRONTEND_URL}/?view=applications", True),
        ("10_interview_prep.png", f"{FRONTEND_URL}/?view=interview", True),
        ("11_settings.png", f"{FRONTEND_URL}/?view=settings", True),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1.5,
        )

        for filename, url, needs_auth in views_to_capture:
            page = await context.new_page()
            
            # Inject localStorage tokens if authenticated
            if needs_auth:
                await page.goto(FRONTEND_URL)
                await page.evaluate(f"""
                    localStorage.setItem('ai_cv_access_token', '{access_token}');
                    localStorage.setItem('ai_cv_refresh_token', '{refresh_token}');
                """)

            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000) # Let animations and data finish rendering
            
            save_path = os.path.join(SCREENSHOTS_DIR, filename)
            await page.screenshot(path=save_path, full_page=False)
            print(f"Captured: {save_path}")
            await page.close()

        # Capture specific Agent Dashboard tabs to see the full agent capabilities
        page = await context.new_page()
        await page.goto(f"{FRONTEND_URL}/?view=agent")
        await page.wait_for_timeout(2000)
        
        # Tab: Discovered Jobs
        try:
            jobs_tab = page.locator("button:has-text('Discovered Jobs')")
            if await jobs_tab.count() > 0:
                await jobs_tab.first.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "12_agent_discovered_jobs_tab.png"))
                print("Captured: 12_agent_discovered_jobs_tab.png")
        except Exception as e:
            print(f"Error capturing discovered jobs tab: {e}")

        # Tab: Applications Pipeline
        try:
            apps_tab = page.locator("button:has-text('Applications Pipeline')")
            if await apps_tab.count() > 0:
                await apps_tab.first.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "13_agent_applications_tab.png"))
                print("Captured: 13_agent_applications_tab.png")
        except Exception as e:
            print(f"Error capturing applications tab: {e}")

        # Tab: Recruiter Outreach
        try:
            outreach_tab = page.locator("button:has-text('Recruiter Outreach')")
            if await outreach_tab.count() > 0:
                await outreach_tab.first.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "14_agent_outreach_tab.png"))
                print("Captured: 14_agent_outreach_tab.png")
        except Exception as e:
            print(f"Error capturing outreach tab: {e}")

        # Tab: QA Memory Bank
        try:
            qa_tab = page.locator("button:has-text('QA Memory Bank')")
            if await qa_tab.count() > 0:
                await qa_tab.first.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "15_agent_qa_memory_tab.png"))
                print("Captured: 15_agent_qa_memory_tab.png")
        except Exception as e:
            print(f"Error capturing QA tab: {e}")

        # Tab: Preferences
        try:
            pref_tab = page.locator("button:has-text('Preferences')")
            if await pref_tab.count() > 0:
                await pref_tab.first.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "16_agent_preferences_tab.png"))
                print("Captured: 16_agent_preferences_tab.png")
        except Exception as e:
            print(f"Error capturing preferences tab: {e}")

        await page.close()
        await browser.close()
        print("All screenshots captured successfully in:", SCREENSHOTS_DIR)

if __name__ == "__main__":
    asyncio.run(capture_all_views())
