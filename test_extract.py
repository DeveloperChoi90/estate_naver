from naver_estate_crawling import NaverEstateCrawler
import time
import os

# 디버그 로그 디렉토리 생성
os.makedirs("debug_logs", exist_ok=True)

print("네이버 부동산 데이터 추출 테스트 시작...")

# 크롤러 초기화
crawler = NaverEstateCrawler(headless=False)

try:
    # 서울 강남구 URL
    test_url = "https://new.land.naver.com/complexes?ms=37.5073421,127.0588579,15&a=APT&e=RETAIL"
    
    print(f"강남구 아파트 목록 페이지 로딩 중... URL: {test_url}")
    # 해당 지역의 아파트 목록 가져오기
    complexes = crawler.parse_complex_list(test_url)
    
    print(f"\n{len(complexes)}개의 아파트 단지를 찾았습니다.\n")
    
    # 아파트 정보 표시
    for i, complex_data in enumerate(complexes[:5]):
        print(f"- 아파트 {i+1}: {complex_data['name']}")
        print(f"  주소/정보: {complex_data['info']}")
        print(f"  가격정보: {complex_data['price']}")
        print(f"  링크: {complex_data['link']}")
        print("")
    
    # 첫 번째 아파트 상세 정보 가져오기
    if complexes:
        print("\n첫 번째 아파트 상세 정보 가져오는 중...")
        first_complex = complexes[0]
        detail = crawler.parse_complex_detail(first_complex['link'])
        
        print("\n상세 정보:")
        for key, value in detail.items():
            print(f"{key}: {value}")
        
        # 데이터 저장 테스트
        print("\n데이터 저장 테스트...")
        saved_file = crawler.save_to_csv([detail], "test_output.csv")
        
        if saved_file:
            full_path = os.path.abspath(saved_file)
            print(f"\n파일이 다음 경로에 저장되었습니다: {full_path}")
    
except Exception as e:
    print(f"오류 발생: {e}")

finally:
    # 브라우저 종료
    crawler.close_browser()
    print("\n테스트 완료") 