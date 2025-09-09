from playwright.async_api import async_playwright
from app.modules.loaders import load_file
import time
import json
import asyncio, random

async def crawl_and_extract(
    job_title="Software Engineer",
    job_location="Vietnam",
    max_pages=1,
    sleep_between=(1, 3)
):
    results = []
    counter = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for _ in range(max_pages):
            page = await browser.new_page()
            url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={job_location}&refresh=true&start={counter}"
            await page.goto(url, timeout=60000)

            job_cards = await page.locator("li").all()
            for card in job_cards:
                title = card.locator(".base-search-card__title")
                location = card.locator(".job-search-card__location")
                company = card.locator(".base-search-card__subtitle a")
                link = card.locator(".base-card__full-link")

                if await title.count() > 0 and await location.count() > 0 and await company.count() > 0 and await link.count() > 0:
                    job_link = await link.get_attribute("href")
                    job = {
                        "title": (await title.inner_text()).strip(),
                        "company": (await company.inner_text()).strip(),
                        "location": (await location.inner_text()).strip(),
                        "link": job_link,
                        "description": ""
                    }

                    detail_page = await browser.new_page()
                    try:
                        await detail_page.goto(job_link, timeout=60000)
                        desc_locator = detail_page.locator(".show-more-less-html__markup")
                        if await desc_locator.count() > 0:
                            job["description"] = (await desc_locator.inner_text()).strip()
                        else:
                            try:
                                docs = load_file([job_link])
                                if docs:
                                    job["description"] = docs[0].text.strip()
                            except:
                                pass
                    except:
                        pass
                    await detail_page.close()
                    results.append(job)

                    await asyncio.sleep(random.randint(sleep_between[0], sleep_between[1]))

            await page.close()
            counter += 25
        await browser.close()

    return results