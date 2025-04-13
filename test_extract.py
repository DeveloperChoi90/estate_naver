from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
import csv
import time
from naver_estate_crawling import NaverEstateCrawler

# 디버그 로그 디렉토리 생성
debug_dir = "debug_logs"
os.makedirs(debug_dir, exist_ok=True)

# 크롤러 초기화 (브라우저 창 표시)
crawler = NaverEstateCrawler(headless=False)

try:
    # 네이버 부동산 URL (강남구 아파트 매물)
    url = "https://new.land.naver.com/complexes/117397?ms=37.5056,127.0562,17&a=APT&b=A1&e=RETAIL"
    
    # 브라우저 시작 및 URL 로드
    crawler.start_browser()
    crawler.driver.get(url)
    
    # 페이지 로딩 대기
    time.sleep(5)
    
    print("매물 목록 파싱 시작...")
    
    # 페이지 스크린샷 (디버깅용)
    crawler.driver.save_screenshot(os.path.join(debug_dir, "page.png"))
    
    # 안양씨엘포레자이 매물 페이지 파싱 시도
    print("\n특정 HTML 구조 파싱 시도 중...")
    
    # 매물 데이터를 저장할 리스트
    property_items = []
    
    # HTML 매물 요소 추출 (사용자가 보낸 HTML 구조 기반)
    try:
        # 1. 매물 항목의 조건을 확인
        items = crawler.driver.find_elements(By.CSS_SELECTOR, "div.item")
        
        # 사용할 수 있는 다양한 CSS 선택자 시도
        if not items:
            items = crawler.driver.find_elements(By.CSS_SELECTOR, "div.item_inner")
        if not items:
            items = crawler.driver.find_elements(By.CSS_SELECTOR, "div.article_item")
        if not items:
            items = crawler.driver.find_elements(By.CSS_SELECTOR, "li.item_list")
        if not items:
            items = crawler.driver.find_elements(By.CSS_SELECTOR, "li[class*='item']")
        
        print(f"발견된 매물 항목: {len(items)}개")
        
        # 각 매물 항목에서 정보 추출
        for i, item in enumerate(items):
            try:
                # 안전하게 텍스트 추출하는 함수
                def safe_extract(element, selector):
                    try:
                        elements = element.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            return elements[0].text.strip()
                    except:
                        pass
                    return ""
                
                # 매물 정보 추출
                property_data = {}
                
                # 매물 제목/이름 (아파트명, 동 정보)
                title_selectors = ["div.title", "div.item_title", "strong", "h2", "h3", "[class*='title']"]
                for selector in title_selectors:
                    title = safe_extract(item, selector)
                    if title:
                        property_data["title"] = title
                        break
                
                # 가격 정보
                price_selectors = ["div.price", "span.price", "span[class*='price']", "em", ".complex_price"]
                for selector in price_selectors:
                    price = safe_extract(item, selector)
                    if price and ("억" in price or "만" in price):
                        property_data["price"] = price
                        break
                
                # 아파트 정보 (타입, 면적, 층수, 방향)
                info_selectors = ["div.info", "span.info", "span[class*='info']", "p.info"]
                for selector in info_selectors:
                    info = safe_extract(item, selector)
                    if info:
                        property_data["info"] = info
                        break
                
                # 태그 정보 (특징)
                tags_selectors = ["div.tag_list", "span.tag", "div.tag", "[class*='tag']"]
                for selector in tags_selectors:
                    tags = safe_extract(item, selector)
                    if tags:
                        property_data["tags"] = tags
                        break
                
                # 확인 날짜
                date_selectors = ["div.date", "span.date", "[class*='date']"]
                for selector in date_selectors:
                    date = safe_extract(item, selector)
                    if date:
                        property_data["date"] = date
                        break
                
                # 중개사 수
                agent_selectors = ["div.agent_cnt", "span.agent", "[class*='agent']"]
                for selector in agent_selectors:
                    agent = safe_extract(item, selector)
                    if agent:
                        property_data["agent"] = agent
                        break
                
                # 이미지 URL
                try:
                    img_elements = item.find_elements(By.CSS_SELECTOR, "img")
                    if img_elements:
                        property_data["img_url"] = img_elements[0].get_attribute("src")
                except:
                    property_data["img_url"] = ""
                
                # 텍스트에서 정보 추출 (백업)
                item_text = item.text.strip()
                
                # 제목이 없을 경우 첫 번째 줄을 제목으로 설정
                if "title" not in property_data or not property_data["title"]:
                    lines = item_text.split('\n')
                    if lines:
                        property_data["title"] = lines[0].strip()
                
                # 가격이 없을 경우 정규식으로 추출
                if "price" not in property_data or not property_data["price"]:
                    price_pattern = r'(\d{1,3}(?:,\d{3})*억(?:\s*\d{1,3}(?:,\d{3})*만)?)'
                    price_match = re.search(price_pattern, item_text)
                    if price_match:
                        property_data["price"] = price_match.group(1)
                
                # 유효한 데이터만 추가 (제목과 가격이 있는 경우)
                if property_data.get("title") and property_data.get("price"):
                    property_items.append(property_data)
                    print(f"매물 #{i+1}: {property_data.get('title')} - {property_data.get('price')}")
            except Exception as e:
                print(f"매물 항목 처리 중 오류: {e}")
    
    except Exception as e:
        print(f"매물 목록 추출 중 오류: {e}")
    
    # CSV 파일로 저장
    if property_items:
        csv_file = "안양씨엘포레자이_매물.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ["title", "price", "info", "tags", "date", "agent", "img_url"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in property_items:
                writer.writerow(item)
        print(f"매물 정보 저장 완료: {csv_file} ({len(property_items)}개 항목)")
    else:
        print("추출된 매물 정보가 없습니다.")
    
    print("\n테스트 완료.")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")
    
finally:
    # 브라우저 종료
    crawler.close_browser() 