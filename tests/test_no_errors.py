from playwright.sync_api import Playwright, Request


def on_failure(failure: Request):
    raise Exception(failure)


def test_has_title(playwright: Playwright):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    page.on("requestfailed", on_failure)
    page.goto("http://localhost:8000")
    browser.close()
