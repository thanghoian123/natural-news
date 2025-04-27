import requests
from bs4 import BeautifulSoup
from datetime import datetime
from app.jobs.scheduler import scheduler
import pandas as pd
def extract_product_data(post):
    try:
        # Extracting the title and product URL
        title_tag = post.select_one(".listing-link")
        title = title_tag.get("title", "").strip() if title_tag else "No title"
        product_url = title_tag.get("href") if title_tag else None

        # Extracting the thumbnail image URL
        thumbnail_tag = post.select_one(".listing-card-image-no-shadow img")
        thumbnail = thumbnail_tag.get("src") if thumbnail_tag else None

        # Extracting the price and original price
        price_tag = post.select_one(".wt-text-slime")
        price = price_tag.text.strip() if price_tag else "No price"

        original_price_tag = post.select_one(".wt-text-strikethrough")
        original_price = original_price_tag.text.strip() if original_price_tag else None

        # Extracting the discount information (if available)
        discount_tag = post.select_one(".wt-text-caption.search-collage-promotion-price")
        discount = discount_tag.text.strip() if discount_tag else None

        return {
            "title": title,
            "product_url": product_url,
            "thumbnail": thumbnail,
            "price": price,
            "original_price": original_price,
            "discount": discount
        }

    except Exception as e:
        print(f"⚠️ Error extracting product data: {e}")
        return None

def crawl_product_data():
    url = 'https://www.etsy.com/shop/XuyenCraft?ref=shop-header-name&listing_id=1184846146&from_page=listing'

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }

    all_data = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        posts = soup.select(".js-merch-stash-check-listing")

        for post in posts:
            data = extract_product_data(post)
            if data:
                all_data.append(data)

        # Create a DataFrame and save it to an Excel file
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_excel("product_data.xlsx", index=False, engine="openpyxl")
            print(f"✅ Data written to 'product_data.xlsx'")

        now = datetime.utcnow()
        print(f"[{now}] 🕸️ Crawled product data from {url}")

    except requests.RequestException as e:
        print(f"❌ [{datetime.utcnow()}] Error during crawl: {e}")
def start_crawler_task():
    crawl_product_data()
    scheduler.add_job(crawl_product_data, "interval", hours=1, id="crawl_news", replace_existing=True)
    print("🕷️ Web crawler scheduler started.")
