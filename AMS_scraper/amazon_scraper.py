import os
import re
import csv
import time
import random
import hashlib
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SCRAPER_API_KEY")
CACHE_DIR = 'amazon_cache'

# 🚀 【終極商業模式切換開關】
# "organic" -> 精準拿滿 22 筆左右的正宗直排自然排名商品 (自動過濾橫向/大品牌影片廣告，適用 SEO 排名權重分析)
# "matrix"  -> 暴力拿滿 34 筆+ 全景數據 (包含大橫幅廣告、影片廣告、推薦位的所有實體 ASIN，適用 PPC 競品選品)
RUN_MODE = "matrix" 

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_amazon_page(url, render_js=False):
    """
    帶有本地快取功能與四段式深度滾動的 Amazon 網頁抓取函式
    """
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f"{url_hash}.html")
    
    if os.path.exists(cache_file):
        print(f"📦 [快取命中] 讀取本機檔案，花費 0 點數。")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return f.read()
            
    print(f"📡 [快取未命中] 正在呼叫 ScraperAPI 抓取... URL: {url[:60]}...")
    
    payload = {
        'api_key': api_key,
        'url': url
    }
    
    if render_js:
        payload['render'] = 'true' 
        # 四段式深度滾動，直達 9000 像素，每次停頓 2.5 秒，完全激發並榨乾 5 點的最大商業價值
        payload['js_scenario'] = (
            '{"instructions":['
            '{"scroll_x": 0, "scroll_y": 2500}, {"wait": 2500},'
            '{"scroll_x": 0, "scroll_y": 5000}, {"wait": 2500},'
            '{"scroll_x": 0, "scroll_y": 7500}, {"wait": 2500},'
            '{"scroll_x": 0, "scroll_y": 9000}, {"wait": 2500}'
            ']}'
        )
        
    try:
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=30)
        if response.status_code == 200:
            html_content = response.text
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return html_content
        else:
            print(f"❌ ScraperAPI 請求失敗，狀態碼: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 發生網路異常: {e}")
        return None

# ==================== 主要執行區塊 ====================
if __name__ == "__main__":
    
    # 測試監控的利基市場關鍵字池
    keywords_pool = [
        "PLA filament 1.75mm",
        "PETG filament 1.75mm",
        "3D printer nozzle 0.4mm"
    ]
    
    start_page = 1
    end_page = 2
    
    scraped_matrix_data = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🚀 【終極雙模數據引擎啟動】當前運行模式: 【{RUN_MODE.upper()}】")
    print(f"📊 準備掃描 {len(keywords_pool)} 個關鍵字，每個關鍵字抓取 {end_page} 頁...\n")
    
    for kw in keywords_pool:
        print(f"====== 🔍 正在探索利基市場：【{kw}】 ======")
        encoded_keyword = kw.replace(" ", "+")
        
        for page in range(start_page, end_page + 1):
            print(f"📄 正在處理 -> 第 {page} 頁...")
            
            target_url = f"https://www.amazon.com/s?k={encoded_keyword}&page={page}&language=en_US"
            
            # 呼叫抓取（開啟 JS 滾動渲染）
            html_content = get_amazon_page(target_url, render_js=True)
            
            if not html_content:
                print(f"⚠️ 關鍵字【{kw}】第 {page} 頁抓取失敗，跳過。")
                continue
                
            soup = BeautifulSoup(html_content, 'lxml')
            
            seen_asins_on_page = set()
            page_count = 0
            
            # ==================== 🌟 🚀 1. 品牌大橫幅廣告特種捕獲器 (大廣告區塊) ====================
            ad_containers = soup.find_all('div', class_=lambda x: x and any(cls in x.lower() for cls in ['sbv-video', 'creative-container', 'brand-story', 'shopping-ad']))
            
            if RUN_MODE == "matrix" and ad_containers:
                for ad_box in ad_containers:
                    
                    # 嘗試在廣告盒子內搜尋價格
                    ad_price = "N/A"
                    price_node = ad_box.find(string=re.compile(r'\$\d+\.\d+'))
                    if price_node:
                        ad_price = price_node.strip()
                    
                    # 嘗試在廣告盒子內搜尋評論
                    ad_review = "0"
                    underline_span = ad_box.find('span', {'class': 's-underline-text'})
                    if underline_span:
                        ad_review = re.sub(r'\D', '', underline_span.get_text(strip=True))
                    else:
                        parentheses_node = ad_box.find(string=re.compile(r'\(\d+[\d,]*\)'))
                        if parentheses_node:
                            ad_review = re.sub(r'\D', '', parentheses_node)
                            
                    # 遍歷廣告盒內的所有 ASIN
                    internal_asins = ad_box.find_all(attrs={"data-asin": True})
                    for node in internal_asins:
                        asin = node.get('data-asin', '').strip()
                        if asin and asin not in seen_asins_on_page:
                            
                            ad_title = "未知商品 (廣告推薦)"
                            h2_tag = node.find('h2') or ad_box.find('h2')
                            if h2_tag:
                                ad_title = h2_tag.get_text(strip=True)
                            else:
                                img_tag = node.find('img') or ad_box.find('img')
                                if img_tag and img_tag.get('alt'):
                                    ad_title = img_tag.get('alt').strip()
                                    
                            seen_asins_on_page.add(asin)

                            # 🎯 【真·物理防禦線】：如果價格是 N/A 且評論是 0，代表 100% 是被非同步卡住的廣告商品
                            # 我們直接強制將它轉換為標籤，不再留 N/A 和 0 給 Excel
                            if price == "N/A" and review_count == "0":
                                final_price = "Sponsored (Ad Dynamic)"
                                final_reviews = "Sponsored (Ad Dynamic)"
                            else:
                                final_price = price
                                final_reviews = review_count
                            
                            # 如果大橫幅非同步渲染導致抓不到實時價格/評論，給予明確的商業防禦標籤
                            scraped_matrix_data.append({
                                "Date": current_time,
                                "Keyword": kw,
                                "ASIN": asin,
                                "Price": final_price,
                                "Reviews": final_reviews,
                                "Title": ad_title
                            })
                            page_count += 1

            # ==================== 🏢 🌟 2. 標準商品 / 常規格子商品捕獲器 ====================
            all_asin_nodes = soup.find_all(attrs={"data-asin": True})
            
            for product in all_asin_nodes:
                asin = product.get('data-asin', '').strip()
                if not asin or asin in seen_asins_on_page:
                    continue
                    
                # 🛑 檢查這個常規商品的父層 Class 裡面有沒有廣告特徵 (無論是常規格子廣告還是橫幅)
                is_sponsored_item = False
                parent_classes = ""
                for parent in product.parents:
                    if parent.name == 'body':
                        break
                    p_class = parent.get('class')
                    if p_class:
                        parent_classes += " " + " ".join(p_class).lower()
                
                # 如果有廣告特徵關鍵字，記錄下來
                if any(x in parent_classes for x in ['ad-preview', 'creative-slot', 'shopping-ad', 'carousel', 'slot-', 's-sponsored']):
                    is_sponsored_item = True
                    
                # 如果目前是 Organic (純自然排名模式)，只要是廣告一律直接剔除不抓
                if RUN_MODE == "organic" and is_sponsored_item:
                    continue
                
                # 常規提取標題
                title = "未知商品"
                h2_tag = product.find('h2')
                if h2_tag:
                    title = h2_tag.get_text(strip=True)
                else:
                    img_tag = product.find('img')
                    if img_tag and img_tag.get('alt'):
                        title = img_tag.get('alt').strip()
                
                # 常規提取價格
                price = "N/A"
                price_span = product.find('span', {'class': 'a-price'})
                if price_span:
                    price_offscreen = price_span.find('span', {'class': 'a-offscreen'})
                    if price_offscreen:
                        price = price_offscreen.get_text(strip=True)
                if price == "N/A":
                    price_text_node = product.find(string=re.compile(r'\$\d+\.\d+'))
                    if price_text_node:
                        price = price_text_node.strip()

                # 常規提取評論數
                review_count = "0"
                underline_span = product.find('span', {'class': 's-underline-text'})
                if underline_span:
                    review_count = re.sub(r'\D', '', underline_span.get_text(strip=True))
                if review_count == "0":
                    parentheses_node = product.find(string=re.compile(r'\(\d+[\d,]*\)'))
                    if parentheses_node:
                        review_count = re.sub(r'\D', '', parentheses_node)

                # 記憶體去重記錄
                seen_asins_on_page.add(asin)
                
                # 🎯 物理防禦判斷
                if price == "N/A" and review_count == "0":
                    final_price = "Sponsored (Ad Dynamic)"
                    final_reviews = "Sponsored (Ad Dynamic)"
                else:
                    final_price = price
                    final_reviews = review_count

                scraped_matrix_data.append({
                    "Date": current_time,
                    "Keyword": kw,
                    "ASIN": asin,
                    "Price": final_price,
                    "Reviews": final_reviews,
                    "Title": title
                })
                page_count += 1
                
            print(f"✅ 成功提取 {page_count} 個【完全不重複】的有效商品。")
            
            # 【安全機制】非快取狀態下，隨機延遲 1~3 秒
            if not os.path.exists(os.path.join(CACHE_DIR, f"{hashlib.md5(target_url.encode('utf-8')).hexdigest()}.html")):
                time.sleep(random.uniform(1.0, 3.0))

    # ==================== 統一寫入 CSV ====================
    if scraped_matrix_data:
        csv_filename = "amazon_niche_data.csv"
        file_exists = os.path.exists(csv_filename)
        fieldnames = ["Date", "Keyword", "ASIN", "Price", "Reviews", "Title"]
        
        with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(scraped_matrix_data)
            
        print(f"\n🎉 【全案大成功】模式【{RUN_MODE.upper()}】掃描結束！共採集 {len(scraped_matrix_data)} 筆資料，已寫入 {csv_filename}！")
    else:
        print("❌ 未採集到任何數據。")