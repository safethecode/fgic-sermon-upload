# 설교 관리 시스템

설교 파일을 관리하고 업로드하기 위한 통합 시스템입니다. RTF 형식의 설교 파일을 변환하고, 설교 정보를 관리하며, 웹사이트 업로드를 자동화할 수 있습니다.
> 이번주까지 해야 하는데, 작업하기 번거로워서 자동화 했어요.

## 주요 기능

### RTF to TXT 변환기
- RTF 형식의 설교 파일을 TXT 형식으로 변환
- 연도별 폴더 구조 유지
- 파일명의 날짜 형식 자동 인식

### 설교 관리 GUI
- 설교 파일 목록 관리 및 검색
- 설교 정보 자동 추출 (제목, 성경구절 등)
- 썸네일 이미지 관리 (드래그 앤 드롭 지원)
- YouTube 영상 자동 검색 및 링크 생성
- 성경 구절 자동 조회

### 자동화 기능
- 클립보드 자동 복사
- 입력 위치 자동 설정
- 매크로를 통한 자동 입력

## 시스템 요구사항

- Python 3.6 이상
- PyQt5
- 필요한 Python 패키지:
  - striprtf
  - requests
  - beautifulsoup4
  - google-api-python-client
  - python-dotenv
  - pynput

## 설치 방법

1. 이 저장소를 클론합니다.
   ```bash
   git clone https://github.com/safethecode/fgic-sermon-upload
   cd fgic-sermon-upload
   ```

2. 필요한 패키지를 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```

3. `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다. 예:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

## 사용법

1. `rtf_to_txt_converter.py`를 실행하여 RTF 파일을 TXT 파일로 변환합니다.
   ```bash
   python rtf_to_txt_converter.py <input_path> <output_path>
   ```

2. `app.py`를 실행하여 설교 업로드 애플리케이션을 시작합니다.
   ```bash
   python app.py
   ```