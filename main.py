from naver_estate_crawling import NaverEstateCrawler
import time
import os
import pandas as pd
import re
import sys
from datetime import datetime

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

def main():
    # 디버그 로그 디렉토리 생성
    os.makedirs("debug_logs", exist_ok=True)
    
    # 크롤러 초기화
    crawler = NaverEstateCrawler(headless=False)
    
    try:
        print("네이버 부동산 매물 검색 프로그램\n")
        print("1. 지역 카테고리별 검색 (전국 모든 지역)")
        print("2. 직접 지역명 입력 (모든 지역 검색)")
        print("3. 전국 주요 지역 검색")
        print("4. 특정 URL로 검색 (주택유형, 거래방식 선택)")
        choice = input("\n원하는 옵션을 선택하세요 (1-4): ")
        
        # 주택유형과 거래방식 선택 (옵션 4일 때만 필수, 나머지는 선택사항)
        housing_type_code = "APT"  # 기본값: 아파트
        trade_type_code = "RETAIL"  # 기본값: 매매
        
        if choice == "4" or input("\n주택유형과 거래방식을 선택하시겠습니까? (y/n): ").lower() == 'y':
            # 주택유형 선택
            print("\n주택유형 선택:")
            for key, value in HOUSING_TYPES.items():
                print(f"{key}. {value['name']}")
            
            housing_choice = input("\n주택유형 번호를 선택하세요: ")
            if housing_choice in HOUSING_TYPES:
                housing_type_code = HOUSING_TYPES[housing_choice]["code"]
                print(f"선택한 주택유형: {HOUSING_TYPES[housing_choice]['name']}")
            else:
                print(f"잘못된 선택입니다. 기본값(아파트)으로 설정합니다.")
            
            # 거래방식 선택
            print("\n거래방식 선택:")
            for key, value in TRADE_TYPES.items():
                print(f"{key}. {value['name']}")
            
            trade_choice = input("\n거래방식 번호를 선택하세요: ")
            if trade_choice in TRADE_TYPES:
                trade_type_code = TRADE_TYPES[trade_choice]["code"]
                print(f"선택한 거래방식: {TRADE_TYPES[trade_choice]['name']}")
            else:
                print(f"잘못된 선택입니다. 기본값(매매)으로 설정합니다.")
        
        # 사용자로부터 최대 추출 매물 수 입력 받기
        max_limit_input = input("\n최대 추출할 매물 수를 입력하세요 (전체 추출은 0 입력): ")
        try:
            max_limit = int(max_limit_input)
            if max_limit < 0:
                max_limit = 0
                print("[알림] 음수 입력으로 인해 전체 매물을 추출합니다.")
        except ValueError:
            max_limit = 0
            print("[알림] 유효하지 않은 입력으로 인해 전체 매물을 추출합니다.")
        
        if max_limit == 0:
            print("[알림] 전체 매물을 추출합니다.")
        else:
            print(f"[알림] 최대 {max_limit}개 매물을 추출합니다.")
        
        if choice == "1":
            # 카테고리별 지역 선택
            print("\n지역 카테고리를 선택하세요:")
            categories = list(REGIONS_BY_CATEGORY.keys())
            
            for i, category in enumerate(categories):
                region_count = len(REGIONS_BY_CATEGORY[category])
                print(f"{i+1}. {category} ({region_count}개 지역)")
            
            category_choice = int(input(f"\n카테고리 번호를 입력하세요 (1-{len(categories)}): ")) - 1
            
            if 0 <= category_choice < len(categories):
                selected_category = categories[category_choice]
                regions_in_category = REGIONS_BY_CATEGORY[selected_category]
                
                print(f"\n{selected_category} 내 지역 목록:")
                for i, region in enumerate(regions_in_category):
                    print(f"{i+1}. {region['name']}")
                
                region_choice = int(input(f"\n검색할 지역 번호를 입력하세요 (1-{len(regions_in_category)}): ")) - 1
                
                if 0 <= region_choice < len(regions_in_category):
                    selected_region = regions_in_category[region_choice]
                    region_name = selected_region['name']
                    region_url = selected_region['url']
                    
                    # URL에 주택유형과 거래방식 적용
                    region_url = update_url_with_filters(region_url, housing_type_code, trade_type_code)
                    
                    # 파일명 생성 (공백 및 특수문자 제거)
                    safe_region = ''.join(c for c in region_name if c.isalnum() or c.isspace()).strip().replace(' ', '_')
                    filename = f"{safe_region}_매물정보.csv"
                    
                    print(f"\n'{region_name}' 지역의 매물 정보를 검색합니다...\n")
                    
                    # 해당 지역의 매물 목록 가져오기
                    complexes = crawler.parse_complex_list(region_url)
                    print(f"\n검색된 총 {len(complexes)}개의 매물 목록:")
                    for i, complex_data in enumerate(complexes):
                        print(f"[{i+1}] {complex_data['name']}")
                    
                    # 추출할 매물 수 결정
                    if max_limit > 0:
                        complexes_to_process = complexes[:max_limit]
                        print(f"사용자 설정에 따라 최대 {max_limit}개 매물만 추출합니다.")
                    else:
                        complexes_to_process = complexes
                        print(f"모든 매물 ({len(complexes)}개)을 추출합니다.")
                    
                    # 상세 정보 목록
                    details = []
                    
                    # 모든 매물 정보 가져오기
                    for i, complex_data in enumerate(complexes_to_process):
                        print(f"[{i+1}/{len(complexes_to_process)}] '{complex_data['name']}' 상세 정보 수집 중...")
                        detail = crawler.parse_complex_detail(complex_data['link'])
                        details.append(detail)
                        time.sleep(1.5)  # 과도한 요청 방지
                    
                    # 데이터 저장
                    saved_file = crawler.save_to_csv(details, filename)
                    
                    # 저장 위치 출력
                    if saved_file:
                        full_path = os.path.abspath(saved_file)
                        print(f"\n파일이 다음 경로에 저장되었습니다: {full_path}")
                else:
                    print("잘못된 지역 번호를 입력했습니다.")
            else:
                print("잘못된 카테고리 번호를 입력했습니다.")
                
        elif choice == "2":
            # 직접 지역명 입력 (검색 API 사용)
            region = input("\n검색할 지역명을 입력하세요 (예: 강남구 압구정동, 서초구 반포동, 전주시 덕진구): ")
            
            # 파일명 생성 (공백 및 특수문자 제거)
            safe_region = ''.join(c for c in region if c.isalnum() or c.isspace()).strip().replace(' ', '_')
            filename = f"{safe_region}_매물정보.csv"
            
            print(f"\n'{region}' 지역의 매물 정보를 검색합니다...\n")
            
            # 지역 검색 및 URL 획득
            url = crawler.search_region(region)
            
            # URL에 주택유형과 거래방식 적용
            url = update_url_with_filters(url, housing_type_code, trade_type_code)
            
            # 해당 지역의 매물 목록 가져오기
            complexes = crawler.parse_complex_list(url)
            print(f"\n검색된 총 {len(complexes)}개의 매물 목록:")
            for i, complex_data in enumerate(complexes):
                print(f"[{i+1}] {complex_data['name']}")
            
            # 추출할 매물 수 결정
            if max_limit > 0:
                complexes_to_process = complexes[:max_limit]
                print(f"사용자 설정에 따라 최대 {max_limit}개 매물만 추출합니다.")
            else:
                complexes_to_process = complexes
                print(f"모든 매물 ({len(complexes)}개)을 추출합니다.")
            
            # 상세 정보 목록
            details = []
            
            # 모든 매물 정보 가져오기
            for i, complex_data in enumerate(complexes_to_process):
                print(f"[{i+1}/{len(complexes_to_process)}] '{complex_data['name']}' 상세 정보 수집 중...")
                detail = crawler.parse_complex_detail(complex_data['link'])
                details.append(detail)
                time.sleep(1.5)  # 과도한 요청 방지
            
            # 데이터 저장
            saved_file = crawler.save_to_csv(details, filename)
            
            # 저장 위치 출력
            if saved_file:
                full_path = os.path.abspath(saved_file)
                print(f"\n파일이 다음 경로에 저장되었습니다: {full_path}")
                
        elif choice == "3":
            # 전국 주요 지역 검색 - 검색 범위 지정
            print("\n검색 범위를 선택하세요:")
            print("1. 서울 지역만 (25개 구)")
            print("2. 주요 광역시만 (6개 광역시)")
            print("3. 모든 지역 (서울, 경기, 광역시, 도청소재지 등)")
            
            range_choice = input("\n검색 범위 번호를 입력하세요 (1-3): ")
            
            # 지역별 추출 매물 수 설정
            articles_per_region_input = input("\n지역당 최대 추출할 매물 수를 입력하세요 (전체 추출은 0 입력): ")
            try:
                articles_per_region = int(articles_per_region_input)
                if articles_per_region < 0:
                    articles_per_region = 0
                    print("[알림] 음수 입력으로 인해 전체 매물을 추출합니다.")
            except ValueError:
                articles_per_region = 0
                print("[알림] 유효하지 않은 입력으로 인해 전체 매물을 추출합니다.")
            
            if articles_per_region == 0:
                print("[알림] 각 지역의 전체 매물을 추출합니다.")
            else:
                print(f"[알림] 지역당 최대 {articles_per_region}개 매물을 추출합니다.")
            
            # 검색할 지역 목록 선택
            search_regions = []
            if range_choice == "1":
                # 서울 지역만
                search_regions = REGIONS_BY_CATEGORY["서울"]
                print(f"\n서울 {len(search_regions)}개 구 검색을 시작합니다.")
            elif range_choice == "2":
                # 광역시만
                search_regions = REGIONS_BY_CATEGORY["광역시"] + REGIONS_BY_CATEGORY["특별자치시/도"]
                print(f"\n{len(search_regions)}개 광역시/특별시 검색을 시작합니다.")
            else:
                # 모든 지역
                search_regions = ALL_REGIONS
                print(f"\n전국 {len(search_regions)}개 지역 검색을 시작합니다.")
            
            print(f"\n검색할 지역 수: {len(search_regions)}개\n")
            
            all_results = []
            successful_regions = []
            failed_regions = []
            
            # 검색 진행률 표시
            for i, region in enumerate(search_regions):
                region_name = region['name']
                region_url = region['url']
                
                # URL에 주택유형과 거래방식 적용
                region_url = update_url_with_filters(region_url, housing_type_code, trade_type_code)
                
                print(f"\n===== [{i+1}/{len(search_regions)}] {region_name} 검색 중... =====")
                
                try:
                    # 해당 지역의 매물 목록 가져오기
                    complexes = crawler.parse_complex_list(region_url)
                    
                    if complexes and len(complexes) > 0:
                        print(f"{len(complexes)}개의 매물을 찾았습니다.")
                        
                        # 최대 매물 수 제한 적용
                        if articles_per_region > 0:
                            max_to_collect = min(len(complexes), articles_per_region)
                            complexes_to_add = complexes[:max_to_collect]
                        else:
                            max_to_collect = len(complexes)
                            complexes_to_add = complexes
                        
                        for j, complex_data in enumerate(complexes_to_add):
                            print(f"[{j+1}/{max_to_collect}] '{complex_data['name']}' 상세 정보 수집 중...")
                            detail = crawler.parse_complex_detail(complex_data['link'])
                            
                            # 지역 정보 추가
                            detail["search_region"] = region_name
                            all_results.append(detail)
                            time.sleep(1.5)  # 과도한 요청 방지
                        
                        successful_regions.append(region_name)
                    else:
                        print(f"{region_name}에서 매물을 찾을 수 없습니다.")
                        failed_regions.append(region_name)
                    
                except Exception as e:
                    print(f"{region_name} 검색 중 오류: {e}")
                    failed_regions.append(region_name)
                
                # 과도한 요청 방지를 위한 대기
                time.sleep(3)
            
            # 전체 결과 저장
            if all_results:
                # 데이터프레임 생성 및 저장
                df = pd.DataFrame(all_results)
                filename = "전국_부동산_매물정보.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                
                full_path = os.path.abspath(filename)
                print(f"\n전국 부동산 매물 정보가 다음 경로에 저장되었습니다: {full_path}")
                print(f"총 {len(all_results)}개의 매물 정보가 저장되었습니다.")
                
                # 요약 정보 출력
                print(f"\n성공적으로 검색된 지역: {len(successful_regions)}개")
                print(f"검색에 실패한 지역: {len(failed_regions)}개")
                
                if failed_regions:
                    print("\n검색에 실패한 지역 목록:")
                    for region_name in failed_regions:
                        print(f"- {region_name}")
            else:
                print("\n검색 결과가 없습니다.")
        
        elif choice == "4":
            # 특정 URL로 검색
            url = input("\n검색할 네이버 부동산 URL을 입력하세요: ")
            if not url.startswith("https://new.land.naver.com"):
                print("네이버 부동산 URL만 입력 가능합니다.")
                return False
            
            # URL에 주택유형과 거래방식 적용
            url = update_url_with_filters(url, housing_type_code, trade_type_code)
            
            print(f"\n입력한 URL로 매물 정보를 검색합니다...\n")
            print(f"적용된 URL: {url}")
            
            # 해당 URL의 매물 목록 가져오기
            complexes = crawler.parse_complex_list(url)
            print(f"\n검색된 총 {len(complexes)}개의 매물 목록:")
            for i, complex_data in enumerate(complexes):
                print(f"[{i+1}] {complex_data['name']}")
            
            # 추출할 매물 수 결정
            if max_limit > 0:
                complexes_to_process = complexes[:max_limit]
                print(f"사용자 설정에 따라 최대 {max_limit}개 매물만 추출합니다.")
            else:
                complexes_to_process = complexes
                print(f"모든 매물 ({len(complexes)}개)을 추출합니다.")
            
            # 상세 정보 목록
            details = []
            
            # 모든 매물 정보 가져오기
            for i, complex_data in enumerate(complexes_to_process):
                print(f"[{i+1}/{len(complexes_to_process)}] '{complex_data['name']}' 상세 정보 수집 중...")
                detail = crawler.parse_complex_detail(complex_data['link'])
                details.append(detail)
                time.sleep(1.5)  # 과도한 요청 방지
            
            # 데이터 저장
            filename = f"네이버부동산_매물정보_{int(time.time())}.csv"
            saved_file = crawler.save_to_csv(details, filename)
            
            # 저장 위치 출력
            if saved_file:
                full_path = os.path.abspath(saved_file)
                print(f"\n파일이 다음 경로에 저장되었습니다: {full_path}")
        
        else:
            print("잘못된 옵션을 선택했습니다.")
        
        return True
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 브라우저 종료
        crawler.close_browser()

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