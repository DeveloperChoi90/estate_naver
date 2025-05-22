from naver_estate_crawling import NaverEstateCrawler
import time
import os
import pandas as pd
import re
import sys
from datetime import datetime
from selenium.webdriver.common.by import By
import urllib.parse

# 전국 지역 데이터 (지역명과 URL) - 카테고리별로 정리
REGIONS_BY_CATEGORY = {
    "서울": [
        {"name": "서울 강남구", "url": "https://new.land.naver.com/complexes?ms=37.5073421,127.0588579,15&a=APT&e=RETAIL"},
        {"name": "서울 서초구", "url": "https://new.land.naver.com/complexes?ms=37.4837121,127.0147000,15&a=APT&e=RETAIL"},
        {"name": "서울 송파구", "url": "https://new.land.naver.com/complexes?ms=37.5048121,127.1144579,15&a=APT&e=RETAIL"},
        {"name": "서울 강동구", "url": "https://new.land.naver.com/complexes?ms=37.5492077,127.1464824,15&a=APT&e=RETAIL"},
        {"name": "서울 마포구", "url": "https://new.land.naver.com/complexes?ms=37.5546788,126.9250539,15&a=APT&e=RETAIL"},
        {"name": "서울 종로구", "url": "https://new.land.naver.com/complexes?ms=37.5728933,126.9793882,15&a=APT&e=RETAIL"},
        {"name": "서울 중구", "url": "https://new.land.naver.com/complexes?ms=37.5634696,126.9975223,15&a=APT&e=RETAIL"},
        {"name": "서울 용산구", "url": "https://new.land.naver.com/complexes?ms=37.5311008,126.9809633,15&a=APT&e=RETAIL"},
        {"name": "서울 성동구", "url": "https://new.land.naver.com/complexes?ms=37.5636557,127.0364335,15&a=APT&e=RETAIL"},
        {"name": "서울 광진구", "url": "https://new.land.naver.com/complexes?ms=37.5384272,127.0821695,15&a=APT&e=RETAIL"},
        {"name": "서울 동대문구", "url": "https://new.land.naver.com/complexes?ms=37.5742905,127.0395918,15&a=APT&e=RETAIL"},
        {"name": "서울 중랑구", "url": "https://new.land.naver.com/complexes?ms=37.6037656,127.0787905,15&a=APT&e=RETAIL"},
        {"name": "서울 성북구", "url": "https://new.land.naver.com/complexes?ms=37.603969,127.0232185,15&a=APT&e=RETAIL"},
        {"name": "서울 강북구", "url": "https://new.land.naver.com/complexes?ms=37.6482897,127.0114557,15&a=APT&e=RETAIL"},
        {"name": "서울 도봉구", "url": "https://new.land.naver.com/complexes?ms=37.6684926,127.0471121,15&a=APT&e=RETAIL"},
        {"name": "서울 노원구", "url": "https://new.land.naver.com/complexes?ms=37.6563149,127.0750347,15&a=APT&e=RETAIL"},
        {"name": "서울 은평구", "url": "https://new.land.naver.com/complexes?ms=37.619002,126.9336479,15&a=APT&e=RETAIL"},
        {"name": "서울 서대문구", "url": "https://new.land.naver.com/complexes?ms=37.577144,126.9559564,15&a=APT&e=RETAIL"},
        {"name": "서울 양천구", "url": "https://new.land.naver.com/complexes?ms=37.5247151,126.8665356,15&a=APT&e=RETAIL"},
        {"name": "서울 강서구", "url": "https://new.land.naver.com/complexes?ms=37.5657576,126.8226501,15&a=APT&e=RETAIL"},
        {"name": "서울 구로구", "url": "https://new.land.naver.com/complexes?ms=37.4954031,126.8874576,15&a=APT&e=RETAIL"},
        {"name": "서울 금천구", "url": "https://new.land.naver.com/complexes?ms=37.4600969,126.9001546,15&a=APT&e=RETAIL"},
        {"name": "서울 영등포구", "url": "https://new.land.naver.com/complexes?ms=37.5265454,126.9095492,15&a=APT&e=RETAIL"},
        {"name": "서울 동작구", "url": "https://new.land.naver.com/complexes?ms=37.4965037,126.9443073,15&a=APT&e=RETAIL"},
        {"name": "서울 관악구", "url": "https://new.land.naver.com/complexes?ms=37.4781549,126.9514847,15&a=APT&e=RETAIL"}
    ],
    "경기도": [
        {"name": "경기도 성남시", "url": "https://new.land.naver.com/complexes?ms=37.4449168,127.1388684,15&a=APT&e=RETAIL"},
        {"name": "경기도 용인시", "url": "https://new.land.naver.com/complexes?ms=37.2410864,127.1574276,15&a=APT&e=RETAIL"},
        {"name": "경기도 수원시", "url": "https://new.land.naver.com/complexes?ms=37.2749785,127.0096295,15&a=APT&e=RETAIL"},
        {"name": "경기도 부천시", "url": "https://new.land.naver.com/complexes?ms=37.5035917,126.7882882,15&a=APT&e=RETAIL"},
        {"name": "경기도 고양시", "url": "https://new.land.naver.com/complexes?ms=37.6583599,126.8320201,15&a=APT&e=RETAIL"},
        {"name": "경기도 안양시", "url": "https://new.land.naver.com/complexes?ms=37.3884559,126.9541475,15&a=APT&e=RETAIL"},
        {"name": "경기도 남양주시", "url": "https://new.land.naver.com/complexes?ms=37.6357645,127.2165139,15&a=APT&e=RETAIL"},
        {"name": "경기도 화성시", "url": "https://new.land.naver.com/complexes?ms=37.1990038,127.1066593,15&a=APT&e=RETAIL"},
        {"name": "경기도 시흥시", "url": "https://new.land.naver.com/complexes?ms=37.3799896,126.8037959,15&a=APT&e=RETAIL"},
        {"name": "경기도 파주시", "url": "https://new.land.naver.com/complexes?ms=37.7680446,126.7780579,15&a=APT&e=RETAIL"},
        {"name": "경기도 의정부시", "url": "https://new.land.naver.com/complexes?ms=37.7407293,127.0477856,15&a=APT&e=RETAIL"},
        {"name": "경기도 김포시", "url": "https://new.land.naver.com/complexes?ms=37.6155311,126.7155962,15&a=APT&e=RETAIL"},
        {"name": "경기도 평택시", "url": "https://new.land.naver.com/complexes?ms=36.9927064,127.1124344,15&a=APT&e=RETAIL"},
        {"name": "경기도 광명시", "url": "https://new.land.naver.com/complexes?ms=37.4785065,126.8644800,15&a=APT&e=RETAIL"},
        {"name": "경기도 광주시", "url": "https://new.land.naver.com/complexes?ms=37.4141111,127.2585898,15&a=APT&e=RETAIL"},
        {"name": "경기도 안산시", "url": "https://new.land.naver.com/complexes?ms=37.3226694,126.8308083,15&a=APT&e=RETAIL"}
    ],
    "광역시": [
        {"name": "부산광역시", "url": "https://new.land.naver.com/complexes?ms=35.1795543,129.0756416,15&a=APT&e=RETAIL"},
        {"name": "인천광역시", "url": "https://new.land.naver.com/complexes?ms=37.4562557,126.7052062,15&a=APT&e=RETAIL"},
        {"name": "대구광역시", "url": "https://new.land.naver.com/complexes?ms=35.8714354,128.6012393,15&a=APT&e=RETAIL"},
        {"name": "대전광역시", "url": "https://new.land.naver.com/complexes?ms=36.3504119,127.3845475,15&a=APT&e=RETAIL"},
        {"name": "광주광역시", "url": "https://new.land.naver.com/complexes?ms=35.1595454,126.8526012,15&a=APT&e=RETAIL"},
        {"name": "울산광역시", "url": "https://new.land.naver.com/complexes?ms=35.5388449,129.3113596,15&a=APT&e=RETAIL"}
    ],
    "특별자치시/도": [
        {"name": "세종특별자치시", "url": "https://new.land.naver.com/complexes?ms=36.5040736,127.2494855,15&a=APT&e=RETAIL"},
        {"name": "제주특별자치도", "url": "https://new.land.naver.com/complexes?ms=33.4996213,126.5311884,15&a=APT&e=RETAIL"}
    ],
    "강원도": [
        {"name": "강원도 춘천시", "url": "https://new.land.naver.com/complexes?ms=37.8856271,127.7342291,15&a=APT&e=RETAIL"},
        {"name": "강원도 원주시", "url": "https://new.land.naver.com/complexes?ms=37.3422186,127.9202491,15&a=APT&e=RETAIL"},
        {"name": "강원도 강릉시", "url": "https://new.land.naver.com/complexes?ms=37.7556468,128.8967813,15&a=APT&e=RETAIL"},
        {"name": "강원도 속초시", "url": "https://new.land.naver.com/complexes?ms=38.2071701,128.5916426,15&a=APT&e=RETAIL"}
    ],
    "충청북도": [
        {"name": "충청북도 청주시", "url": "https://new.land.naver.com/complexes?ms=36.6424187,127.4890444,15&a=APT&e=RETAIL"},
        {"name": "충청북도 충주시", "url": "https://new.land.naver.com/complexes?ms=36.9907272,127.9258050,15&a=APT&e=RETAIL"}
    ],
    "충청남도": [
        {"name": "충청남도 홍성군", "url": "https://new.land.naver.com/complexes?ms=36.6016772,126.6611401,15&a=APT&e=RETAIL"},
        {"name": "충청남도 천안시", "url": "https://new.land.naver.com/complexes?ms=36.8205882,127.1546756,15&a=APT&e=RETAIL"},
        {"name": "충청남도 아산시", "url": "https://new.land.naver.com/complexes?ms=36.7897160,127.0039833,15&a=APT&e=RETAIL"}
    ],
    "전라북도": [
        {"name": "전라북도 전주시", "url": "https://new.land.naver.com/complexes?ms=35.8242238,127.1479532,15&a=APT&e=RETAIL"},
        {"name": "전라북도 익산시", "url": "https://new.land.naver.com/complexes?ms=35.9475394,126.9575991,15&a=APT&e=RETAIL"},
        {"name": "전라북도 군산시", "url": "https://new.land.naver.com/complexes?ms=35.9675997,126.7368831,15&a=APT&e=RETAIL"}
    ],
    "전라남도": [
        {"name": "전라남도 무안군", "url": "https://new.land.naver.com/complexes?ms=34.9917188,126.4789177,15&a=APT&e=RETAIL"},
        {"name": "전라남도 목포시", "url": "https://new.land.naver.com/complexes?ms=34.8118181,126.3921462,15&a=APT&e=RETAIL"},
        {"name": "전라남도 여수시", "url": "https://new.land.naver.com/complexes?ms=34.7604268,127.6622188,15&a=APT&e=RETAIL"},
        {"name": "전라남도 순천시", "url": "https://new.land.naver.com/complexes?ms=34.9504191,127.4874981,15&a=APT&e=RETAIL"}
    ],
    "경상북도": [
        {"name": "경상북도 안동시", "url": "https://new.land.naver.com/complexes?ms=36.5680673,128.7292674,15&a=APT&e=RETAIL"},
        {"name": "경상북도 포항시", "url": "https://new.land.naver.com/complexes?ms=36.0190411,129.3434641,15&a=APT&e=RETAIL"},
        {"name": "경상북도 구미시", "url": "https://new.land.naver.com/complexes?ms=36.1199551,128.3443976,15&a=APT&e=RETAIL"},
        {"name": "경상북도 경주시", "url": "https://new.land.naver.com/complexes?ms=35.8562126,129.2246935,15&a=APT&e=RETAIL"}
    ],
    "경상남도": [
        {"name": "경상남도 창원시", "url": "https://new.land.naver.com/complexes?ms=35.2539903,128.6395211,15&a=APT&e=RETAIL"},
        {"name": "경상남도 김해시", "url": "https://new.land.naver.com/complexes?ms=35.2359782,128.8869124,15&a=APT&e=RETAIL"},
        {"name": "경상남도 진주시", "url": "https://new.land.naver.com/complexes?ms=35.1803151,128.1076351,15&a=APT&e=RETAIL"},
        {"name": "경상남도 통영시", "url": "https://new.land.naver.com/complexes?ms=34.8542093,128.4332745,15&a=APT&e=RETAIL"}
    ]
}

# 주택유형 매핑
HOUSING_TYPES = {
    "1": {"name": "아파트", "code": "APT"},
    "2": {"name": "오피스텔", "code": "OPST"},
    "3": {"name": "빌라/연립", "code": "VL:DDDGG:JGC"},
    "4": {"name": "단독/다가구", "code": "DDDGG"},
    "5": {"name": "원룸", "code": "JWJT"},
    "6": {"name": "상가/사무실", "code": "SGJT:GJCG"},
    "7": {"name": "지식산업센터", "code": "JGC"},
    "8": {"name": "토지", "code": "TJ"},
    "9": {"name": "전체", "code": "APT:OPST:VL:DDDGG:JGC:JWJT:SGJT:GJCG:TJ"}
}

# 거래방식 매핑
TRADE_TYPES = {
    "1": {"name": "매매", "code": "RETAIL"},
    "2": {"name": "전세", "code": "JWSELL"},
    "3": {"name": "월세", "code": "MONTH"},
    "4": {"name": "단기임대", "code": "SHORT"},
    "5": {"name": "전체", "code": "RETAIL:JWSELL:MONTH:SHORT"}
}

# 모든 지역 목록 합치기
ALL_REGIONS = []
for category, regions in REGIONS_BY_CATEGORY.items():
    ALL_REGIONS.extend(regions)

def show_menu():
    print("\n=== 네이버 부동산 크롤러 ===")
    print("1. 지역별 크롤링")
    print("2. 특정 단지 크롤링")
    print("3. 행정구역별 크롤링")
    print("4. 검색어를 통한 크롤링")
    print("0. 종료")
    choice = input("\n작업을 선택하세요: ")
    return choice

def main():
    # 크롤러 초기화
    crawler = NaverEstateCrawler()
    
    # 크롤링할 단지 번호 리스트
    complex_numbers = [
        "123456",  # 예시 단지 번호
        "789012"   # 예시 단지 번호
    ]
    
    all_articles = []
    
    for complex_no in complex_numbers:
        print(f"\n단지 번호 {complex_no} 크롤링 시작...")
        
        # 단지 정보 가져오기
        complex_info = crawler.get_complex_info(complex_no)
        if not complex_info:
            print(f"단지 {complex_no}의 정보를 가져오는데 실패했습니다.")
            continue
            
        # 매물 정보 가져오기
        page = 1
        while True:
            articles_data = crawler.get_complex_articles(complex_no, page)
            if not articles_data or not articles_data.get("articleList"):
                break
                
            for article in articles_data["articleList"]:
                parsed_article = crawler.parse_article_data(article)
                if parsed_article:
                    all_articles.append(parsed_article)
                    
            page += 1
            time.sleep(1)  # API 요청 간 딜레이
            
        print(f"단지 {complex_no} 크롤링 완료")
        
    # 결과 저장
    if all_articles:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"naver_estate_data_{timestamp}.csv"
        crawler.save_to_csv(all_articles, filename)
    else:
        print("크롤링된 매물이 없습니다.")

def update_url_with_filters(url, housing_type, trade_type):
    """URL에 주택유형과 거래방식 필터 적용"""
    # 기존 URL에서 쿼리 파라미터 분리
    if '?' in url:
        base_url, params = url.split('?', 1)
        params_dict = {}
        for param in params.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params_dict[key] = value
    else:
        base_url = url
        params_dict = {}
    
    # 주택유형과 거래방식 파라미터 설정
    params_dict['a'] = housing_type
    params_dict['e'] = trade_type
    
    # 모든 거래 표시
    params_dict['ad'] = 'true'
    
    # 새 URL 구성
    query_params = '&'.join([f"{key}={value}" for key, value in params_dict.items()])
    new_url = f"{base_url}?{query_params}"
    
    return new_url

# 스크립트 실행
if __name__ == "__main__":
    main()