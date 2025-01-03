import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import time
import re

# .env 파일에서 환경 변수 로드
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + API_KEY

# API 요청 헤더 설정
headers = {
    "Content-Type": "application/json"
}

def extract_section_content(markdown_content, section_title):
    """
    마크다운 내용에서 특정 섹션의 내용을 추출합니다.
    """
    # 섹션 제목을 찾기 위한 정규 표현식 패턴
    pattern = rf"^##\s+{section_title}\s*?\n([\s\S]*?)(?=\n##\s|$)"
    match = re.search(pattern, markdown_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    else:
        return ""

def generate_content(cursor_rules_content, knowledge_content, title):
    """
    Gemini 모델 API를 호출하여 내용을 생성합니다.
    """
    section_content = extract_section_content(knowledge_content, title)
    
    prompt = f"{cursor_rules_content}\n\n{knowledge_content}\n\n지금 작성하려는 섹션은 '{title}'입니다.\n\n이 섹션에 대한 자세한 내용은 다음과 같습니다:\n{section_content}\n\n이 섹션에 대한 자세하고 명확한 설명을 작성해 주세요."

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
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 오류 발생: {http_err}")
        print(f"응답 상태 코드: {response.status_code}")
        # print(f"응답 내용: {response.text}")
    except Exception as err:
        print(f"기타 오류 발생: {err}")
    return ""

def main():
    # manual 폴더 경로 설정
    manual_path = Path("C:/workspaces/python_workspace/arduino/manual")

    # .cursorrules 파일 경로
    cursor_rules_path = Path(".cursorrules")

    # knowledge.md 파일 경로
    knowledge_path = Path("knowledge.md")

    # .cursorrules 파일 내용 읽기
    with open(cursor_rules_path, 'r', encoding='utf-8') as f:
        cursor_rules_content = f.read()

    # knowledge.md 파일 내용 읽기
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        knowledge_content = f.read()

    # 모든 단원 폴더 탐색
    for section_folder in manual_path.iterdir():
        if section_folder.is_dir():
            print(f"단원 폴더 탐색 중: {section_folder.name}")
            # 각 단원 내의 모든 .md 파일 탐색
            for md_file in section_folder.glob("*.md"):
                title = md_file.stem  # 파일명에서 확장자 제거
                print(f"소단원 제목: {title}")

                # 파일 내용 확인 (비어 있는지 여부)
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                # 파일이 비어 있는 경우에만 내용 생성
                if not content:
                    content = generate_content(cursor_rules_content, knowledge_content, title)

                    if content:
                        # .md 파일에 내용 작성
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"내용이 성공적으로 '{md_file}'에 작성되었습니다.")
                    else:
                        print(f"내용 생성 실패: '{md_file}'")
                else:
                    print(f"파일 '{md_file}'은 비어 있지 않으므로 건너뜁니다.")

                # API 호출 간 간격 두기 (필요 시)
                time.sleep(1)  # 1초 대기

    print("모든 소단원에 내용이 작성되었습니다.")

if __name__ == "__main__":
    main()