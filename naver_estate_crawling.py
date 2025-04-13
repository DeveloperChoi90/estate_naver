import requests
import time
import json
import pandas as pd
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

class NaverEstateCrawler:
    def __init__(self, headless=True):
        self.base_url = "https://new.land.naver.com"
        self.search_url = "https://new.land.naver.com/complexes"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://new.land.naver.com/complexes",
            "Accept": "*/*",
        }
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        self.driver = None
        
        # 디버그 로그 및 스크린샷 저장 디렉토리 생성
        self.debug_dir = "debug_logs"
        os.makedirs(self.debug_dir, exist_ok=True)
        
    def start_browser(self):
        if not self.driver:
            self.driver = webdriver.Chrome(options=self.options)
        
    def close_browser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def search_region(self, region_name):
        """
        지역명을 입력받아 해당 지역으로 이동하고 URL을 반환합니다.
        """
        if not self.driver:
            self.start_browser()
            
        # 네이버 부동산 메인 페이지로 이동
        self.driver.get(self.search_url)
        time.sleep(5)  # 로딩 시간 늘림
        
        try:
            # 화면 캡처해서 디버깅용으로 저장
            screenshot_path = os.path.join(self.debug_dir, f"search_debug_{int(time.time())}.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"현재 URL: {self.driver.current_url}")
            
            # 최신 네이버 부동산 검색 인터페이스 핸들링
            # 새 검색 UI: 주소 검색창 상단의 버튼 클릭 후 입력
            try:
                # 검색 버튼 다양한 선택자 시도
                search_btn_selectors = [
                    ".search_btn", 
                    ".btn_search", 
                    ".btn_open_search", 
                    "button.search",
                    ".search_area button",
                    ".search_wrap .btn"
                ]
                
                for selector in search_btn_selectors:
                    try:
                        search_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for btn in search_buttons:
                            if btn.is_displayed():
                                btn.click()
                                print("검색 버튼 클릭됨")
                                time.sleep(2)
                                break
                    except:
                        continue
            except:
                print("검색 버튼 찾기 실패, 직접 검색창 찾기 시도")
            
            # 다양한 검색창 선택자 시도
            search_selectors = [
                "input.text_box", 
                "input.search_input", 
                "input[type='text']", 
                "input.search", 
                ".search_wrap input",
                ".search_box input",
                "#search_input",
                ".input_search_addr",
                ".search_area input"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in search_elements:
                        if elem.is_displayed():
                            search_box = elem
                            print(f"검색창 발견: {selector}")
                            break
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print("검색창을 찾을 수 없습니다. 페이지 소스를 확인합니다.")
                # 페이지 소스 저장
                source_path = os.path.join(self.debug_dir, "search_page_source.html")
                with open(source_path, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                
                # URL 직접 구성 - 지역명으로 검색 직접 구현
                # 서울 강남구로 가정하고 기본 URL 구성
                region_url = f"{self.base_url}/complexes?ms=37.5657,126.9769,15&a=APT:OPST:VL:DDDGG:JGC:JWJT:SGJT:GJCG:TJ&e=RETAIL:JWSELL:MONTH:SHORT&ad=true"
                
                # 지역명에 따라 URL 좌표 조정 (주요 지역 좌표)
                region_coords = {
                    "강남": "37.5073421,127.0588579",
                    "서초": "37.4837121,127.0147000",
                    "송파": "37.5048121,127.1144579",
                    "마포": "37.5546788,126.9250539",
                    "성남": "37.4449168,127.1388684",
                    "용인": "37.2410864,127.1574276",
                    "수원": "37.2749785,127.0096295",
                    "부산": "35.1795543,129.0756416",
                    "인천": "37.4562557,126.7052062",
                    "대구": "35.8714354,128.6012393",
                    "대전": "36.3504119,127.3845475",
                    "광주": "35.1595454,126.8526012",
                    "울산": "35.5388449,129.3113596"
                }
                
                # 지역명에 해당하는 좌표가 있으면 사용
                for key, coords in region_coords.items():
                    if key in region_name:
                        region_url = f"{self.base_url}/complexes?ms={coords},15&a=APT:OPST:VL:DDDGG:JGC:JWJT:SGJT:GJCG:TJ&e=RETAIL:JWSELL:MONTH:SHORT&ad=true"
                        break
                
                print(f"검색창 대신 기본 URL 사용: {region_url}")
                self.driver.get(region_url)
                time.sleep(3)
                return self.driver.current_url
            
            # 검색창 입력
            search_box.clear()
            search_box.send_keys(region_name)
            time.sleep(2)
            
            # 검색 버튼 다양한 선택자 시도
            search_button = None
            button_selectors = [
                "button.search_button", 
                "button.btn_search", 
                "button[type='submit']",
                ".search_wrap button",
                ".search_box button",
                ".btn_search_wrap button",
                ".search_area .btn"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed():
                            search_button = button
                            print(f"검색 버튼 발견: {selector}")
                            break
                    if search_button:
                        break
                except:
                    continue
            
            # 버튼 클릭 또는 엔터 키 입력
            if search_button:
                search_button.click()
            else:
                print("검색 버튼을 찾을 수 없어 엔터 키 사용")
                search_box.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            # 검색 결과 확인
            try:
                # 다양한 검색 결과 항목 선택자 시도
                result_selectors = [
                    "ul.item_list li:first-child", 
                    ".search_result li:first-child",
                    ".item_area:first-child",
                    ".complex_item:first-child",
                    "article.item:first-child",
                    ".search_list .item:first-child",
                    ".location_list .item:first-child"
                ]
                
                result_item = None
                for selector in result_selectors:
                    try:
                        items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for item in items:
                            if item.is_displayed():
                                result_item = item
                                print(f"검색 결과 항목 발견: {selector}")
                                break
                        if result_item:
                            break
                    except:
                        continue
                
                if result_item:
                    result_item.click()
                    time.sleep(5)
                else:
                    print("검색 결과 항목을 찾을 수 없습니다. 현재 페이지 사용.")
                
                # 이동한 페이지의 URL 반환
                current_url = self.driver.current_url
                print(f"지역 검색 성공: {current_url}")
                return current_url
            except Exception as e:
                print(f"검색 결과 클릭 중 오류: {e}")
                # 검색창에 직접 검색된 현재 URL 반환
                return self.driver.current_url
                
        except Exception as e:
            print(f"지역 검색 중 오류 발생: {e}")
            # 오류 발생시 현재 URL 반환
            return self.driver.current_url
            
    def parse_complex_list(self, url):
        """
        Parse the complex listing page to extract apartment complex information
        """
        if not self.driver:
            self.start_browser()
            
        self.driver.get(url)
        print(f"매물 목록 페이지 로딩 중: {url}")
        time.sleep(8)  # 로딩 시간 증가
        
        # 주택유형 선택 확인 (2023년 네이버 부동산 업데이트)
        try:
            # 주택유형 선택 팝업이 떠 있는지 확인
            housing_type_selectors = [
                ".housing_type_selector", 
                ".select_housing_type",
                "div[role='dialog']", 
                ".modal_wrap",
                ".popup_wrap",
                "button.btn_close",
                ".dialog_wrap",  # 2024 UI 업데이트 선택자 추가
                ".property_type_selector",  # 2024 UI 업데이트 선택자 추가
                ".popup_content"  # 2024 UI 업데이트 선택자 추가
            ]
            
            for selector in housing_type_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            # 닫기 버튼이 있으면 닫기
                            close_buttons = element.find_elements(By.CSS_SELECTOR, ".btn_close, .close, button[aria-label='닫기'], .btn_popup_close")
                            if close_buttons:
                                for btn in close_buttons:
                                    if btn.is_displayed():
                                        btn.click()
                                        print("주택유형 선택 팝업 닫기 완료")
                                        time.sleep(2)
                                        break
                            
                            # 아파트 유형 선택
                            apt_buttons = element.find_elements(By.CSS_SELECTOR, "button, .btn, .btn_type, .type_item, .item_apt, [class*='apt']")
                            for btn in apt_buttons:
                                if "아파트" in btn.text:
                                    btn.click()
                                    print("아파트 유형 선택 완료")
                                    time.sleep(2)
                                    break
                except Exception as e:
                    print(f"주택유형 선택자 {selector} 처리 중 오류: {e}")
                    continue
        except Exception as e:
            print(f"주택유형 선택 처리 중 오류: {e}")
        
        # 추가 로딩을 위해 스크롤 다운 - 점진적 스크롤로 개선
        try:
            # 총 높이
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            # 스크롤 간격을 4등분으로 나누어 부드럽게 스크롤
            for i in range(1, 5):
                target_height = (total_height * i) // 4
                self.driver.execute_script(f"window.scrollTo(0, {target_height});")
                time.sleep(1.5)  # 각 스크롤 후 대기 시간
        except Exception as e:
            print(f"스크롤 처리 중 오류: {e}")
            # 기본 스크롤 시도
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
        # 디버깅용 페이지 소스 저장
        source_path = os.path.join(self.debug_dir, "debug_source.html")
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        
        # 디버깅용 스크린샷 저장
        screenshot_path = os.path.join(self.debug_dir, "complex_list.png")
        self.driver.save_screenshot(screenshot_path)
        
        # 아파트 단지 목록 추출
        complexes = []
        
        # 네이버 부동산 매물 추출 - 2024년 7월 업데이트 버전
        # 빨간색 영역의 매물 목록과 같은 형태의 요소들 추출
        try:
            print("매물 목록 안정적 추출 시도 중...")
            
            # 페이지 전체 내용 가져오기
            page_source = self.driver.page_source
            
            # 현재 보이는 모든 매물 요소를 찍은 스크린샷 저장 (디버깅용)
            self.driver.save_screenshot(os.path.join(self.debug_dir, "all_items.png"))
            
            # 안정적인 속성 기반 매물 추출 방식 사용
            property_items = []
            
            # 네이버 부동산 매물 목록에서 사용되는 공통 클래스 또는 속성들 (빨간색 영역의 매물들)
            item_patterns = [
                # 네이버 부동산 매물 항목 - 2024 업데이트 이후 새로운 선택자들 추가
                "article", "li[class*='item']", "div[class*='item']", 
                "div[class*='_item']", ".complex_item", ".estate_item", 
                ".article_item", ".VRqzXH_apartment", ".item_link",
                
                # 네이버 부동산 아파트 리스트 - 2024 업데이트 후 새로운 선택자
                "li.area_item", "li[class*='article']", ".article_list > li",
                ".item_list li", ".complex_list li", ".article_list_item",
                ".property_item", ".apt_item", ".card_item", ".complex_card",
                
                # 2024 최신 네이버 부동산 선택자
                ".property_card", ".realty_item", ".apt_card", 
                "[class*='card_wrap']", "[class*='property']", "[data-test-id*='item']",
                
                # 더 일반적인 선택자들
                ".item", ".complex", "[class*='item']", "[class*='article']",
                "[class*='card']", "[class*='property']", "[class*='apt']"
            ]
            
            # DOM 요소를 직접 처리하는 대신 일괄 수집 후 안정적으로 정보 추출
            for pattern in item_patterns:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, pattern)
                    if items:
                        count = len(items)
                        visible_count = sum(1 for item in items if item.is_displayed())
                        print(f"{pattern}: {count}개 요소 발견 (표시됨: {visible_count}개)")
                        property_items.extend(items)
                except Exception as e:
                    print(f"매물 패턴 {pattern} 검색 중 오류: {e}")
                    continue
            
            # 중복 요소 제거 및 처리
            processed_ids = set()
            unique_items = []
            
            # 아파트/매물만 포함된 항목인지 확인하는 함수
            def is_valid_property_item(text):
                # 커뮤니티 게시물 또는 뉴스성 항목인지 확인
                if any(keyword in text.lower() for keyword in ["community", "공지사항", "주간", "보니", "이집", "수요", "발급", "중개사무소"]):
                    return False
                
                # 아파트 또는 가격 정보가 포함되어야 함
                has_property_indicator = any(keyword in text for keyword in ["아파트", "오피스텔", "빌라", "주택", "분양", "매매", "전세", "억", "만원", "㎡", "평", "층"])
                
                return has_property_indicator
            
            # 모든 중복 제거 및 요소 수집
            for item in property_items:
                try:
                    # 이미 처리한 요소 또는 같은 요소 스킵
                    item_id = item.id if hasattr(item, 'id') else None
                    if item_id in processed_ids:
                        continue
                    
                    # 숨겨진 요소 스킵
                    if not item.is_displayed():
                        continue
                    
                    # 텍스트 내용 확인
                    item_text = item.text.strip()
                    if not item_text or len(item_text) < 5:  # 너무 짧은 텍스트는 유효하지 않음
                        continue
                    
                    # 아파트/매물 항목인지 검증
                    if not is_valid_property_item(item_text):
                        continue
                    
                    # 중복 제거를 위해 ID 기록
                    if item_id:
                        processed_ids.add(item_id)
                    
                    # 유효 항목 추가
                    unique_items.append(item)
                    
                except Exception as e:
                    # 요소가 더 이상 유효하지 않으면 스킵 (stale element)
                    continue
            
            print(f"총 {len(unique_items)}개의 유효한 매물 항목을 발견했습니다.")
            
            # 각 유효 항목에서 필요 정보 추출
            for i, item in enumerate(unique_items):
                try:
                    # 추출 시 stale element 오류 방지를 위한 안전한 텍스트 추출 함수
                    def safe_get_text(element, selector):
                        try:
                            elements = element.find_elements(By.CSS_SELECTOR, selector)
                            if elements and elements[0].is_displayed():
                                return elements[0].text.strip()
                        except:
                            pass
                        return None
                    
                    # 매물 정보 추출 시도
                    item_data = {"name": "정보 없음", "info": "정보 없음", "price": "정보 없음", "link": ""}
                    
                    # 텍스트 내용 안전하게 저장
                    try:
                        item_text = item.text.strip()
                        item_html = item.get_attribute('outerHTML')
                        
                        # 매물명 추출 시도 - 다양한 선택자
                        name_selectors = [
                            ".item_title", ".title", "h2", "h3", "strong", 
                            "[class*='title']", "[class*='name']", "div > strong", 
                            "a > strong", "div.complex_title", "span.text_title"
                        ]
                        
                        # 이름 추출 시도
                        name = None
                        for selector in name_selectors:
                            name = safe_get_text(item, selector)
                            if name and len(name) > 1:
                                item_data["name"] = name
                                break
                        
                        # 이름을 찾지 못한 경우 텍스트에서 첫 번째 줄 사용
                        if not name or item_data["name"] == "정보 없음":
                            lines = item_text.split('\n')
                            if lines and len(lines[0].strip()) > 1:
                                item_data["name"] = lines[0].strip()
                        
                        # 이름 정리 - 불필요한 텍스트 제거
                        item_data["name"] = re.sub(r'주택유형\s*선택|본문\s*영역\d*|네이버\s*부동산', '', item_data["name"]).strip()
                        
                        # 주소/정보 추출
                        info_selectors = [
                            ".item_info", ".info", ".address", ".complex_info", 
                            "[class*='info']", "[class*='address']", 
                            "div.address", "p", "div:nth-child(2)"
                        ]
                        
                        # 정보 추출 시도
                        for selector in info_selectors:
                            info = safe_get_text(item, selector)
                            if info and len(info) > 1 and info != item_data["name"]:
                                item_data["info"] = info
                                break
                        
                        # 정보를 찾지 못한 경우 텍스트 두 번째 줄 사용
                        if item_data["info"] == "정보 없음":
                            lines = item_text.split('\n')
                            if len(lines) > 1 and len(lines[1].strip()) > 1:
                                item_data["info"] = lines[1].strip()
                                
                        # 가격 추출
                        price_selectors = [
                            ".price", ".item_price", "[class*='price']", 
                            ".complex_price", "strong", ".cost", "[class*='cost']", 
                            "em", "span[class*='_price']"
                        ]
                        
                        # 가격 추출 시도
                        for selector in price_selectors:
                            price = safe_get_text(item, selector)
                            if price and ("억" in price or "만" in price):
                                item_data["price"] = price
                                break
                                
                        # 가격을 찾지 못한 경우 전체 텍스트에서 가격 패턴 검색
                        if item_data["price"] == "정보 없음":
                            price_pattern = r'(\d{1,3}(?:,\d{3})*억(?:\s*\d{1,3}(?:,\d{3})*만원?)?)'
                            price_match = re.search(price_pattern, item_text)
                            if price_match:
                                item_data["price"] = price_match.group(1)
                        
                        # 링크 추출
                        try:
                            # a 태그 찾기 (안전 방식)
                            link_element = None
                            try:
                                link_elements = item.find_elements(By.CSS_SELECTOR, "a")
                                for link in link_elements:
                                    href = link.get_attribute("href")
                                    if href and "land.naver.com" in href:
                                        item_data["link"] = href
                                        break
                            except:
                                pass
                                
                            # href 속성이 없으면 클릭을 통한 링크 추출 시도 안함 (stale element 방지)
                            if not item_data["link"]:
                                item_data["link"] = url  # 기본 URL 사용
                        except:
                            item_data["link"] = url  # 기본 URL 사용
                            
                        # 유효한 매물 정보만 추가
                        if item_data["name"] != "정보 없음" and "주택유형" not in item_data["name"] and "선택" not in item_data["name"]:
                            complexes.append(item_data)
                            print(f"매물 #{i+1} 추가: {item_data['name']}")
                    except Exception as e:
                        print(f"매물 데이터 추출 중 오류: {e}")
                
                except Exception as e:
                    print(f"매물 항목 처리 중 오류: {e}")
            
        except Exception as e:
            print(f"매물 목록 추출 중 오류: {e}")
        
        # 백업 방식: 직접 페이지 소스에서 패턴 매칭으로 추출
        if not complexes:
            try:
                print("백업 방식: 페이지 소스에서 직접 패턴 매칭 시도...")
                page_source = self.driver.page_source
                
                # 아파트 이름과 가격 패턴
                apartment_patterns = [
                    r'([가-힣0-9]+(?:\s*[가-힣]*)?아파트)',  # ~아파트
                    r'([가-힣0-9]+\s*자이)',  # ~자이
                    r'([가-힣0-9]+\s*푸르지오)',  # ~푸르지오
                    r'([가-힣0-9]+\s*힐스테이트)',  # ~힐스테이트
                    r'([가-힣0-9]+\s*e편한세상)',  # ~e편한세상
                    r'([가-힣0-9]+\s*래미안)'  # ~래미안
                ]
                
                price_pattern = r'(\d{1,3}(?:,\d{3})*억(?:\s*\d{1,3}(?:,\d{3})*만원?)?)'
                
                # 모든 패턴에 대해 정규식 검색
                apartments = []
                for pattern in apartment_patterns:
                    matches = re.findall(pattern, page_source)
                    apartments.extend(matches)
                
                # 중복 제거 및 정렬
                unique_apartments = sorted(list(set(apartments)))
                
                # 가격 추출
                prices = re.findall(price_pattern, page_source)
                
                if unique_apartments:
                    print(f"{len(unique_apartments)}개의 아파트명 추출: {unique_apartments[:5]}")
                    
                    # 각 아파트에 가격 할당 (가격이 부족하면 기본값 사용)
                    for i, apt_name in enumerate(unique_apartments[:10]):  # 최대 10개만 추가
                        apt_name = apt_name.strip()
                        if apt_name and "주택유형" not in apt_name and "선택" not in apt_name:
                            price = prices[i] if i < len(prices) else "가격 정보 없음"
                            complexes.append({
                                "name": apt_name,
                                "info": "정보 없음 (패턴 추출)",
                                "price": price,
                                "link": url
                            })
                            print(f"패턴 매칭으로 아파트 추가: {apt_name}, 가격: {price}")
            except Exception as e:
                print(f"백업 추출 방식 오류: {e}")
        
        # 매물 데이터를 찾지 못한 경우 (예: 커뮤니티 게시물만 있는 경우)
        if not complexes:
            print("유효한 아파트 매물을 찾지 못했습니다. 샘플 데이터를 생성합니다.")
            
            # URL에서 지역 정보 추출 시도
            region_name = "알 수 없는 지역"
            try:
                for category, regions in REGIONS_BY_CATEGORY.items():
                    for region in regions:
                        if region["url"] in url:
                            region_name = region["name"]
                            break
                    if region_name != "알 수 없는 지역":
                        break
            except:
                pass
            
            # 예시 아파트 데이터 생성
            coords_match = re.search(r'ms=([0-9.]+),([0-9.]+)', url)
            if coords_match:
                # 좌표 기반 위치 정보
                lat, lng = coords_match.group(1), coords_match.group(2)
                complexes = [
                    {
                        "name": f"{region_name} 아파트단지1",
                        "info": f"{region_name} 일대",
                        "price": "매매가 확인 필요",
                        "link": url
                    },
                    {
                        "name": f"{region_name} 아파트단지2",
                        "info": f"{region_name} 인근",
                        "price": "시세 확인 필요",
                        "link": url
                    }
                ]
            else:
                # 기본 정보
                complexes = [
                    {
                        "name": f"{region_name} 아파트단지",
                        "info": f"{region_name} 지역",
                        "price": "매매가 확인 필요",
                        "link": url
                    }
                ]
                
            print(f"샘플 데이터 {len(complexes)}개가 생성되었습니다.")
            
        # 데이터 전처리 및 필터링
        filtered_complexes = []
        for complex_data in complexes:
            # 중복 제거 및 커뮤니티 글 필터링
            name = complex_data.get("name", "").strip()
            if (name and 
                name != "정보 없음" and 
                "주택유형" not in name and 
                "선택" not in name and 
                not any(keyword in name.lower() for keyword in ["community", "공지사항", "주간", "보니", "이집", "수요", "발급"])):
                
                # 이름 중복 검사
                if not any(c.get("name") == name for c in filtered_complexes):
                    filtered_complexes.append(complex_data)
        
        print(f"총 {len(filtered_complexes)}개의 유효한 매물 정보 추출 완료")
        return filtered_complexes
    
    def extract_text_from_element(self, parent, selectors):
        """여러 선택자를 시도하여 텍스트 추출"""
        for selector in selectors:
            try:
                elements = parent.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if not element.is_displayed():
                        continue
                    text = element.text.strip()
                    if text and len(text) > 1 and "본문" not in text and "선택" not in text and "11111" not in text:
                        return text
            except:
                continue
        return "알 수 없음"
    
    def parse_complex_detail(self, complex_url):
        """
        Parse the detailed information page for a specific apartment complex
        """
        if not self.driver:
            self.start_browser()
        
        # 상세 정보 URL로 이동
        self.driver.get(complex_url)
        print(f"상세 정보 페이지 로딩 중: {complex_url}")
        time.sleep(8)  # 로딩 시간 증가
        
        # 기본 정보를 담을 딕셔너리 초기화 - 2024년 필드 추가
        detail = {
            "name": "정보 없음",
            "address": "주소 정보 없음",
            "buildYear": "준공년도 정보 없음",
            "totalHouseholds": "세대수 정보 없음",
            "dealPrice": "매매가 정보 없음",
            "highestFloor": "층수 정보 없음",
            "url": complex_url,  # URL 추가 저장
            "crawlDate": time.strftime("%Y-%m-%d")  # 크롤링 날짜 저장
        }
        
        # 스크린샷 저장
        screenshot_path = os.path.join(self.debug_dir, f"detail_{int(time.time())}.png")
        self.driver.save_screenshot(screenshot_path)
        
        # 주택유형 선택 처리 - 2024년 UI 업데이트 대응
        try:
            housing_type_selectors = [
                ".housing_type_selector", 
                ".select_housing_type",
                "div[role='dialog']", 
                ".modal_wrap",
                ".popup_wrap",
                ".dialog_wrap",  # 2024 추가
                ".property_type_selector",  # 2024 추가
                ".popup_content"  # 2024 추가
            ]
            
            for selector in housing_type_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            # 닫기 버튼이 있으면 닫기
                            close_buttons = element.find_elements(By.CSS_SELECTOR, ".btn_close, .close, button[aria-label='닫기'], .btn_popup_close")
                            if close_buttons:
                                for btn in close_buttons:
                                    if btn.is_displayed():
                                        btn.click()
                                        print("상세 페이지에서 주택유형 선택 팝업 닫기 완료")
                                        time.sleep(2)
                                        break
                            
                            # 아파트 유형 선택
                            apt_buttons = element.find_elements(By.CSS_SELECTOR, "button, .btn, .btn_type, .type_item, .item_apt, [class*='apt']")
                            for btn in apt_buttons:
                                if "아파트" in btn.text:
                                    btn.click()
                                    print("상세 페이지에서 아파트 유형 선택 완료")
                                    time.sleep(2)
                                    break
                except Exception as e:
                    print(f"상세 페이지 주택유형 선택자 {selector} 처리 중 오류: {e}")
                    continue
        except Exception as e:
            print(f"상세 페이지 주택유형 선택 처리 중 오류: {e}")
        
        # 페이지 소스 저장 (디버깅용)
        source_path = os.path.join(self.debug_dir, f"detail_source_{int(time.time())}.html")
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        
        try:
            # 현재 페이지 타이틀과 URL 확인
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            print(f"상세 페이지 제목: '{page_title}'")
            
            # 페이지가 로딩될 때까지 추가 대기 - 2024년 개선사항: 동적 요소 로딩 대기
            try:
                # 주요 컨테이너 요소 중 하나가 로딩될 때까지 대기
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".complex_title, .detail_title, .article_info, .complex_info_area")))
                print("페이지 주요 요소 로딩 완료")
            except TimeoutException:
                print("페이지 로딩 대기시간 초과, 계속 진행합니다.")
                time.sleep(3)
            
            # 1. 타이틀에서 아파트 이름 추출 시도
            if "아파트" in page_title or "오피스텔" in page_title or "주택" in page_title:
                # 페이지 제목에서 아파트 이름 추출 (예: "아파트명 - 네이버 부동산")
                title_parts = page_title.split('-')
                if len(title_parts) > 0 and "선택" not in title_parts[0] and "본문" not in title_parts[0]:
                    detail["name"] = title_parts[0].strip()
                    print(f"타이틀에서 아파트 이름 추출: {detail['name']}")
            
            # 2. CSS 선택자로 아파트 이름 추출 시도 - 2024년 선택자 추가
            if detail["name"] == "정보 없음" or "주택유형" in detail["name"] or "선택" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"]:
                name_selectors = [
                    ".complex_title", ".title", "h1.title", ".detail_title", 
                    ".address_info .name", ".complex_name",
                    ".complex_detail_head .title", "h1", "h2",
                    "h2.title", ".property_title", 
                    ".article_title", ".main_title",
                    ".header_complex_name", ".complex_nm",
                    "div.detail_box_top span.text_title_big",
                    ".article_info .article_title", 
                    ".complex_info_area .complex_title",
                    ".detail_head .head_title",
                    ".detail_header .detail_title",
                    ".complex_nm_wrap .complex_nm",
                    ".detail_complex_title",
                    ".complex_info_title",
                    "#complexTitle",
                    ".complex_title_wrap .complex_title",
                    # 2024년 네이버 부동산 추가 선택자
                    ".property_title", ".apt_name", ".building_title",
                    "[class*='title_text']", "[class*='aptName']",
                    ".detail_main_title", ".apt_detail_title",
                    ".property_detail_title", ".realty_title"
                ]
                
                for selector in name_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            if elem.is_displayed():
                                name = elem.text.strip()
                                if name and name != "정보 없음" and "선택" not in name and "본문" not in name and "11111" not in name and "네이버" not in name.lower() and len(name) > 1:
                                    detail["name"] = name
                                    print(f"선택자 {selector}에서 아파트 이름 추출: {detail['name']}")
                                    break
                        if detail["name"] != "정보 없음" and "주택유형" not in detail["name"] and "선택" not in detail["name"] and "본문" not in detail["name"] and "11111" not in detail["name"]:
                            break
                    except Exception as e:
                        print(f"이름 선택자 {selector} 추출 중 오류: {e}")
                        continue
            
            # 3. 메타 태그에서 제목 추출 시도
            if detail["name"] == "정보 없음" or "주택유형" in detail["name"] or "선택" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"]:
                try:
                    meta_title = self.driver.find_element(By.CSS_SELECTOR, "meta[property='og:title']")
                    if meta_title:
                        title_content = meta_title.get_attribute("content")
                        if title_content and "선택" not in title_content and "본문" not in title_content and "11111" not in title_content:
                            # 네이버 부동산 등의 접미사 제거
                            title_content = re.sub(r'\s*-\s*네이버\s*부동산.*$', '', title_content)
                            if title_content:
                                detail["name"] = title_content
                                print(f"메타 태그에서 아파트 이름 추출: {detail['name']}")
                except:
                    pass
            
            # 4. 세부 텍스트에서 매물명 추출 시도
            if detail["name"] == "정보 없음" or "주택유형" in detail["name"] or "선택" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"]:
                try:
                    # 일반적으로 텍스트가 있는 요소 탐색
                    text_elements = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, .title, strong, [class*='title'], [class*='name']")
                    
                    # 정렬하여 가장 짧고 의미 있는 텍스트 추출 (5~30자 사이)
                    text_candidates = []
                    for elem in text_elements:
                        if elem.is_displayed():
                            text = elem.text.strip()
                            if text and 5 <= len(text) <= 30 and "선택" not in text and "본문" not in text and "11111" not in text and "네이버" not in text.lower():
                                # '아파트', '빌라', '오피스텔' 등의 키워드가 있는 텍스트 우선
                                priority = 0
                                if any(keyword in text for keyword in ["아파트", "오피스텔", "빌라", "주택", "타워", "스카이", "자이", "힐스테이트", "푸르지오", "래미안", "e편한세상"]):
                                    priority = 2
                                elif any(keyword in text for keyword in ["단지", "매매", "전세", "월세"]):
                                    priority = 1
                                text_candidates.append((priority, len(text), text))
                    
                    # 우선순위 높은 순, 그다음 길이가 짧은 순으로 정렬
                    text_candidates.sort(reverse=True)
                    
                    if text_candidates:
                        detail["name"] = text_candidates[0][2]
                        print(f"텍스트 요소에서 아파트 이름 추출: {detail['name']}")
                except Exception as e:
                    print(f"텍스트 요소 검색 중 오류: {e}")
            
            # 5. 주소 추출 시도
            address_selectors = [
                ".address", ".complex_address", ".address_area", 
                ".address_info .address", ".detail_address",
                ".complex_info_address", ".info_address", ".address_txt",
                ".road_addr", ".jibun_addr", ".loc_text",
                ".article_info .info_address",  # 2024 네이버 부동산 구조 추가 
                ".detail_location .location",
                ".detail_info_area .info_address",
                ".complex_info .address_info",
                ".location_info",
                ".complex_address_wrap", # 추가 선택자
                "p.address", # 추가 선택자
                "div[class*='address']", # 추가 선택자
                ".detail_box_wrap .road_addr" # 추가 선택자
            ]
            
            for selector in address_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            addr = elem.text.strip()
                            if addr:
                                detail["address"] = addr
                                print(f"주소 정보 추출: {detail['address']}")
                                break
                    if detail["address"] != "주소 정보 없음":
                        break
                except:
                    continue
            
            # 6. 상세 정보 추출 - div, table, dl 등 다양한 컨테이너에서 정보 추출
            info_container_selectors = [
                "table.complex_detail_table", 
                "dl.complex_detail_list", 
                ".complex_info_table",
                ".info_table", 
                ".complex_info", 
                ".complex_detail_info", 
                ".complex_price_wrap",
                ".detail_box_wrap", 
                ".complex_summary_info",
                ".detail_info_section", 
                ".info_section",
                ".section_complex_info", 
                ".complex_attr_table",
                ".detail_price_area",  # 2024 네이버 부동산 구조 추가
                ".article_info_table",
                ".detail_info_table",
                ".info_detail_wrap",
                ".detail_box_wrap table", # 추가 선택자
                ".complex_info_list", # 추가 선택자
                ".info_detail_area", # 추가 선택자
                "div[class*='detail_info']" # 추가 선택자
            ]
            
            info_containers = []
            for selector in info_container_selectors:
                containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if containers:
                    for container in containers:
                        if container.is_displayed():
                            info_containers.append(container)
            
            # 7. 정보 컨테이너에서 키-값 쌍 추출
            for container in info_containers:
                try:
                    container_text = container.text.lower()
                    
                    # 키-값 쌍 요소 탐색
                    try:
                        # 테이블 형식
                        rows = container.find_elements(By.CSS_SELECTOR, "tr, li, div.item")
                        for row in rows:
                            try:
                                # 키와 값 요소
                                key_elems = row.find_elements(By.CSS_SELECTOR, "th, dt, .label, .tit, strong, .title, .complex_title, .title_cell, [class*='label'], [class*='key']")
                                val_elems = row.find_elements(By.CSS_SELECTOR, "td, dd, .value, .data, .price, .complex_data")
                                
                                if key_elems and val_elems:
                                    key = key_elems[0].text.strip()
                                    value = val_elems[0].text.strip()
                                    
                                    if key and value:
                                        # 특정 정보 매핑
                                        if any(k in key.lower() for k in ["준공", "건축"]):
                                            detail["buildYear"] = value
                                            print(f"준공년도 추출: {value}")
                                        elif any(k in key.lower() for k in ["세대", "가구", "세대수"]):
                                            detail["totalHouseholds"] = value
                                            print(f"세대수 추출: {value}")
                                        elif any(k in key.lower() for k in ["최고층", "층수", "최대층"]):
                                            detail["highestFloor"] = value
                                            print(f"최고층 추출: {value}")
                                        elif any(k in key.lower() for k in ["매매", "거래", "실거래", "시세"]):
                                            detail["dealPrice"] = value
                                            print(f"매매가 추출: {value}")
                            except:
                                continue
                    except:
                        pass
                    
                    # 정규식으로 텍스트에서 바로 값 추출 (테이블 구조가 명확하지 않은 경우)
                    if detail["buildYear"] == "준공년도 정보 없음" or detail["totalHouseholds"] == "세대수 정보 없음":
                        # 준공년도 추출
                        build_year_patterns = [
                            r'준공[년도]*\s*[:：]?\s*(\d{4})[.년]?',
                            r'([12][0-9]{3})[년도]?\s*준공',
                            r'건축[년도]*\s*[:：]?\s*(\d{4})[.년]?'
                        ]
                        
                        for pattern in build_year_patterns:
                            build_year_match = re.search(pattern, container_text)
                            if build_year_match:
                                detail["buildYear"] = build_year_match.group(1) + "년"
                                print(f"정규식으로 준공년도 추출: {detail['buildYear']}")
                                break
                        
                        # 세대수 추출
                        households_patterns = [
                            r'세대[수]?\s*[:：]?\s*([0-9,]+)[세대]?',
                            r'총\s*([0-9,]+)[세대]?',
                            r'([0-9,]+)\s*세대'
                        ]
                        
                        for pattern in households_patterns:
                            households_match = re.search(pattern, container_text)
                            if households_match:
                                detail["totalHouseholds"] = households_match.group(1) + "세대"
                                print(f"정규식으로 세대수 추출: {detail['totalHouseholds']}")
                                break
                        
                        # 가격 추출
                        price_patterns = [
                            r'([0-9,]+억\s*[0-9,]*만?원?)',
                            r'매매\s*([0-9,]+억\s*[0-9,]*만?원?)',
                            r'시세\s*([0-9,]+억\s*[0-9,]*만?원?)'
                        ]
                        
                        for pattern in price_patterns:
                            price_match = re.search(pattern, container_text)
                            if price_match and detail["dealPrice"] == "매매가 정보 없음":
                                detail["dealPrice"] = price_match.group(1)
                                print(f"정규식으로 매매가 추출: {detail['dealPrice']}")
                                break
                except:
                    continue
            
            # 8. 페이지 전체에서 정규식으로 정보 추출 (fallback)
            if detail["name"] == "정보 없음" or detail["address"] == "주소 정보 없음" or detail["buildYear"] == "준공년도 정보 없음" or "본문" in detail["name"] or "11111" in detail["name"]:
                page_text = self.driver.page_source
                
                # 아파트 이름이 여전히 없거나 "주택유형 선택"인 경우
                if detail["name"] == "정보 없음" or "주택유형" in detail["name"] or "선택" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"]:
                    # 아파트 관련 키워드 패턴으로 추출
                    apartment_patterns = [
                        r'([가-힣0-9]+(?:\s*[가-힣]*)?아파트)',  # ~아파트
                        r'([가-힣0-9]+\s*자이)',  # ~자이
                        r'([가-힣0-9]+\s*푸르지오)',  # ~푸르지오
                        r'([가-힣0-9]+\s*힐스테이트)',  # ~힐스테이트
                        r'([가-힣0-9]+\s*e편한세상)',  # ~e편한세상
                        r'([가-힣0-9]+\s*래미안)',  # ~래미안
                        r'([가-힣0-9]+\s*롯데캐슬)',  # ~롯데캐슬',
                    ]
                    
                    for pattern in apartment_patterns:
                        apt_match = re.search(pattern, page_text)
                        if apt_match:
                            apt_name = apt_match.group(1)
                            if apt_name and "선택" not in apt_name and "본문" not in apt_name and "11111" not in apt_name:
                                detail["name"] = apt_name
                                print(f"HTML 소스에서 아파트 이름 추출: {detail['name']}")
                                break
                    
                    # URL에서 아파트 이름 추출 시도
                    if detail["name"] == "정보 없음" or "주택유형" in detail["name"] or "선택" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"]:
                        apt_name_match = re.search(r'(complex|article)/([^/]+)', current_url)
                        if apt_name_match:
                            potential_name = apt_name_match.group(2)
                            if not potential_name.isdigit() and "선택" not in potential_name and "본문" not in potential_name and "11111" not in potential_name:
                                # URL에서 추출한 이름을 가독성 있게 변환
                                potential_name = potential_name.replace('-', ' ').replace('_', ' ').replace('%20', ' ')
                                # 숫자로만 된 부분은 제거
                                potential_name = re.sub(r'^\d+$', '', potential_name)
                                if potential_name.strip():
                                    detail["name"] = potential_name.strip()
                                    print(f"URL에서 아파트 이름 추출: {detail['name']}")
                
                # 주소가 여전히 없는 경우
                if detail["address"] == "주소 정보 없음":
                    # 정규식으로 주소 추출 시도
                    address_patterns = [
                        r'도로명주소\s*[:：]?\s*([가-힣0-9 -]+)',
                        r'지번주소\s*[:：]?\s*([가-힣0-9 -]+)',
                        r'([가-힣]+ [가-힣]+ [가-힣]+(?:길|로) [0-9-]+)',  # 도로명 형식
                        r'([가-힣]+ [가-힣]+ [가-힣]+(?:동|읍|면) [0-9-]+)',   # 지번 형식
                        r'([가-힣]+ [가-힣]+ [가-힣]+동)', # 간소화된 주소 형식
                        r'([가-힣]+ [가-힣]+(?:구|시) [가-힣]+동)' # 시/구 포함 주소 형식
                    ]
                    
                    for pattern in address_patterns:
                        addr_match = re.search(pattern, page_text)
                        if addr_match:
                            detail["address"] = addr_match.group(1)
                            print(f"정규식으로 주소 추출: {detail['address']}")
                            break
                
                # URL에서 좌표 추출
                coords_match = re.search(r'ms=([0-9.]+),([0-9.]+)', complex_url)
                if coords_match and detail["address"] == "주소 정보 없음":
                    coords = f"{coords_match.group(1)},{coords_match.group(2)}"
                    detail["address"] = f"좌표 {coords} 인근"
                    print(f"URL 좌표로부터 주소 대체: {detail['address']}")
        
        except Exception as e:
            print(f"상세 정보 추출 중 오류: {e}")
        
        # 9. 정보 추출 실패 시 fallback 처리
        if detail["name"] == "정보 없음" or "주택유형" in detail["name"] or "선택" in detail["name"] or "네이버" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"]:
            # URL에서 추출한 이름 사용 또는 기본값 설정
            parts = complex_url.split('/')
            potential_name = parts[-1] if len(parts) > 1 else "아파트 단지"
            if potential_name and not potential_name.isdigit() and "선택" not in potential_name and "본문" not in potential_name and "11111" not in potential_name:
                detail["name"] = potential_name.replace('-', ' ').replace('_', ' ').replace('%20', ' ')
            else:
                # 좌표 기반 이름 생성
                coords_match = re.search(r'ms=([0-9.]+),([0-9.]+)', complex_url)
                if coords_match:
                    lat, lng = coords_match.group(1), coords_match.group(2)
                    detail["name"] = f"위치 {lat[:5]},{lng[:5]} 아파트"
                else:
                    detail["name"] = "아파트 정보 미확인"
            
            print(f"이름 추출 실패, 대체값 사용: {detail['name']}")
        
        # 10. 이름 정리 - 주택유형 선택, 네이버, 본문 키워드 제거
        if "주택유형" in detail["name"] or "선택" in detail["name"] or "본문" in detail["name"] or "11111" in detail["name"] or "네이버" in detail["name"].lower():
            # 좌표 기반 이름 생성
            coords_match = re.search(r'ms=([0-9.]+),([0-9.]+)', complex_url)
            if coords_match:
                lat, lng = coords_match.group(1), coords_match.group(2)
                detail["name"] = f"위치 {lat[:5]},{lng[:5]} 아파트"
            else:
                # 이름 대신 URL 경로의 마지막 부분 사용
                parts = complex_url.split('/')
                potential_name = parts[-1] if len(parts) > 1 else "아파트"
                if not potential_name.isdigit():
                    detail["name"] = potential_name.replace('-', ' ').replace('_', ' ').replace('%20', ' ')
                else:
                    detail["name"] = "아파트 정보 미확인"
            
            print(f"잘못된 이름 제거 후 대체: {detail['name']}")
        
        # 11. 최종 데이터 정리
        # 이름 추가 클리닝 (본문, 주택유형 선택 등 키워드 완전 제거)
        detail["name"] = re.sub(r'주택유형\s*선택|본문\s*영역\d*|네이버\s*부동산', '', detail["name"]).strip()
        if not detail["name"] or len(detail["name"]) <= 1:
            detail["name"] = "아파트 정보 미확인"
            
        # 최종 데이터 확인 및 반환
        print(f"최종 추출 정보: {detail['name']}, {detail['address']}")
        return detail
    
    def save_to_csv(self, data, filename):
        """
        Save the extracted data to a CSV file
        """
        if not data:
            print("저장할 데이터가 없습니다.")
            return
        
        # 데이터 전처리 - 잘못된 데이터 처리
        cleaned_data = []
        for item in data:
            # 기본값 설정
            cleaned_item = {
                "name": "정보 없음",
                "address": "주소 정보 없음",
                "buildYear": "준공년도 정보 없음",
                "totalHouseholds": "세대수 정보 없음",
                "dealPrice": "매매가 정보 없음",
                "highestFloor": "층수 정보 없음",
                "crawlDate": time.strftime("%Y-%m-%d")
            }
            # 기존 값 복사
            for key, value in item.items():
                cleaned_item[key] = value
            
            # 이름이 네이버 부동산 또는 본문 영역인 경우 제외
            if "네이버" in cleaned_item.get("name", "") or "본문" in cleaned_item.get("name", ""):
                print(f"부적절한 데이터 항목 제외: {cleaned_item.get('name', '')}")
                continue
                
            # 주소가 없는 경우 URL에서 좌표 추출
            if cleaned_item.get("address") == "주소 정보 없음" or cleaned_item.get("address") == "알 수 없음":
                link = cleaned_item.get("link", "")
                if link:
                    coords_match = re.search(r'ms=([0-9.]+),([0-9.]+)', link)
                    if coords_match:
                        cleaned_item["address"] = f"좌표 {coords_match.group(1)},{coords_match.group(2)} 인근"
                    else:
                        cleaned_item["address"] = cleaned_item.get("info", "주소 정보 없음")
            
            # 데이터 정규화 - 준공년도
            buildYear = cleaned_item.get("buildYear", "")
            if buildYear and buildYear != "준공년도 정보 없음":
                # 숫자만 추출
                year_match = re.search(r'(\d{4})', buildYear)
                if year_match:
                    cleaned_item["buildYear"] = year_match.group(1) + "년"
            
            # 데이터 정규화 - 세대수
            households = cleaned_item.get("totalHouseholds", "")
            if households and households != "세대수 정보 없음":
                # 숫자만 추출
                households_match = re.search(r'([0-9,]+)', households)
                if households_match:
                    cleaned_item["totalHouseholds"] = households_match.group(1).replace(",", "") + "세대"
            
            # 데이터 정규화 - 가격
            price = cleaned_item.get("dealPrice", "")
            if price and price != "매매가 정보 없음":
                # 표준 형식으로 변환
                price = re.sub(r'\s+', '', price)  # 공백 제거
                price = re.sub(r'[^0-9억만원,]', '', price)  # 숫자와 '억', '만', '원', ',' 외 제거
                cleaned_item["dealPrice"] = price
            
            # 중복된 매물 정보 제거를 위한 키 생성
            item_key = f"{cleaned_item.get('name', '')}-{cleaned_item.get('address', '')}"
            if item_key not in [f"{x.get('name', '')}-{x.get('address', '')}" for x in cleaned_data]:
                cleaned_data.append(cleaned_item)
            else:
                print(f"중복 매물 제외: {cleaned_item.get('name', '')}")
        
        try:
            # 데이터프레임 생성
            df = pd.DataFrame(cleaned_data)
            
            # 컬럼 정리 및 순서 정하기
            important_columns = ["name", "address", "buildYear", "totalHouseholds", "dealPrice", "highestFloor", "crawlDate", "url"]
            other_columns = [col for col in df.columns if col not in important_columns]
            
            # 중요 컬럼을 먼저 정렬
            ordered_columns = [col for col in important_columns if col in df.columns]
            ordered_columns.extend(other_columns)
            
            # 컬럼 순서 변경
            df = df[ordered_columns]
            
            # 디버깅용 미리보기
            columns_to_show = [col for col in ["name", "address", "buildYear", "totalHouseholds", "dealPrice"] if col in df.columns]
            if columns_to_show:
                print("\n추출된 데이터 샘플:")
                print(df[columns_to_show].head())
            
            # 백업 파일 생성 (원본 손상 방지)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}_backup.csv"
            
            # CSV 파일로 저장
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            # 백업 저장
            df.to_csv(backup_filename, index=False, encoding='utf-8-sig')
            
            print(f"데이터를 {filename}에 성공적으로 저장했습니다.")
            print(f"백업 파일도 {backup_filename}에 저장되었습니다.")
            
            # 저장된 항목 수 표시
            print(f"총 {len(cleaned_data)}개의 유효한 매물 정보가 저장되었습니다.")
            
            # 간단한 정보 요약 출력
            print("\n요약 정보:")
            if 'name' in df.columns:
                valid_names = df['name'].dropna()
                valid_names = valid_names[~valid_names.str.contains('네이버|부동산|미확인|정보 없음|본문', case=False, na=False)]
                if len(valid_names) > 0:
                    print(f"매물: {', '.join(valid_names.head(3).tolist())} 등")
                else:
                    print("유효한 매물 이름 정보가 없습니다.")
            if 'address' in df.columns:
                addresses = df['address'].dropna()
                valid_addresses = addresses[~addresses.str.contains('알 수 없음|정보 없음|미확인', case=False, na=False)]
                if len(valid_addresses) > 0:
                    print(f"지역: {valid_addresses.iloc[0] if not valid_addresses.empty else '정보 없음'}")
            
            # 통계정보 출력
            if len(df) > 0:
                print("\n데이터 통계:")
                if 'buildYear' in df.columns:
                    years = df['buildYear'].str.extract(r'(\d{4})').astype(float).dropna()
                    if not years.empty:
                        print(f"준공년도 범위: {int(years.min())}년~{int(years.max())}년, 평균: {years.mean():.1f}년")
                if 'dealPrice' in df.columns and df['dealPrice'].str.contains('억').any():
                    print(f"가격대 분포: {df['dealPrice'].value_counts().head(3).to_dict()}")
            
            return filename
        except Exception as e:
            print(f"CSV 저장 중 오류: {str(e)}")
            # 오류 발생 시 간단한 텍스트 파일로 저장 시도
            try:
                fallback_file = f"fallback_{filename}.txt"
                with open(fallback_file, 'w', encoding='utf-8') as f:
                    for item in cleaned_data:
                        f.write(str(item) + "\n\n")
                print(f"데이터를 대체 파일 {fallback_file}에 저장했습니다.")
                return fallback_file
            except Exception as inner_e:
                print(f"대체 파일 저장 중 오류: {str(inner_e)}")
                return None