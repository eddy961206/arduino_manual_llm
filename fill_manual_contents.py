import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import time

# .env 파일에서 환경 변수 로드
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-exp-1206:generateContent?key=" + API_KEY

# API 요청 헤더 설정
headers = {
    "Content-Type": "application/json"
}

def generate_content(cursor_rules_content, title):
    """
    Gemini 모델 API를 호출하여 내용을 생성합니다.
    """
    prompt = f"{cursor_rules_content}\n\n'{title}'에 대한 자세하고 명확한 설명을 작성해 주세요."
    
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # 응답 JSON 구조를 확인하고 텍스트 추출
        if response.status_code == 200:
            response_json = response.json()
            if 'candidates' in response_json and response_json['candidates']:
                first_candidate = response_json['candidates'][0]
                if 'content' in first_candidate and 'parts' in first_candidate['content']:
                    parts = first_candidate['content']['parts']
                    if parts and 'text' in parts[0]:
                        return parts[0]['text'].strip()
                    else:
                        print("응답에 텍스트가 없습니다.")
                else:
                    print("응답 후보에 콘텐츠가 없습니다.")
            else:
                print("응답에 후보가 없습니다.")
        else:
            print(f"응답 상태 코드가 {response.status_code}입니다.")
            print(f"응답 내용: {response.text}")
        return ""
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
    except Exception as err:
        print(f"기타 오류 발생: {err}")
    return ""

def main():
    # manual 폴더 경로 설정
    manual_path = Path("C:/workspaces/python_workspace/arduino/manual")
    
    # .cursorrules 파일 경로
    cursor_rules_path = Path(".cursorrules")
    
    # .cursorrules 파일 내용 읽기
    with open(cursor_rules_path, 'r', encoding='utf-8') as f:
        cursor_rules_content = f.read()
    
    # 모든 단원 폴더 탐색
    for section_folder in manual_path.iterdir():
        if section_folder.is_dir():
            print(f"단원 폴더 탐색 중: {section_folder.name}")
            # 각 단원 내의 모든 .md 파일 탐색
            for md_file in section_folder.glob("*.md"):
                title = md_file.stem  # 파일명에서 확장자 제거
                print(f"소단원 제목: {title}")
                
                # 내용 생성
                content = generate_content(cursor_rules_content, title)
                
                if content:
                    # .md 파일에 내용 작성
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"내용이 성공적으로 '{md_file}'에 작성되었습니다.")
                else:
                    print(f"내용 생성 실패: '{md_file}'")
                
                # API 호출 간 간격 두기 (필요 시)
                time.sleep(1)  # 1초 대기

    print("모든 소단원에 내용이 작성되었습니다.")

if __name__ == "__main__":
    main()
