import pandas as pd
import time
import os
from tracker import RealEstateTracker

def main():
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    # ★ 텍스트가 잘리지 않고 끝까지 나오게 하는 옵션 추가
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.unicode.east_asian_width', True)

    tracker = RealEstateTracker(applyhome_api_key="API_KEY_HERE")

    # 반복 검색을 위한 루프 추가
    while True:
        print("\n" + "="*60)
        print("🏠 부동산 매물 통합 조회 (종료하려면 'q' 또는 '종료' 입력)")
        print("="*60)

        user_region = input("조회할 지역명을 입력하세요 (예: 마포구, 광명시): ").strip()

        # 종료 로직
        if user_region.lower() in ['q', 'quit', 'exit', '종료']:
            print("👋 프로그램을 완전히 종료합니다. 이용해 주셔서 감사합니다.")
            break

        if not user_region:
            print("⚠️ 지역명을 입력해야 합니다. 다시 시도해주세요.")
            continue

        print(f"\n🔍 지역 검색 중: {user_region}...")
        region_info = tracker.get_region_info(user_region)

        if region_info:
            print("\n[거래 유형 선택]")
            print("1: 매매, 2: 전세, 3: 월세")
            choice = input("번호 입력 (엔터 입력 시 처음으로 이동): ").strip()

            # 입력 없이 넘어가거나 뒤로가기를 원할 때 처리
            if not choice:
                continue

            mapping = {'1': 'A1', '2': 'B1', '3': 'B2'}
            trade_names = {'1': '매매', '2': '전세', '3': '월세'}

            if choice in mapping:
                print("\n[정렬 기준 선택]")
                print("1: 랭킹순 (기본값)")
                print("2: 낮은 가격순")
                print("3: 높은 가격순")
                print("4: 최신 등록순")
                sort_choice = input("번호 입력 (엔터 입력 시 기본값): ").strip()

                sort_mapping = {'1': 'rank', '2': 'prc', '3': 'prcG', '4': 'date'}
                selected_sort = sort_mapping.get(sort_choice, 'rank')

                limit_input = input("\n출력할 매물 개수를 입력하세요 (엔터 입력 시 기본 15개): ").strip()
                try:
                    limit = int(limit_input) if limit_input else 15
                except ValueError:
                    limit = 15

                # 검색 시 limit 값을 넘겨주어 해당 개수를 채울 때까지 페이지를 조회하도록 함
                result = tracker.get_naver_listings(region_info, mapping[choice], selected_sort, limit)

                if result is not None and not result.empty:
                    print(f"\n✅ 조회 결과 (상위 {len(result)}개):")
                    print(result)

                    # --- ★ 검색한 지역의 네이버 부동산 링크 생성 및 출력 ---
                    lat = region_info.get('lat')
                    lon = region_info.get('lon')
                    trade_code = mapping[choice]

                    # 지도를 15 레벨 줌으로 설정하고 검색한 유형(매매/전세/월세)과 아파트 필터를 적용한 링크
                    naver_link = f"https://new.land.naver.com/complexes?ms={lat},{lon},15&a=APT&b={trade_code}&e=RETAIL"

                    print(f"\n🔗 네이버 부동산에서 보기 ({region_info.get('name')}):")
                    print(naver_link)
                    
                    # --- ★ 관심 매물 CSV 저장 로직 ---
                    print("\n[관심 매물 저장]")
                    save_input = input("저장할 매물의 번호(맨 왼쪽 숫자)를 쉼표(,)로 구분하여 입력하세요\n(예: 0, 2, 5) / 건너뛰려면 엔터: ").strip()
                    
                    if save_input:
                        try:
                            # 입력받은 문자열을 쉼표 기준으로 나누고 정수로 변환 (숫자인 것만)
                            indices = [int(idx.strip()) for idx in save_input.split(',') if idx.strip().isdigit()]
                            # 유효한 인덱스 범위 확인
                            valid_indices = [idx for idx in indices if 0 <= idx < len(result)]
                            
                            if valid_indices:
                                # 선택된 행만 추출
                                selected_df = result.iloc[valid_indices].copy()
                                
                                # 구분을 쉽게 하기 위해 파일 저장 시 지역명과 거래유형 정보 추가
                                selected_df.insert(0, '검색지역', region_info.get('name'))
                                selected_df.insert(1, '거래유형', trade_names[choice])
                                
                                csv_filename = "selected_listings.csv"
                                # 파일이 없으면 헤더 포함 저장, 이미 있으면 헤더 없이 이어서 누적 저장(append)
                                write_header = not os.path.exists(csv_filename)
                                selected_df.to_csv(csv_filename, mode='a', index=False, encoding='utf-8-sig', header=write_header)
                                
                                print(f"✅ 선택하신 {len(valid_indices)}개의 매물이 '{csv_filename}' 파일에 성공적으로 저장(누적)되었습니다!")
                            else:
                                print("⚠️ 유효한 번호가 입력되지 않았습니다. 저장을 건너뜁니다.")
                        except Exception as e:
                            print(f"❌ 저장 중 오류가 발생했습니다: {e}")
                else:
                    print("\n⚠️ 선택하신 조건에 맞는 매물을 찾지 못했습니다.")
            else:
                print("❌ 잘못된 입력입니다. 처음부터 다시 시작합니다.")
        else:
            print("❌ 지역 정보를 찾을 수 없습니다. 지역명을 다시 확인해 주세요.")

        # 결과 출력 후, 콘솔 화면이 바로 넘어가지 않도록 잠시 대기
        time.sleep(1)

if __name__ == "__main__":
    main()