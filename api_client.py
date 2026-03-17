from curl_cffi import requests
import time
import random

class NaverApiClient:
    def __init__(self):
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

    def request_with_retry(self, url, params=None, custom_headers=None, max_retries=3):
        """TLS 위장 상태에서의 요청 로직"""
        for attempt in range(max_retries):
            time.sleep(random.uniform(0.5, 1.5))

            try:
                current_headers = custom_headers if custom_headers else self.headers
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
