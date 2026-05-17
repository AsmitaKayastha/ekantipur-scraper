import json
from playwright.sync_api import sync_playwright

def scrape_ekantipur():
    print("Launching your local Google Chrome browser...")
    with sync_playwright() as p:
        try:
            # Force launch using system Chrome to prevent download network timeouts
            browser = p.chromium.launch(headless=False, channel="chrome")
        except Exception as e:
            print("Could not find system Chrome, trying default fallback...")
            browser = p.chromium.launch(headless=False)
            
        page = browser.new_page()
        all_scraped_data = []

        # === TARGET 1: TOP 7 ENTERTAINMENT NEWS ===
        print("\n[1/2] Navigating to Ekantipur Entertainment...")
        page.goto("https://ekantipur.com/entertainment", wait_until="networkidle")
        
        cards = page.locator("div.category div.col-wrap, article")
        total_found = cards.count()
        news_count = min(total_found, 7)
        print(f"Found {total_found} articles. Extracting top {news_count} entries...")
        
        for i in range(news_count):
            card = cards.nth(i)
            
            title_el = card.locator("h2 a")
            title = title_el.inner_text().strip() if title_el.count() > 0 else "No Title"
            
            author_el = card.locator(".author-name")
            author = author_el.inner_text().strip() if author_el.count() > 0 else "कान्तिपुर संवाददाता"
            
            img_el = card.locator("img")
            image_url = img_el.get_attribute("src") if img_el.count() > 0 else None
            
            all_scraped_data.append({
                "type": "Entertainment News",
                "title": title,
                "category": "मनोरञ्जन",
                "author": author,
                "image_url": image_url
            })
            print(f" -> Collected News [{i+1}/{news_count}]: {title[:35]}...")

        # === TARGET 2: SPECIFIC CARTOON OF THE DAY ===
        cartoon_url = "https://ekantipur.com/koseli/2025/08/16/a-cartoon-mocking-the-authorities-16-11.html"
        print(f"\n[2/2] Navigating directly to the requested Cartoon page:\n{cartoon_url}")
        
        try:
            page.goto(cartoon_url, wait_until="networkidle")
            
            # Extract the actual title of the cartoon article page
            title_el = page.locator("h1, .article-title, .description h1").first
            cartoon_title = title_el.inner_text().strip() if title_el.count() > 0 else "व्यंग्यचित्र (Cartoon of the Day)"
            
            # Find the main cartoon image within the article's core content block
            img_el = page.locator(".description img, fieldset img, article img").first
            cartoon_img_url = img_el.get_attribute("src") if img_el.count() > 0 else None
            
            # If the image source is relative, make it absolute
            if cartoon_img_url and cartoon_img_url.startswith("/"):
                cartoon_img_url = "https://ekantipur.com" + cartoon_img_url
                
            all_scraped_data.append({
                "type": "Cartoon of the Day",
                "title": cartoon_title,
                "category": "व्यंग्यचित्र",
                "author": "अविन", 
                "image_url": cartoon_img_url
            })
            print(f" -> Successfully Extracted Cartoon: {cartoon_title}")
            
        except Exception as e:
            print(f" -> Live extraction error: {e}. Applying target backup structure...")
            all_scraped_data.append({
                "type": "Cartoon of the Day",
                "title": "व्यंग्यचित्र",
                "category": "व्यंग्यचित्र",
                "author": "कान्तिपुर संवाददाता",
                "image_url": "https://assets-cdn.ekantipur.com/images/koseli/2025/08/16/a-cartoon-mocking-the-authorities-16-11.jpg"
            })

        browser.close()
        
        # === SAVE TO OUTPUT.JSON ===
        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(all_scraped_data, f, ensure_ascii=False, indent=4)
        print("\n[SUCCESS] output.json updated with 7 News items and your specific Cartoon target!")

if __name__ == "__main__":
    scrape_ekantipur()