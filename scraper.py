import asyncio
import json
import os
from playwright.async_api import async_playwright, Page
from config import get_settings

settings = get_settings()

class FacebookScraper:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None

    async def start_browser(self):
        """Starts the Playwright browser with stealth settings."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=settings.scraper.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        # Load cookies if available
        if os.path.exists(settings.facebook.cookies_file_path):
            try:
                with open(settings.facebook.cookies_file_path, 'r') as f:
                    cookies = json.load(f)
                    await self.context.add_cookies(cookies)
                print("✅ Cookies loaded successfully.")
            except Exception as e:
                print(f"⚠️ Failed to load cookies: {e}")

        self.page = await self.context.new_page()

    async def get_comments(self, post_url: str):
        """Navigates to a post and scrapes visible comments."""
        if not self.page:
            await self.start_browser()
        
        try:
            print(f"🕵️ Navigating to: {post_url}")
            await self.page.goto(post_url, timeout=60000)
            await self.page.wait_for_timeout(5000) # Wait for load

            # Simple scraping logic (Can be enhanced with specific selectors)
            # Collecting text from common comment containers
            content = await self.page.evaluate("""() => {
                return document.body.innerText;
            }""")
            
            return content[:10000] # Return first 10k chars for analysis

        except Exception as e:
            print(f"❌ Scraping Error: {e}")
            return ""
        finally:
            await self.close()

    async def close(self):
        if self.browser:
            await self.browser.close()

scraper_service = FacebookScraper()