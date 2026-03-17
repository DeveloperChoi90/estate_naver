# 필수 설치 패키지: pip install curl_cffi pandas
from curl_cffi import requests
import json
import pandas as pd
from urllib.parse import unquote
import time
import random
import os

class RealEstateTracker:
    def __init__(self, applyhome_api_key=None):
        self.applyhome_api_key = applyhome_api_key

        # 핵심 우회 로직: curl_cffi를 사용하여 실제 Chrome 120 브라우저의 TLS 지문(Fingerprint)으로 위장
        self.session = requests.Session(impersonate="chrome120")

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        self._initialize_session()

    def _initialize_session(self):
        """네이버 NNB 쿠키 생성을 위한 초기 방문"""
        print("🔄 브라우저 세션 초기화 및 쿠키 발급 중 (TLS 우회 모드)...")
        try:
            self.session.get("https://www.naver.com/", timeout=10)
            time.sleep(random.uniform(0.5, 1.0))

            self.session.get("https://new.land.naver.com/", timeout=10)
            time.sleep(random.uniform(1.0, 2.0))
            print("✅ 세션 및 TLS 위장 초기화 완료")
        except Exception as e:
            print(f"⚠️ 세션 초기화 중 오류: {e}")

    def _request_with_retry(self, url, params=None, headers=None, max_retries=3):
        """TLS 위장 상태에서의 요청 로직"""
        for attempt in range(max_retries):
            time.sleep(random.uniform(0.5, 1.5))

            try:
                current_headers = headers if headers else self.headers
                response = self.session.get(url, headers=current_headers, params=params, timeout=15)

                if response.status_code == 200:
                    return response

                if response.status_code == 429:
                    wait_time = (2 ** attempt) + random.uniform(1.0, 2.0)
                    print(f"⚠️ 접속 제한 감지. {wait_time:.1f}초 대기... ({attempt+1}/{max_retries})")

                    if attempt == 1:
                        self._initialize_session()

                    time.sleep(wait_time)
                    continue

                print(f"⚠️ 서버 응답 오류: {response.status_code}")
                return response

            except Exception as e:
                print(f"⚠️ 연결 오류 발생: {e}")
                time.sleep(3)

        return None

    def _get_entrance_type(self, atcl_no):
        """매물 상세 API를 개별 호출하여 현관구조 추출 (PC API & 모바일 HTML 교차 2중 검증)"""
        if not atcl_no:
            return "-"

        # 목록 전체의 로딩 속도 저하를 막기 위해 아주 짧은 딜레이 허용
        time.sleep(random.uniform(0.05, 0.15))

        headers = self.headers.copy()

        # 1차 시도: PC 버전 JSON API 확인
        url_pc = f"https://new.land.naver.com/api/articles/{atcl_no}"
        headers['Referer'] = 'https://new.land.naver.com/'

        try:
            res = self.session.get(url_pc, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()

                # 명시적 키값 접근
                detail = data.get('articleDetail', {})
                facility = data.get('articleFacility', {})
                ent_type = detail.get('entranceType') or facility.get('entranceType')

                if ent_type:
                    return ent_type

                # JSON을 문자열로 변환하여 검색
                text_str = str(data)
                if '계단식' in text_str: return "계단식"
                if '복도식' in text_str: return "복도식"
                if '복합식' in text_str: return "복합식"
        except Exception:
            pass

        # 2차 시도: PC 버전에 정보가 없거나 실패 시, 모바일 웹페이지 HTML을 통째로 긁어와서 파싱 (확실한 우회법)
        url_mobile = f"https://m.land.naver.com/article/info/{atcl_no}"
        headers['Referer'] = 'https://m.land.naver.com/'

        try:
            res = self.session.get(url_mobile, headers=headers, timeout=5)
            if res.status_code == 200:
                text = res.text
                if '계단식' in text: return "계단식"
                if '복도식' in text: return "복도식"
                if '복합식' in text: return "복합식"
        except Exception:
            pass

        return "-"

    def get_region_info(self, region_query):
        # 1. 1차 검색: 자동완성 API를 통한 상위 지역 파악
        url = "https://new.land.naver.com/api/search"
        params = {'keyword': region_query}

        headers = self.headers.copy()
        headers['Referer'] = 'https://new.land.naver.com/'

        response = self._request_with_retry(url, headers=headers, params=params)

        if not response:
            return None

        try:
            if not response.text.strip():
                print("❌ 서버에서 빈 응답을 반환했습니다. (차단 의심)")
                return None
            data = response.json()
        except json.decoder.JSONDecodeError:
            print(f"❌ JSON 파싱 에러 (응답 데이터가 올바르지 않음)")
            return None

        try:
            regions = data.get('regions', [])

            if not regions:
                print("⚠️ 해당 키워드로 검색된 지역이 없습니다.")
                return None

            # 2. 2차 검색: 가장 정확한 상위 1개 지역의 하위 행정구역 전체 조회 API 호출
            base_region = regions[0]
            base_cortar_no = base_region.get('cortarNo')
            base_full_name = base_region.get('name') or base_region.get('fullName') or base_region.get('cortarName') or ''

            if base_cortar_no:
                sub_url = f"https://new.land.naver.com/api/regions/list?cortarNo={base_cortar_no}"
                sub_response = self._request_with_retry(sub_url, headers=headers)

                if sub_response and sub_response.status_code == 200:
                    sub_data = sub_response.json()
                    sub_region_list = sub_data.get('regionList', [])

                    if sub_region_list:
                        print(f"🔄 '{base_full_name}'의 전체 하위 행정구역을 추가로 불러왔습니다.")

                        # 0번 인덱스는 상위 지역 자체(예: 마포구 전체)로 두고 나머지는 하위 지역(예: 동)으로 채움
                        extended_regions = [base_region]

                        for sr in sub_region_list:
                            sr_name = sr.get('cortarName', '')
                            # 하위 지역 이름 조합 (예: "서울시 마포구" + " 공덕동")
                            sr['fullName'] = f"{base_full_name} {sr_name}".strip()
                            extended_regions.append(sr)

                        # 기존 자동완성(10개 제한) 결과를 새로 불러온 전체 하위 지역 목록으로 교체
                        regions = extended_regions

            if len(regions) > 1:
                print(f"\n여러 지역이 검색되었습니다:")
                for i, res in enumerate(regions):
                    # 새롭게 조합한 fullName을 가장 우선시하여 출력
                    region_name = (res.get('fullName') or
                                   res.get('cortarName') or
                                   res.get('dispNm') or
                                   res.get('name') or
                                   '알 수 없는 지역')
                    print(f"{i+1}: {region_name}")

                try:
                    choice = input(f"\n번호 선택 (1~{len(regions)}): ")
                    target = regions[int(choice) - 1]
                except:
                    target = regions[0]
            else:
                target = regions[0]

            # 최종 선택된 지역의 이름 설정
            target_name = (target.get('fullName') or
                           target.get('cortarName') or
                           target.get('dispNm') or
                           target.get('name') or
                           '알 수 없는 지역')

            print(f"✅ 선택 완료: {target_name}")

            return {
                'cortarNo': target.get('cortarNo'),
                'lat': target.get('centerLat'),
                'lon': target.get('centerLon'),
                'name': target_name
            }

        except Exception as e:
            print(f"❌ 데이터 파싱 에러: {e}")
            return None

    def format_price(self, prc, rent_prc, trade_type):
        try:
            def to_korean_unit(val):
                val = int(val)
                if val == 0: return ""
                if val >= 10000:
                    uk, man = val // 10000, val % 10000
                    return f"{uk}억 {man:,}만" if man > 0 else f"{uk}억"
                return f"{val:,}만"
            if trade_type == "B2": return f"{to_korean_unit(prc)} / {to_korean_unit(rent_prc)}"
            return to_korean_unit(prc)
        except: return "가격 미정"

    def get_naver_listings(self, region_info, trade_type="A1", sort_type="rank", limit=15):
        trade_dict = {"A1": "매매", "B1": "전세", "B2": "월세"}
        sort_dict = {"rank": "랭킹순", "prc": "낮은 가격순", "prcG": "높은 가격순", "date": "최신 등록순"}

        lat = float(region_info.get('lat'))
        lon = float(region_info.get('lon'))
        cortar_no = region_info.get('cortarNo')  # 지역 번호 추출

        print(f"🔍 매물 검색 중: {region_info.get('name')} [{trade_dict[trade_type]} - {sort_dict[sort_type]}] (최대 {limit}개)...")

        url = "https://m.land.naver.com/cluster/ajax/articleList"
        headers = self.headers.copy()
        headers['Referer'] = 'https://m.land.naver.com/'

        parsed_data = []
        seen_listings = set()  # ★ 중복 매물 추적을 위한 Set 추가
        page = 1

        try:
            # 설정한 limit을 채울 때까지 페이지를 넘기며 데이터 수집
            while len(parsed_data) < limit:
                params = {
                    'rletTpCd': 'APT', 'tradTpCd': trade_type, 'z': 14,
                    'lat': lat, 'lon': lon,
                    'btm': lat - 0.02, 'lft': lon - 0.02,
                    'top': lat + 0.02, 'rgt': lon + 0.02,
                    'sort': sort_type,
                    'page': page,
                    'cortarNo': cortar_no  # ★ 이 파라미터를 추가하여 주변 지역(예: 철산동)이 나오는 것을 원천 차단
                }

                response = self._request_with_retry(url, headers=headers, params=params)

                if not response or not response.text.strip():
                    break

                try:
                    data = response.json()
                except json.decoder.JSONDecodeError:
                    break

                item_list = data.get('body', [])

                if not item_list:
                    break

                for item in item_list:
                    raw_prc = item.get('prc', 0)
                    raw_rent = item.get('rentPrc', 0)

                    # ★ 중복 확인을 위한 고유 키 생성 (단지명, 동/호, 층, 가격, 면적)
                    atcl_nm = item.get('atclNm', '')
                    bild_nm_dtl = f"{item.get('bildNm', '')} {item.get('dtlAddr', '')}".strip()
                    flr_info = item.get('flrInfo', '')
                    spc2 = item.get('spc2', '')

                    unique_key = (atcl_nm, bild_nm_dtl, flr_info, raw_prc, raw_rent, spc2)

                    # 이미 처리된 매물이면 건너뛰기 (중복 제거)
                    if unique_key in seen_listings:
                        continue

                    seen_listings.add(unique_key)

                    # 월세(B2)인 경우: 보증금 + (월세 * 24), 그 외는 일반 가격 기준
                    sort_val = raw_prc + (raw_rent * 24) if trade_type == "B2" else raw_prc

                    # atclNo 또는 articleNo 키값 확인하여 저장
                    article_no = item.get('atclNo') or item.get('articleNo')

                    parsed_data.append({
                        '_atcl_no': article_no, # 상세 정보 조회를 위해 매물 번호 저장
                        '단지명': atcl_nm,
                        '동/호': bild_nm_dtl,
                        '층': flr_info,
                        '방향': item.get('direction', ''),
                        '현관구조': '-', # 일단 빈값으로 세팅 후 최종 결과에서만 업데이트
                        '가격': self.format_price(raw_prc, raw_rent, trade_type),
                        '면적': f"{spc2}㎡",
                        '특징': item.get('atclFetrDesc', ''),
                        # 내부 정렬을 위해 원시(raw) 가격 데이터 및 계산된 정렬값 저장
                        '_raw_prc': raw_prc,
                        '_raw_rent': raw_rent,
                        '_sort_val': sort_val
                    })

                # 네이버 API는 보통 한 페이지에 20개의 매물을 반환합니다.
                # 20개 미만으로 나왔다면 해당 조건의 마지막 페이지라는 뜻이므로 반복 종료
                if len(item_list) < 20:
                    break

                page += 1
                # 너무 잦은 API 호출로 차단당하지 않도록 짧은 대기 시간 추가
                time.sleep(random.uniform(0.3, 0.8))

            if not parsed_data:
                print("⚠️ 현재 지도 범위 내에 검색된 매물이 없습니다.")
                return pd.DataFrame()

            df = pd.DataFrame(parsed_data)

            # Pandas를 이용해 클라이언트 단에서 한 번 더 완벽하게 정렬 처리 (월세 계산식 반영)
            if sort_type == 'prc':
                df = df.sort_values(by=['_sort_val', '_raw_prc'], ascending=[True, True]).reset_index(drop=True)
            elif sort_type == 'prcG':
                df = df.sort_values(by=['_sort_val', '_raw_prc'], ascending=[False, False]).reset_index(drop=True)

            # 사용자가 요청한 개수(limit)만큼만 미리 자르기 (상세조회 호출 최소화 목적)
            df = df.head(limit)

            # --- [현관구조 추가 통신 로직] ---
            # 모든 매물이 아닌 최종 출력할 limit 개의 매물에 대해서만 상세정보를 개별 조회합니다.
            if not df.empty:
                print(f"🔄 최종 {len(df)}개 매물의 추가 상세 정보(현관구조 등)를 분석 중입니다. 잠시만 기다려주세요...")
                entrance_types = []
                for atcl_no in df['_atcl_no']:
                    entrance_types.append(self._get_entrance_type(atcl_no))
                df['현관구조'] = entrance_types

            # 출력 시 지저분해 보이지 않도록 정렬용 임시 컬럼 삭제
            df = df.drop(columns=['_raw_prc', '_raw_rent', '_sort_val', '_atcl_no'])

            return df

        except Exception as e:
            print(f"❌ 매물 리스트 생성 중 에러: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
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