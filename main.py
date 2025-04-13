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
    # 디버그 로그 디렉토리 생성
    debug_dir = "debug_logs"
    os.makedirs(debug_dir, exist_ok=True)
    
    # 결과 저장 디렉토리 생성
    results_dir = "crawl_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 현재 시간 기록
    start_time = time.time()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # 로그 파일 설정
    log_file = os.path.join(debug_dir, f"crawl_log_{timestamp}.txt")
    
    # 크롤러 초기화 - 헤드리스 모드 선택 옵션 추가
    headless_mode = input("헤드리스 모드로 실행할까요? (브라우저 창 숨김) (y/n): ").lower() == 'y'
    print(f"{'헤드리스' if headless_mode else '일반'} 모드로 크롤러를 실행합니다.")
    
    crawler = NaverEstateCrawler(headless=headless_mode)
    
    try:
        while True:
            choice = show_menu()
            
            # 결과 저장 파일에 타임스탬프 추가
            timestamp_short = time.strftime("%m%d_%H%M")
            
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
            
            # 크롤링 시작 메시지 출력
            print(f"\n=== 크롤링 시작: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
            
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
                        filename = os.path.join(results_dir, f"{safe_region}_{timestamp_short}.csv")
                        
                        print(f"\n'{region_name}' 지역의 매물 정보를 검색합니다...\n")
                        
                        # 해당 지역의 매물 목록 가져오기
                        try:
                            complexes = crawler.parse_complex_list(region_url)
                            print(f"\n검색된 총 {len(complexes)}개의 매물 목록:")
                            for i, complex_data in enumerate(complexes[:10]):  # 처음 10개만 출력
                                print(f"[{i+1}] {complex_data['name']}")
                            
                            if len(complexes) > 10:
                                print(f"... 외 {len(complexes) - 10}개")
                            
                            # 추출할 매물 수 결정
                            if max_limit > 0:
                                complexes_to_process = complexes[:max_limit]
                                print(f"사용자 설정에 따라 최대 {max_limit}개 매물만 추출합니다.")
                            else:
                                complexes_to_process = complexes
                                print(f"모든 매물 ({len(complexes)}개)을 추출합니다.")
                            
                            # 상세 정보 목록
                            details = []
                            failed_items = []
                            
                            # 진행상황 표시 및 예외처리 개선
                            for i, complex_data in enumerate(complexes_to_process):
                                try:
                                    print(f"[{i+1}/{len(complexes_to_process)}] '{complex_data['name']}' 상세 정보 수집 중...")
                                    detail = crawler.parse_complex_detail(complex_data['link'])
                                    detail["region"] = region_name  # 지역정보 추가
                                    details.append(detail)
                                    # 성공한 경우 더 짧은 대기 시간 적용
                                    time.sleep(1.5)
                                except Exception as e:
                                    print(f"[오류] '{complex_data['name']}' 상세 정보 수집 실패: {e}")
                                    failed_items.append(complex_data)
                                    # 오류 발생 시 더 긴 대기 시간 적용 (IP 차단 방지)
                                    time.sleep(3)
                            
                            # 실패한 아이템 재시도
                            if failed_items:
                                print(f"\n{len(failed_items)}개의 매물 정보 수집에 실패했습니다. 재시도합니다...")
                                for i, complex_data in enumerate(failed_items):
                                    try:
                                        print(f"[재시도 {i+1}/{len(failed_items)}] '{complex_data['name']}' 상세 정보 수집 중...")
                                        detail = crawler.parse_complex_detail(complex_data['link'])
                                        detail["region"] = region_name
                                        details.append(detail)
                                        time.sleep(2)
                                    except Exception as e:
                                        print(f"[재시도 실패] '{complex_data['name']}' 상세 정보 수집 실패: {e}")
                                        # 실패 로그 남기기
                                        with open(os.path.join(debug_dir, "failed_items.txt"), "a", encoding="utf-8") as f:
                                            f.write(f"{region_name}\t{complex_data['name']}\t{complex_data['link']}\n")
                            
                            # 데이터 저장
                            if details:
                                saved_file = crawler.save_to_csv(details, filename)
                                
                                # 저장 위치 출력
                                if saved_file:
                                    full_path = os.path.abspath(saved_file)
                                    print(f"\n파일이 다음 경로에 저장되었습니다: {full_path}")
                                    print(f"총 {len(details)}개의 매물 정보가 저장되었습니다.")
                            else:
                                print("\n저장할 데이터가 없습니다.")
                        
                        except Exception as e:
                            print(f"\n지역 검색 중 오류 발생: {e}")
                            # 실패 로그에 기록
                            with open(os.path.join(debug_dir, "failed_regions.txt"), "a", encoding="utf-8") as f:
                                f.write(f"{region_name}\t{region_url}\t{str(e)}\n")
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
                # 행정구역별 검색 (시/도/구)
                print("\n행정구역별 검색을 시작합니다.")
                
                # 시/도 목록
                metro_areas = {
                    "1": "서울특별시", "2": "부산광역시", "3": "대구광역시", "4": "인천광역시", 
                    "5": "광주광역시", "6": "대전광역시", "7": "울산광역시", "8": "세종특별자치시",
                    "9": "경기도", "10": "강원도", "11": "충청북도", "12": "충청남도",
                    "13": "전라북도", "14": "전라남도", "15": "경상북도", "16": "경상남도", "17": "제주특별자치도"
                }
                
                # 시/도 선택
                print("\n시/도를 선택하세요:")
                for key, value in metro_areas.items():
                    print(f"{key}. {value}")
                    
                metro_choice = input("선택 (1-17): ")
                
                if metro_choice not in metro_areas:
                    print("잘못된 선택입니다.")
                    continue
                    
                selected_metro = metro_areas[metro_choice]
                print(f"\n{selected_metro}의 구/군을 검색합니다...")
                
                # URL 구성
                base_url = f"https://new.land.naver.com/regions?cortarNo="
                metro_data = {
                    "서울특별시": "1100000000", "부산광역시": "2600000000", "대구광역시": "2700000000", 
                    "인천광역시": "2800000000", "광주광역시": "2900000000", "대전광역시": "3000000000", 
                    "울산광역시": "3100000000", "세종특별자치시": "3600000000", "경기도": "4100000000", 
                    "강원도": "4200000000", "충청북도": "4300000000", "충청남도": "4400000000",
                    "전라북도": "4500000000", "전라남도": "4600000000", "경상북도": "4700000000", 
                    "경상남도": "4800000000", "제주특별자치도": "5000000000"
                }
                
                # 시/도 URL 방문
                crawler.start_browser()
                metro_cortarNo = metro_data[selected_metro]
                metro_url = base_url + metro_cortarNo
                crawler.driver.get(metro_url)
                time.sleep(5)  # 페이지 로딩 대기
                
                # 구/군 목록 추출
                districts = []
                try:
                    elements = crawler.driver.find_elements(By.CSS_SELECTOR, "div.area_item")
                    for element in elements:
                        try:
                            district_name = element.find_element(By.CSS_SELECTOR, "span.text").text
                            district_el = element.find_element(By.CSS_SELECTOR, "span.text")
                            crawler.driver.execute_script("arguments[0].scrollIntoView();", district_el)
                            
                            # 클릭하여 코드 추출
                            district_el.click()
                            time.sleep(2)
                            current_url = crawler.driver.current_url
                            cortarNo = current_url.split("cortarNo=")[1].split("&")[0] if "cortarNo=" in current_url else ""
                            
                            districts.append({
                                "name": district_name,
                                "cortarNo": cortarNo,
                                "url": f"https://new.land.naver.com/complexes?ms={metro_cortarNo}&cortarNo={cortarNo}"
                            })
                            
                            # 전체 선택으로 돌아가기
                            crawler.driver.get(metro_url)
                            time.sleep(3)
                        except Exception as e:
                            print(f"구/군 추출 중 오류: {e}")
                            continue
                except Exception as e:
                    print(f"구/군 목록 추출 실패: {e}")
                
                if not districts:
                    print("구/군 목록을 추출할 수 없습니다.")
                    continue
                
                # 구/군 선택 표시
                print(f"\n{selected_metro}의 구/군 목록:")
                for i, district in enumerate(districts):
                    print(f"{i+1}. {district['name']}")
                
                district_choice = input(f"선택 (1-{len(districts)}), 또는 '전체'를 입력하세요: ")
                
                selected_districts = []
                if district_choice.lower() == "전체":
                    selected_districts = districts
                    print(f"{selected_metro} 전체 구/군을 크롤링합니다 (총 {len(districts)}개 지역)")
                else:
                    try:
                        idx = int(district_choice) - 1
                        if 0 <= idx < len(districts):
                            selected_districts = [districts[idx]]
                            print(f"{selected_metro} {selected_districts[0]['name']}을(를) 크롤링합니다.")
                        else:
                            print("잘못된 번호입니다.")
                            continue
                    except ValueError:
                        print("잘못된 입력입니다.")
                        continue
                
                # 각 선택된 구/군 크롤링
                for district in selected_districts:
                    district_url = district["url"]
                    district_name = f"{selected_metro} {district['name']}"
                    
                    # URL에 주택유형과 거래방식 적용
                    district_url = update_url_with_filters(district_url, housing_type_code, trade_type_code)
                    
                    print(f"\n'{district_name}' 크롤링 중...")
                    
                    # 파일명 생성
                    safe_district = ''.join(c for c in district_name if c.isalnum() or c.isspace()).strip().replace(' ', '_')
                    filename = os.path.join(results_dir, f"{safe_district}_{timestamp_short}.csv")
                    
                    try:
                        # 매물 목록 가져오기
                        complexes = crawler.parse_complex_list(district_url)
                        print(f"검색된 총 {len(complexes)}개의 매물 목록")
                        
                        # 추출할 매물 수 결정
                        if max_limit > 0:
                            complexes_to_process = complexes[:max_limit]
                            print(f"설정된 한도에 따라 {len(complexes_to_process)}개 매물만 처리합니다.")
                        else:
                            complexes_to_process = complexes
                            
                        # 상세 정보 수집
                        details = []
                        failed_items = []
                        
                        for j, complex_data in enumerate(complexes_to_process):
                            try:
                                print(f"[{j+1}/{len(complexes_to_process)}] '{complex_data['name']}' 상세 정보 수집 중...")
                                detail = crawler.parse_complex_detail(complex_data['link'])
                                detail["region"] = district_name
                                details.append(detail)
                                time.sleep(1.5)
                            except Exception as e:
                                print(f"상세 정보 수집 실패: {e}")
                                failed_items.append({
                                    "region": district_name,
                                    "name": complex_data['name'],
                                    "link": complex_data['link']
                                })
                                time.sleep(3)
                        
                        # 데이터 저장
                        if details:
                            saved_file = crawler.save_to_csv(details, filename)
                            if saved_file:
                                print(f"'{district_name}' 크롤링 성공: {len(details)}개 매물 저장")
                        else:
                            print(f"'{district_name}' 크롤링 실패: 저장할 데이터 없음")
                            # 실패한 지역 기록
                            with open(os.path.join(debug_dir, "failed_regions.txt"), "a", encoding="utf-8") as f:
                                f.write(f"{district_name}\t{district_url}\t실패\n")
                            
                        # 실패한 항목 기록
                        if failed_items:
                            with open(os.path.join(debug_dir, "failed_items.txt"), "a", encoding="utf-8") as f:
                                for item in failed_items:
                                    f.write(f"{item['region']}\t{item['name']}\t{item['link']}\n")
                            print(f"{len(failed_items)}개의 실패한 항목이 기록되었습니다.")
                    
                    except Exception as e:
                        print(f"'{district_name}' 크롤링 실패: {e}")
                        # 실패한 지역 기록
                        with open(os.path.join(debug_dir, "failed_regions.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{district_name}\t{district_url}\t실패\n")
                        time.sleep(5)  # 더 긴 대기 시간
            
            elif choice == "4":
                # 검색어를 통한 크롤링
                print("\n검색어를 통한 크롤링을 시작합니다.")
                
                # 검색어 입력
                search_query = input("검색할 키워드를 입력하세요 (아파트명, 지역명 등): ")
                
                if not search_query.strip():
                    print("검색어를 입력하지 않았습니다.")
                    continue
                    
                # 검색 URL 구성
                search_base = "https://new.land.naver.com/search?"
                search_url = f"{search_base}ms=37.5,127,8&a=APT:ABYG:JGC&e=RETAIL&q={urllib.parse.quote(search_query)}"
                
                # URL에 주택유형과 거래방식 적용
                search_url = update_url_with_filters(search_url, housing_type_code, trade_type_code)
                
                print(f"\n'{search_query}' 검색 중...")
                
                # 파일명 생성 및 경로 설정
                safe_query = ''.join(c for c in search_query if c.isalnum() or c.isspace()).strip().replace(' ', '_')
                filename = os.path.join(results_dir, f"검색_{safe_query}_{timestamp_short}.csv")
                
                try:
                    # 브라우저 시작
                    crawler.start_browser()
                    
                    # 검색 결과 크롤링
                    time.sleep(3)
                    crawler.driver.get(search_url)
                    time.sleep(5)  # 페이지 로딩 대기
                    
                    # 검색 결과 확인
                    try:
                        # 검색 결과가 있는지 확인
                        no_result = crawler.driver.find_elements(By.CSS_SELECTOR, ".no_result")
                        if no_result:
                            print(f"'{search_query}'에 대한 검색 결과가 없습니다.")
                            continue
                            
                        # 매물 목록 가져오기
                        complexes = crawler.parse_complex_list(search_url)
                        print(f"검색된 총 {len(complexes)}개의 매물 목록")
                        
                        # 추출할 매물 수 결정
                        if max_limit > 0:
                            complexes_to_process = complexes[:max_limit]
                            print(f"설정된 한도에 따라 {len(complexes_to_process)}개 매물만 처리합니다.")
                        else:
                            complexes_to_process = complexes
                            
                        # 상세 정보 수집
                        details = []
                        failed_items = []
                        
                        for j, complex_data in enumerate(complexes_to_process):
                            try:
                                print(f"[{j+1}/{len(complexes_to_process)}] '{complex_data['name']}' 상세 정보 수집 중...")
                                detail = crawler.parse_complex_detail(complex_data['link'])
                                detail["region"] = search_query  # 검색어를 지역 정보로 기록
                                details.append(detail)
                                time.sleep(1.5)
                            except Exception as e:
                                print(f"상세 정보 수집 실패: {e}")
                                failed_items.append({
                                    "region": search_query,
                                    "name": complex_data['name'],
                                    "link": complex_data['link']
                                })
                                time.sleep(3)
                        
                        # 데이터 저장
                        if details:
                            saved_file = crawler.save_to_csv(details, filename)
                            if saved_file:
                                print(f"'{search_query}' 검색 결과 크롤링 성공: {len(details)}개 매물 저장")
                        else:
                            print(f"'{search_query}' 검색 결과 크롤링 실패: 저장할 데이터 없음")
                            
                        # 실패한 항목 기록
                        if failed_items:
                            with open(os.path.join(debug_dir, "failed_items.txt"), "a", encoding="utf-8") as f:
                                for item in failed_items:
                                    f.write(f"{item['region']}\t{item['name']}\t{item['link']}\n")
                            print(f"{len(failed_items)}개의 실패한 항목이 기록되었습니다.")
                            
                    except Exception as e:
                        print(f"검색 결과 파싱 중 오류 발생: {e}")
                    
                except Exception as e:
                    print(f"'{search_query}' 검색 중 오류 발생: {e}")
                
                finally:
                    # 브라우저 종료
                    try:
                        crawler.close_browser()
                    except:
                        pass
            
            elif choice == "0":
                print("\n프로그램을 종료합니다.")
                break
            
            else:
                print("잘못된 옵션을 선택했습니다.")
            
            # 크롤링 종료 시간 기록 및 소요 시간 계산
            end_time = time.time()
            elapsed_time = end_time - start_time
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            print(f"\n=== 크롤링 완료: {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
            print(f"소요 시간: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초")
            
            return True
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        # 상세 오류 로그 저장
        with open(os.path.join(debug_dir, f"error_log_{timestamp}.txt"), "w", encoding="utf-8") as f:
            import traceback
            f.write(f"오류 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"오류 내용: {str(e)}\n\n")
            f.write(traceback.format_exc())
        print(f"오류 로그가 {debug_dir} 디렉토리에 저장되었습니다.")
    finally:
        # 브라우저 종료
        crawler.close_browser()
        print("브라우저 종료 완료")

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