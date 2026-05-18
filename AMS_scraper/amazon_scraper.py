import os
import requests
from bs4 import BeautifulSoup
import hashlib
import re
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SCRAPER_API_KEY")

# 建立快取資料夾
CACHE_DIR = 'amazon_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def get_amazon_page(url, render_js=False):
    """
    獲取 Amazon 網頁，優先使用本機快取（防止重複扣點數與被封鎖）
    """
    # 網址轉成唯一的 MD5 檔名
    url_hash = "sample"
    cache_file = os.path.join(CACHE_DIR, f"{url_hash}.html")
    
    # 1. 檢查本機快取
    if os.path.exists(cache_file):
        print(f"[快取命中] 讀取本機檔案，花費 0 點數。 URL: {url[:50]}...")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()
            
    # 2. 快取未命中，呼叫 ScraperAPI
    print(f"[快取未命中] 正在呼叫 ScraperAPI 抓取... URL: {url[:50]}...")
    
    payload = {
        'api_key': api_key,
        'url': url
    }
    
    # 如果未來需要，可以切換為 True。目前搜尋列表頁使用 False (5點) 即可
    if render_js:
        payload['render'] = 'true' 
        
    try:
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
        if response.status_code == 200:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return response.text
        else:
            print(f"錯誤：API 回傳狀態碼 {response.status_code}")
            return None
    except Exception as e:
        print(f"發送請求時發生異常: {e}")
        return None

# ==================== 主要執行區塊 ====================
if __name__ == "__main__":
    # 網址後方加上 &language=en_US 強制讓 Amazon 回傳英文介面（避免中文"萬/千"造成數字洗掉）
    test_url = "https://www.amazon.com/s?k=PLA+filament+1.75mm&language=en_US"
    
    # 執行抓取（如果你已經刪除了舊快取，這次會觸發 [快取未命中]，扣除 5 點 API 額度）
    html_content = get_amazon_page(test_url, render_js=True)
    
    if html_content:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 尋找所有商品的搜尋結果外殼
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        scraped_data = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for product in products:
            # 1. 擷取 ASIN
            asin = product.get('data-asin', '').strip()
            if not asin:
                continue
                
            # 2. 擷取 標題
            title = "未知商品"
            h2_tag = product.find('h2')
            if h2_tag:
                title = h2_tag.get_text(strip=True)
            
            # 3. 擷取 價格
            price = "N/A"
            price_span = product.find('span', {'class': 'a-price'})
            if price_span:
                price_offscreen = price_span.find('span', {'class': 'a-offscreen'})
                if price_offscreen:
                    price = price_offscreen.get_text(strip=True)
            
            # 4. 擷取 評論數（標準英文版邏輯）
            review_count = "0"
            
            # 【策略 1】精準尋找商品卡片中含有「星等/評論」提示的獨立 div 或 span 外殼
            # Amazon 常用 'a-row a-size-small' 來包星星和評論數
            rating_section = product.find('div', {'class': 'a-row a-size-small'})
            if not rating_section:
                # 備用外殼版型
                rating_section = product.find('div', {'class': 's-item-container'})
                
            target_source = rating_section if rating_section else product
            
            # 【策略 2】從這個區塊裡尋找帶有 aria-label 且包含數字與逗號的標籤（最穩）
            review_links = target_source.find_all('a', {'class': 'a-link-normal'})
            for link in review_links:
                aria_label = link.get('aria-label', '')
                # 如果 aria-label 裡面寫著像是 "22,154 ratings" 或 "22,154 reviews"
                if 'rating' in aria_label.lower() or 'review' in aria_label.lower():
                    clean_digits = re.sub(r'\D', '', aria_label)
                    if clean_digits and len(clean_digits) > len(review_count):
                        review_count = clean_digits
                        break
            
            # 【策略 3】如果策略 2 沒撈到，用原本的網址尾端匹配法
            if review_count == "0":
                review_link = product.find('a', {'href': re.compile(r'#customerReviews$|#reviews$')})
                if review_link:
                    review_text = review_link.get_text(strip=True)
                    clean_digits = re.sub(r'\D', '', review_text)
                    if clean_digits:
                        review_count = clean_digits
                        
            # 【策略 4】如果還是 0，且撈到的數字小於等於 2 位數，極可能是誤抓了別的 class，清除它避免污染數據
            #（因為利基市場暢銷品不可能只有個位數/十位數評論）
            if review_count != "0" and int(review_count) <= 99:
                # 檢查是不是真的誤抓，嘗試從鄰近的 s-underline-text 提取
                underline_span = product.find('span', {'class': 's-underline-text'})
                if underline_span:
                    clean_digits = re.sub(r'\D', '', underline_span.get_text(strip=True))
                    if clean_digits:
                        review_count = clean_digits

            # 將結果打包成字典
            scraped_data.append({
                "Date": current_time,
                "ASIN": asin,
                "Price": price,
                "Reviews": review_count,
                "Title": title
            })
            
        # ==================== 顯示結構化結果 ====================
        print(f"\n[分析完成] 在網頁中成功解析出 {len(scraped_data)} 個有效商品：\n")
        print(f"{'ASIN':<12} | {'Price':<8} | {'Reviews':<8} | {'Title'}")
        print("-" * 80)
        for prod in scraped_data:
            # 終端機顯示時縮短標題長度，方便排版閱讀
            short_title = prod['Title'][:50] + "..." if len(prod['Title']) > 50 else prod['Title']
            print(f"{prod['ASIN']:<12} | {prod['Price']:<8} | {prod['Reviews']:<8} | {short_title}")
            
        # ==================== 將資料儲存並累加至 CSV 檔案 ====================
        csv_filename = "amazon_niche_data.csv"
        file_exists = os.path.exists(csv_filename)
        
        # 使用 utf-8-sig 編碼，確保 Excel 打開時中文或特殊符號（如貨幣符號）不會變亂碼
        with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["Date", "ASIN", "Price", "Reviews", "Title"])
            
            # 如果是全新的檔案，先寫入欄位名稱（表頭）
            if not file_exists:
                writer.writeheader()
                
            writer.writerows(scraped_data)
            
        print(f"\n[成功] 已將 {len(scraped_data)} 筆商品數據寫入/累加至 {csv_filename}！")