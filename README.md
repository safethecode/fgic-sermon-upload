# 설교 관리 시스템

설교 파일을 관리하고 업로드하기 위한 통합 시스템입니다. RTF 형식의 설교 파일을 변환하고, 설교 정보를 관리하며, 웹사이트 업로드를 자동화할 수 있습니다.

## 주요 기능

### RTF to TXT 변환기
- RTF 형식의 설교 파일을 TXT 형식으로 변환
- 연도별 폴더 구조 유지
- 파일명의 날짜 형식 자동 인식 (YYYYMMDD)

### 설교 관리 GUI
- 설교 파일 목록 관리 및 검색
  - 연도별 분류
  - 완료/미완료 항목 필터링
  - 검색 기능
- 설교 정보 자동 추출
  - 제목
  - 성경구절
  - 설교자
  - 날짜
- 썸네일 이미지 관리
  - 드래그 앤 드롭 지원
  - 자동 크기 조정
  - 미리보기 기능
- YouTube 영상 자동 검색 및 링크 생성
  - 채널 내 검색
  - 자동 썸네일 다운로드
- 성경 구절 자동 조회
  - 구절 파싱
  - 본문 내용 자동 추출

### 자동화 기능
- 클립보드 자동 복사
- 입력 위치 자동 설정
- 매크로를 통한 자동 입력
- 웹사이트 자동 업로드
  - 일괄 업로드 지원
  - 진행 상태 추적
  - 오류 복구 기능

### 썸네일 다운로더
```bash
python youtube_thumbnail_downloader.py
```

썸네일 다운로더는 다음과 같은 기능을 제공합니다:
- YouTube API를 사용하여 설교 영상 검색
- 연도별 자동 썸네일 다운로드
- 고화질(maxresdefault) 또는 표준화질(hqdefault) 썸네일 자동 선택
- API 키 할당량 관리 및 자동 전환
- 이미 존재하는 썸네일 스킵 기능

#### 설정 방법
1. YouTube API 키 설정
   ```python
   self.api_keys = [
       'YOUR_API_KEY_1',
       'YOUR_API_KEY_2',  # 선택사항: 여러 개의 API 키 사용 가능
   ]
   ```

2. YouTube 채널 ID 설정
   ```python
   self.channel_id = 'YOUR_CHANNEL_ID'  # 검색할 YouTube 채널 ID
   ```

3. 처리할 연도 설정
   ```python
   target_year = "1986"  # 처리할 연도 지정
   ```

#### 주의사항
- YouTube API 일일 할당량 제한에 주의
- 네트워크 상태에 따라 다운로드 속도가 달라질 수 있음
- 대량의 파일 처리 시 충분한 저장 공간 확보 필요

## 시스템 요구사항

- Python 3.6 이상
- PyQt5
- 필요한 Python 패키지:
  - striprtf: RTF 파일 변환
  - requests: HTTP 요청 처리
  - beautifulsoup4: 웹 스크래핑
  - google-api-python-client: YouTube API 연동
  - python-dotenv: 환경변수 관리
  - pynput: 키보드/마우스 제어
  - selenium: 웹 자동화

## 프로젝트 구조

```
fgic-sermon-upload/
├── app.py                              # 메인 GUI 애플리케이션
├── rtf_to_txt_converter.py             # RTF 변환 스크립트
├── youtube_thumbnail_downloader.py     # 썸네일 다운로더
├── requirements.txt                    # 패키지 의존성
├── .env                                # 환경변수 설정
└── contents/                           # 컨텐츠 디렉토리
    ├── 내용/                            # RTF 원본 파일
    ├── 변환/                            # 변환된 TXT 파일
    └── 썸네일/                           # 썸네일 이미지
```

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

3. `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   WEBSITE_USERNAME=your_username
   WEBSITE_PASSWORD=your_password
   ```

## 사용법

### RTF 파일 변환
```bash
python rtf_to_txt_converter.py <input_path> <output_path>
```
- `input_path`: RTF 파일이 있는 디렉토리 경로
- `output_path`: 변환된 TXT 파일을 저장할 경로

### GUI 애플리케이션 실행
```bash
python app.py
```

#### GUI 주요 기능
1. 파일 목록에서 설교 선택
2. 자동으로 추출된 정보 확인 및 수정
3. 썸네일 드래그 앤 드롭으로 추가
4. 입력 위치 설정 (매크로용)
5. 자동 입력 또는 웹사이트 업로드 실행

## 주의사항

- YouTube API 키의 일일 할당량에 주의하세요.
- 웹사이트 자동화 시 네트워크 상태를 확인하세요.
- 매크로 사용 시 입력 위치가 정확히 설정되었는지 확인하세요.
- 대량의 파일을 처리할 때는 충분한 디스크 공간을 확보하세요.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.