from playwright.sync_api import sync_playwright
import hashlib
import requests
import time
import db

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(headless=False, user_data_dir="my_profile")
    page = browser.new_page()
    page.goto("https://www.flaticon.com/stickers-most-downloaded", wait_until='domcontentloaded')

    for _ in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    page.wait_for_timeout(5000)

    page.wait_for_load_state("domcontentloaded")

    page.mouse.wheel(0, 2500)
    page.wait_for_timeout(3000)

    seen_image_hashes = set()

    
    def get_image_hash(images_bytes: bytes) -> str:
        return hashlib.md5(images_bytes).hexdigest()
    
    def is_duplicate_image(image_url: str) -> bool:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img_hash = get_image_hash(response.content)
        if img_hash in seen_image_hashes:
            return True
        seen_image_hashes.add(img_hash)
        return False
    
    print("Get progress Activated")
    progress = db.get_progress()
    current_page = progress if progress is not None else 0
    print(f"Resuming from page {current_page}")
    while current_page < 150:

        items = page.locator(".icon--holder")

        count = items.count()
        print("items:", count)

        for i in range(count):
            item = items.nth(i)

            img = item.locator("img")

            title = img.get_attribute("alt")
    
            image_url = img.get_attribute("data-src") or img.get_attribute("src")
            if is_duplicate_image(image_url):
                print(f"Duplicate image found for title: {title}. Skipping.")
                continue
            
            db.add_icon(title, image_url)
            print(f'title {i+1} : {title}, {image_url}')
        
        db.save_progress(current_page)
        print(f"Progress saved at page {current_page}")
        page.wait_for_timeout(5000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(10)  

        next_btn = page.locator(".pagination-next.bj-button.bj-button--primary")

        if next_btn.count() == 0 or not next_btn.is_visible():
            break

        href = next_btn.get_attribute("href")
        if not href:
            print("Next button does not have a valid href. Stopping.")
            break

        next_url = href if href.startswith("http") else "https://www.flaticon.com" + href
        print("Navigating to:", next_url)
        current_page = current_page + 1
        print(f"Processing page {current_page + 1}.")

        page.goto(next_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)  

    db.clear_progress()
    print("All pages scraped. Progress cleared.")
    browser.close()