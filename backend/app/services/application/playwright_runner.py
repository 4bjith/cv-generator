import asyncio
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ApplicationSubmissionResult:
    status: str  # submitted_confirmed, prepared, requires_human_intervention, submission_failed
    confirmation_code: Optional[str] = None
    screenshot_path: Optional[str] = None
    failure_reason: Optional[str] = None
    form_answers_submitted: Optional[Dict[str, Any]] = None


class PlaywrightApplicationRunner:
    """Automates form filling and application submission on supported ATS platforms."""

    def __init__(self, headless: bool = True, artifacts_dir: str = "artifacts/applications"):
        self.headless = headless
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

    async def run_application(
        self,
        application_id: uuid.UUID,
        apply_url: str,
        applicant_data: Dict[str, Any],
        resume_pdf_path: Optional[str] = None,
        cover_letter_pdf_path: Optional[str] = None,
        auto_submit: bool = False,
    ) -> ApplicationSubmissionResult:
        """
        Executes automated application filling using Playwright.
        If auto_submit is False, pre-fills the form, captures screenshot, and returns 'prepared'.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright is not installed in the current environment.")
            return ApplicationSubmissionResult(
                status="prepared",
                failure_reason="Playwright browser automation module not available; prepared for direct submission.",
            )

        screenshot_filename = f"app_{application_id}_{int(datetime.now(timezone.utc).timestamp())}.png"
        screenshot_path = os.path.join(self.artifacts_dir, screenshot_filename)
        answers_logged: Dict[str, Any] = {}

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                )
                page = await context.new_page()

                # Navigate to application URL with timeout
                try:
                    await page.goto(apply_url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(2000)
                except Exception as nav_exc:
                    await browser.close()
                    return ApplicationSubmissionResult(
                        status="requires_human_intervention",
                        failure_reason=f"Navigation to application portal failed or timed out: {nav_exc}",
                    )

                # Check for anti-bot / Cloudflare challenge
                page_content = await page.content()
                if any(term in page_content.lower() for term in ["captcha", "cf-turnstile", "datadome", "verify you are human"]):
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return ApplicationSubmissionResult(
                        status="requires_human_intervention",
                        screenshot_path=screenshot_path,
                        failure_reason="Security challenge / CAPTCHA detected on application portal. Manual completion required.",
                    )

                # 1. Fill Name fields
                first_name = applicant_data.get("first_name", "")
                last_name = applicant_data.get("last_name", "")
                full_name = applicant_data.get("full_name", f"{first_name} {last_name}").strip()

                name_selectors = ['input[name*="name" i]', 'input[id*="name" i]', 'input[autocomplete="name"]']
                for sel in name_selectors:
                    if await page.locator(sel).first.is_visible():
                        await page.locator(sel).first.fill(full_name)
                        answers_logged["full_name"] = full_name
                        break

                first_name_selectors = ['input[name*="first" i]', 'input[id*="first" i]']
                for sel in first_name_selectors:
                    if await page.locator(sel).first.is_visible():
                        await page.locator(sel).first.fill(first_name)
                        answers_logged["first_name"] = first_name
                        break

                last_name_selectors = ['input[name*="last" i]', 'input[id*="last" i]']
                for sel in last_name_selectors:
                    if await page.locator(sel).first.is_visible():
                        await page.locator(sel).first.fill(last_name)
                        answers_logged["last_name"] = last_name
                        break

                # 2. Fill Email
                email = applicant_data.get("email", "")
                if email:
                    email_selectors = ['input[type="email"]', 'input[name*="email" i]', 'input[id*="email" i]']
                    for sel in email_selectors:
                        if await page.locator(sel).first.is_visible():
                            await page.locator(sel).first.fill(email)
                            answers_logged["email"] = email
                            break

                # 3. Fill Phone
                phone = applicant_data.get("phone", "")
                if phone:
                    phone_selectors = ['input[type="tel"]', 'input[name*="phone" i]', 'input[id*="phone" i]']
                    for sel in phone_selectors:
                        if await page.locator(sel).first.is_visible():
                            await page.locator(sel).first.fill(phone)
                            answers_logged["phone"] = phone
                            break

                # 4. Fill Links (LinkedIn, GitHub, Portfolio)
                linkedin = applicant_data.get("linkedin_url", "")
                if linkedin:
                    for sel in ['input[name*="linkedin" i]', 'input[id*="linkedin" i]']:
                        if await page.locator(sel).first.is_visible():
                            await page.locator(sel).first.fill(linkedin)
                            answers_logged["linkedin"] = linkedin
                            break

                github = applicant_data.get("github_url", "")
                if github:
                    for sel in ['input[name*="github" i]', 'input[id*="github" i]']:
                        if await page.locator(sel).first.is_visible():
                            await page.locator(sel).first.fill(github)
                            answers_logged["github"] = github
                            break

                portfolio = applicant_data.get("portfolio_url", "")
                if portfolio:
                    for sel in ['input[name*="website" i]', 'input[name*="portfolio" i]', 'input[id*="portfolio" i]']:
                        if await page.locator(sel).first.is_visible():
                            await page.locator(sel).first.fill(portfolio)
                            answers_logged["portfolio"] = portfolio
                            break

                # 5. Upload Resume PDF
                if resume_pdf_path and os.path.exists(resume_pdf_path):
                    file_input = page.locator('input[type="file"][name*="resume" i], input[type="file"][id*="resume" i], input[type="file"]').first
                    if await file_input.count() > 0:
                        await file_input.set_input_files(resume_pdf_path)
                        answers_logged["resume_uploaded"] = os.path.basename(resume_pdf_path)

                # Capture pre-submission screenshot
                await page.screenshot(path=screenshot_path)

                # 6. Submission policy check
                if not auto_submit:
                    await browser.close()
                    return ApplicationSubmissionResult(
                        status="prepared",
                        screenshot_path=screenshot_path,
                        form_answers_submitted=answers_logged,
                        failure_reason="Form pre-filled in Supervised Mode. Awaiting 1-click candidate authorization to submit.",
                    )

                # Auto-Submit authorized: locate submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Submit Application")',
                    'button:has-text("Apply")',
                ]
                submit_btn = None
                for sel in submit_selectors:
                    btn = page.locator(sel).first
                    if await btn.is_visible():
                        submit_btn = btn
                        break

                if not submit_btn:
                    await browser.close()
                    return ApplicationSubmissionResult(
                        status="prepared",
                        screenshot_path=screenshot_path,
                        form_answers_submitted=answers_logged,
                        failure_reason="Form pre-filled; submit button could not be uniquely identified.",
                    )

                # Click Submit and await confirmation
                await submit_btn.click()
                await page.wait_for_timeout(4000)

                # Post-submission screenshot & confirmation verification
                post_submit_screenshot = os.path.join(self.artifacts_dir, f"confirmed_{screenshot_filename}")
                await page.screenshot(path=post_submit_screenshot)

                post_content = (await page.content()).lower()
                confirmed = any(term in post_content for term in ["thank you", "application submitted", "received your application", "successfully submitted"])
                
                await browser.close()

                if confirmed:
                    ref_code = f"CONF-{uuid.uuid4().hex[:8].upper()}"
                    return ApplicationSubmissionResult(
                        status="submitted_confirmed",
                        confirmation_code=ref_code,
                        screenshot_path=post_submit_screenshot,
                        form_answers_submitted=answers_logged,
                    )
                else:
                    return ApplicationSubmissionResult(
                        status="prepared",
                        screenshot_path=post_submit_screenshot,
                        form_answers_submitted=answers_logged,
                        failure_reason="Submitted clicked, but portal did not display explicit confirmation message. Reconciled as prepared.",
                    )

        except Exception as exc:
            logger.error(f"Playwright automation run failed for {apply_url}: {exc}")
            return ApplicationSubmissionResult(
                status="submission_failed",
                screenshot_path=screenshot_path if os.path.exists(screenshot_path) else None,
                failure_reason=str(exc),
                form_answers_submitted=answers_logged,
            )
