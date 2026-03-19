import time
import random
import json
import pandas as pd
from api_client import NaverApiClient
from utils import format_price

class RealEstateTracker:
    def __init__(self, applyhome_api_key=None):
        self.applyhome_api_key = applyhome_api_key
        self.api = NaverApiClient()

    def _get_entrance_type(self, atcl_no):
        """매물 상세 API를 개별 호출하여 현관구조 추출 (PC API & 모바일 HTML 교차 2중 검증)"""
        if not atcl_no:
            return "-"

        # 목록 전체의 로딩 속도 저하를 막기 위해 아주 짧은 딜레이 허용
        time.sleep(random.uniform(0.05, 0.15))

        headers = self.api.headers.copy()

        # 1차 시도: PC 버전 JSON API 확인
        url_pc = f"https://new.land.naver.com/api/articles/{atcl_no}"
        headers['Referer'] = 'https://new.land.naver.com/'

        try:
            res = self.api.session.get(url_pc, headers=headers, timeout=5)
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
            res = self.api.session.get(url_mobile, headers=headers, timeout=5)
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

        headers = self.api.headers.copy()
        headers['Referer'] = 'https://new.land.naver.com/'

        response = self.api.request_with_retry(url, custom_headers=headers, params=params)

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
                sub_response = self.api.request_with_retry(sub_url, custom_headers=headers)

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

    def get_naver_listings(self, region_info, trade_type="A1", sort_type="rank", limit=15, min_area=None, max_area=None):
        trade_dict = {"A1": "매매", "B1": "전세", "B2": "월세"}
        sort_dict = {"rank": "랭킹순", "prc": "낮은 가격순", "prcG": "높은 가격순", "date": "최신 등록순"}

        lat = float(region_info.get('lat'))
        lon = float(region_info.get('lon'))
        cortar_no = region_info.get('cortarNo')  # 지역 번호 추출

        # 출력용 면적 필터 메시지 생성
        area_filter_msg = ""
        if min_area is not None or max_area is not None:
            min_str = f"{min_area}㎡" if min_area else "0㎡"
            max_str = f"{max_area}㎡" if max_area else "제한없음"
            area_filter_msg = f" [면적: {min_str} ~ {max_str}]"

        print(f"🔍 매물 검색 중: {region_info.get('name')} [{trade_dict[trade_type]} - {sort_dict[sort_type]}]{area_filter_msg} (최대 {limit}개)...")

        url = "https://m.land.naver.com/cluster/ajax/articleList"
        headers = self.api.headers.copy()
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

                response = self.api.request_with_retry(url, custom_headers=headers, params=params)

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

                    # --- ★ 면적(㎡) 필터링 로직 추가 ---
                    if min_area is not None or max_area is not None:
                        try:
                            # str()을 추가하여 숫자형 등 비문자열 타입도 처리하고, 변환 실패 시 안전하게 건너뛰도록 수정
                            area_val = float(str(spc2)) if spc2 else 0.0
                            
                            if min_area is not None and area_val < min_area:
                                continue
                            if max_area is not None and area_val > max_area:
                                continue
                        except (ValueError, TypeError):
                            # 면적 정보를 숫자로 변환할 수 없는 경우, 해당 매물은 필터링에서 제외
                            continue

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
                        '가격': format_price(raw_prc, raw_rent, trade_type),
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