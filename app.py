import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dotenv import load_dotenv
import tempfile
from pynput import keyboard
from pynput.keyboard import Key, Controller
from pynput import mouse
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import platform
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QShortcut
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
import threading
import gc
import sip

# .env 파일에서 환경변수 로드
load_dotenv()

class BibleAPI:
    def __init__(self):
        # 성경 구절 매핑
        self.bible_books = {
            '창세기': 'ge', '출애굽기': 'exo', '레위기': 'lev', '민수기': 'num',
            '신명기': 'deu', '여호수아': 'jos', '사사기': 'jdg', '룻기': 'rut',
            '사무엘상': '1sa', '사무엘하': '2sa', '열왕기상': '1ki', '열왕기하': '2ki',
            '역대상': '1ch', '역대하': '2ch', '에스라': 'ezr', '느헤미야': 'neh',
            '에스더': 'est', '욥기': 'job', '시편': 'psa', '잠언': 'pro',
            '전도서': 'ecc', '아가': 'sol', '이사야': 'isa', '예레미야': 'jer',
            '예레미야애가': 'lam', '에스겔': 'eze', '다니엘': 'dan', '호세아': 'hos',
            '요엘': 'joe', '아모스': 'amo', '오바댜': 'oba', '요나': 'jon',
            '미가': 'mic', '나훔': 'nah', '하박국': 'hab', '스바냐': 'zep',
            '학개': 'hag', '스가랴': 'zec', '말라기': 'mal', '마태복음': 'mat',
            '마가복음': 'mar', '누가복음': 'luk', '요한복음': 'joh', '사도행전': 'act',
            '로마서': 'rom', '고린도전서': '1co', '고린도후서': '2co', '갈라디아서': 'gal',
            '에베소서': 'eph', '빌립보서': 'phi', '골로새서': 'col', '데살로니가전서': '1th',
            '데살로니가후서': '2th', '디모데전서': '1ti', '디모데후서': '2ti', '디도서': 'tit',
            '빌레몬서': 'phm', '히브리서': 'heb', '야고보서': 'jam', '베드로전서': '1pe',
            '베드로후서': '2pe', '요한일서': '1jo', '요한이서': '2jo', '요한삼서': '3jo',
            '유다서': 'jud', '요한계시록': 'rev'
        }
        
    def parse_reference(self, reference):
        """성경 구절 참조를 파싱"""
        try:
            if not reference or len(reference.strip()) == 0:
                return None
            
            # "마태복음 5:3-12" 형식 파싱
            parts = reference.strip().split(' ', 1)
            if len(parts) < 2:
                return None
            
            book_name, verse_ref = parts
            
            # 장:절 파싱
            if '-' in verse_ref:
                # 범위가 있는 경우 (예: 5:3-12)
                chapter_verse, end_verse = verse_ref.split('-')
                chapter, start_verse = chapter_verse.split(':')
                
                # 장이 다른 경우 처리 (예: 5:3-6:2)
                if ':' in end_verse:
                    end_chapter, end_verse = end_verse.split(':')
                else:
                    end_chapter = chapter
                    
            else:
                # 단일 구절인 경우 (예: 5:3)
                chapter, start_verse = verse_ref.split(':')
                end_chapter = chapter
                end_verse = start_verse
                
            if book_name not in self.bible_books:
                return None
            
            return {
                'book': self.bible_books[book_name],
                'start_chapter': chapter,
                'start_verse': start_verse,
                'end_chapter': end_chapter,
                'end_verse': end_verse
            }
            
        except Exception as e:
            print(f"성경 구절 파싱 에러: {e}")
            return None

    def get_verse(self, reference):
        """성경 구절 가져오기"""
        try:
            parsed = self.parse_reference(reference)
            if not parsed:
                return None
                
            # iBibles URL 생성
            if parsed['start_chapter'] == parsed['end_chapter']:
                url = f"http://ibibles.net/quote.php?kor-{parsed['book']}/{parsed['start_chapter']}:{parsed['start_verse']}-{parsed['end_verse']}"
            else:
                url = f"http://ibibles.net/quote.php?kor-{parsed['book']}/{parsed['start_chapter']}:{parsed['start_verse']}-{parsed['end_chapter']}:{parsed['end_verse']}"
            
            # 웹 페이지 요청
            response = requests.get(url)
            response.encoding = 'utf-8'  # 한글 인코딩 설정
            
            if response.status_code == 200:
                # BeautifulSoup으로 파싱
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 모든 텍스트 추출
                verses = []
                for br in soup.find_all('br'):
                    # small 태그에서 절 번호 가져오기
                    verse_num = ''
                    small = br.find_previous('small')
                    if small:
                        verse_num = small.text.strip()
                    
                    # br 태그 이전의 텍스트 가져오기
                    text = br.previous_sibling
                    if text and isinstance(text, str):
                        # small 태그 내용 제거하고 정리
                        verse = re.sub(r'\s+', ' ', text.strip())
                        if verse:
                            # 절 번호만 추출 (예: "5:3" -> "3")
                            verse_num = verse_num.split(':')[-1]
                            verses.append(f"{verse_num} {verse}")
                
                # 결과 포맷팅
                result = f"\n{reference}\n\n"
                result += "\n".join(verses)
                return result
                
            return None
            
        except Exception as e:
            print(f"성경 구절 가져오기 에러: {e}")
            return None

class YouTubeAPI:
    def __init__(self):
        self.api_keys = [
            'API_KEY를 넣으세요.',
        ]
        self.current_key_index = 0
        self.youtube = self.create_youtube_service()
        self.channel_id = 'UCgeZJWROaoIP3VV2_d7CJlQ'  # @hyotv4508
    
    def create_youtube_service(self):
        """현재 API 키로 YouTube 서비스 생성"""
        return build('youtube', 'v3', developerKey=self.api_keys[self.current_key_index])
    
    def switch_to_next_key(self):
        """다음 API 키로 전환"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.youtube = self.create_youtube_service()
        print(f"YouTube API 키 전환: {self.current_key_index + 1}번째 키로 전환")
    
    def search_sermon(self, title, date):
        """설교 검색 with API 키 순환"""
        for _ in range(len(self.api_keys)):  # API 키 개수만큼 시도
            try:
                search_query = title
                request = self.youtube.search().list(
                    q=search_query,
                    channelId=self.channel_id,
                    part='id',
                    maxResults=1,
                    type='video'
                )
                response = request.execute()
                
                if response['items']:
                    video_id = response['items'][0]['id']['videoId']
                    return f"https://www.youtube.com/embed/{video_id}"
                    
            except Exception as e:
                if 'quota' in str(e).lower() or '403' in str(e):
                    print(f"API 키 할당량 초과 또는 403 에러. 다음 키로 전환 시도")
                    self.switch_to_next_key()
                    continue
                else:
                    print(f"YouTube API 에러: {e}")
                    break
        
        print("모든 API 키 시도 실패")
        return "https://www.youtube.com/embed/"  # 기본값 반환

class SermonProcessor:
    def __init__(self):
        self.base_path = "contents/내용/"
        self.thumbnail_path = "contents/썸네일/"
        self.bible_api = BibleAPI()
        self.youtube_api = YouTubeAPI()
        
    def get_sermon_files(self):
        """설교 파일 목록 가져오기"""
        sermon_files = []
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.rtf'):
                    sermon_files.append(os.path.join(root, file))
        return sorted(sermon_files)
        
    def parse_date(self, filename):
        """파일명에서 날짜 추출"""
        date_str = filename.replace(".rtf", "")
        return datetime.strptime(date_str, "%Y%m%d")
        
    def extract_sermon_info(self, file_path):
        """설교 정보 추출"""
        sermon_info = {
            'title': '',
            'bible_verse': ''
        }
        
        try:
            # RTF 경로를 TXT 경로로 변환
            txt_path = file_path.replace(os.path.join('contents', '내용'), 
                                       os.path.join('contents', '변환')).replace('.rtf', '.txt')
            
            if not os.path.exists(txt_path):
                print(f"TXT 파일이 없습니다: {txt_path}")
                return sermon_info
            
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 설교 제목 추출
            title_match = re.search(r"설교제목\s*:\s*(.*?)[\r\n]", content)
            if title_match:
                sermon_info['title'] = title_match.group(1).strip()
                
            # 성경 구절 추출
            bible_match = re.search(r"성경말씀\s*:\s*(.*?)[\r\n]", content)
            if bible_match:
                sermon_info['bible_verse'] = bible_match.group(1).strip()
                
            # 썸네일 경로 처리
            # 파일 경로에서 연도와 파일명 추출
            path_parts = os.path.normpath(file_path).split(os.sep)
            year = path_parts[-2]  # 연도 폴더명
            date_str = os.path.splitext(path_parts[-1])[0]  # 확장자 제거
            
            print(f"파일 경로 분석: {path_parts}")
            print(f"추출된 연도: {year}")
            print(f"추출된 날짜: {date_str}")
            
            # 썸네일 경로 구성 (연도 폴더 포함)
            thumbnail_path = os.path.join('contents', '썸네일', year, f"{date_str}.jpg")
            
            # 디버깅: 썸네일 경로 출력
            print(f"찾고 있는 썸네일 경로: {thumbnail_path}")
            print(f"썸네일 파일 존재 여부: {os.path.exists(thumbnail_path)}")
            
            if os.path.exists(thumbnail_path):
                sermon_info['thumbnail'] = thumbnail_path
            else:
                # jpg가 없다면 png 확인
                thumbnail_path_png = thumbnail_path.replace('.jpg', '.png')
                print(f"PNG 썸네일 찾기: {thumbnail_path_png}")
                if os.path.exists(thumbnail_path_png):
                    sermon_info['thumbnail'] = thumbnail_path_png
                
        except Exception as e:
            print(f"파일 처리 중 에러 발생: {e}")
            print(f"파일 경로: {txt_path}")
            import traceback
            traceback.print_exc()
            
        print(f"추출된 정보: {sermon_info}")
        return sermon_info

    def generate_content(self, sermon_info, date, bible_text):
        """설교 내용 생성"""
        content = f"""{date.strftime('%Y년 %m월 %d일')} 주일설교

설교제목: {sermon_info['title']}
성경말씀: {sermon_info['bible_verse']}

{bible_text if bible_text else ''}

"성경적 효 운동을 통해 하모니를 이루는 교회, 하모니를 이루는 사회,
하모니를 이루는 세상을 만들어 갑시다"

.................................................................
* 모든 저작권은 최성규의 HYO TV에 있습니다.
재배포시 인천순복음교회로 문의 바랍니다.

인천순복음교회 032)421 0091"""
        return content.strip()

class WebsiteAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.is_logged_in = False  # 로그인 상태 추적
        
    def start_browser(self):
        """브라우저 시작"""
        try:
            if not self.driver:  # 드라이버가 없을 때만 새로 시작
                chrome_options = Options()
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
                self.driver.get("http://admin.harmony7hyo.com/core/admin/login/login.php")
            elif not self.is_logged_in:  # 드라이버는 있지만 로그인이 필요한 경우
                self.driver.get("http://admin.harmony7hyo.com/core/admin/login/login.php")
            else:  # 이미 로그인된 상태면 에디터 페이지로 이동
                self.driver.get("http://admin.harmony7hyo.com/core/admin/vod/write.php?1=1&pageCode=16&category=&keyfield=&key=")
                
        except Exception as e:
            print(f"브라우저 시작 중 오류: {e}")
            self.close()
            raise e

    def close(self):
        """브라우저 종료"""
        try:
            if self.driver:
                # 열려있는 모든 창 닫기
                for handle in self.driver.window_handles:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                
                # 드라이버 종료
                self.driver.quit()
                self.driver = None
                self.wait = None
                
                # 잠시 대기하여 완전히 종료되도록 함
                time.sleep(1)
        except Exception as e:
            print(f"브라우저 종료 중 오류: {e}")
            # 오류가 발생해도 드라이버 참조 제거
            self.driver = None
            self.wait = None

    def __del__(self):
        """소멸자에서 브라우저 강제 종료"""
        self.close()

    def login(self, username, password):
        """로그인"""
        try:
            if self.is_logged_in:  # 이미 로그인된 상태면 True 반환
                return True
                
            # ID 입력
            id_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "id"))
            )
            id_input.send_keys(username)
            
            # 비밀번호 입력
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.CLASS_NAME, "btn_01")
            login_btn.click()
            
            # 로그인 성공 확인
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[menucode='content']"))
            )

            # 직접 등록 페이지로 이동
            self.driver.get("http://admin.harmony7hyo.com/core/admin/vod/write.php?1=1&pageCode=16&category=&keyfield=&key=")
            
            self.is_logged_in = True  # 로그인 상태 설정
            return True
            
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
            self.is_logged_in = False
            return False

    def upload_sermon(self, sermon_data):
        """설교 업로드"""
        try:
            print("업로드 시작...")
            print(f"전달받은 sermon_data: {sermon_data}")  # 전체 데이터 출력
            
            # 카테고리 선택
            category_select = Select(self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.radius3px.formSelect[name='category']"))
            ))
            
            # 성경 구절에 따라 적절한 카테고리 선택
            bible_verse = sermon_data['bible_verse']
            category_value = self.get_category_value(bible_verse)
            if category_value:
                category_select.select_by_value(str(category_value))
            
            # 날짜 선택
            date = sermon_data['date']
            
            # 년도 선택
            year_select = Select(self.driver.find_element(
                By.CSS_SELECTOR, 
                "select[name='year'].radius3px.formSelect"
            ))
            year_select.select_by_value(str(date.year))
            
            # 월 선택
            month_select = Select(self.driver.find_element(
                By.CSS_SELECTOR, 
                "select[name='month'].radius3px.formSelect"
            ))
            month_select.select_by_value(str(date.month).zfill(2))
            
            # 일 선택
            day_select = Select(self.driver.find_element(
                By.CSS_SELECTOR, 
                "select[name='day'].radius3px.formSelect"
            ))
            day_select.select_by_value(str(date.day).zfill(2))
            
            # 제목 입력
            title_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name='subject'].radius3px.basicTextinput")
            ))
            title_input.send_keys(sermon_data['title'])
            
            # 설교자 입력
            preacher_input = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='preacher'].radius3px.basicTextinput"
            )
            preacher_input.send_keys(sermon_data['preacher'])
            
            # 본문 입력
            bible_verse_input = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='word'].radius3px.basicTextinput"
            )
            bible_verse_input.send_keys(sermon_data['bible_verse'])
            
            # 유튜브 URL 입력
            youtube_input = self.driver.find_element(
                By.CSS_SELECTOR, "input[name='vodFile_1'].radius3px.basicTextinput"
            )
            youtube_input.send_keys(sermon_data['youtube_url'])
            
            # 썸네일 업로드
            print(f"썸네일 정보 확인: {sermon_data.get('thumbnail', '없음')}")  # 썸네일 정보 출력
            
            if sermon_data.get('thumbnail'):  # get 메서드로 안전하게 확인
                try:
                    print(f"썸네일 업로드 시도: {sermon_data['thumbnail']}")
                    
                    # 파일 업로드 input 찾기 (여러 방법 시도)
                    file_input = None
                    try:
                        # 방법 1: name으로 찾기
                        file_input = self.wait.until(
                            EC.presence_of_element_located((By.NAME, "thumbnail"))
                        )
                    except Exception as e1:
                        print(f"방법 1 실패: {e1}")
                        try:
                            # 방법 2: CSS 셀렉터로 찾기
                            file_input = self.wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][name='thumbnail']"))
                            )
                        except Exception as e2:
                            print(f"방법 2 실패: {e2}")
                            try:
                                # 방법 3: XPath로 찾기
                                file_input = self.wait.until(
                                    EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @name='thumbnail']"))
                                )
                            except Exception as e3:
                                print(f"방법 3 실패: {e3}")
                    
                    if file_input:
                        # 절대 경로로 변환
                        abs_thumbnail_path = os.path.abspath(sermon_data['thumbnail'])
                        print(f"썸네일 절대 경로: {abs_thumbnail_path}")
                        print(f"파일 존재 여부: {os.path.exists(abs_thumbnail_path)}")
                        
                        # JavaScript로 파일 input의 스타일을 변경하여 보이게 만들기
                        self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                        
                        # 파일 업로드
                        file_input.send_keys(abs_thumbnail_path)
                        print("썸네일 업로드 완료")
                    else:
                        print("파일 업로드 input 요소를 찾을 수 없습니다.")
                    
                except Exception as e:
                    print(f"썸네일 업로드 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("썸네일 정보가 없습니다.")
            
            # 내용 입력 (iframe)
            iframe = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe.cke_wysiwyg_frame")
            ))
            self.driver.switch_to.frame(iframe)
            
            # iframe 내부의 body에 내용 입력
            content_body = self.wait.until(EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            ))
            content_body.click()  # 편집기 활성화
            content_body.send_keys(sermon_data['content'])
            
            # 기본 프레임으로 복귀
            self.driver.switch_to.default_content()
            
            # 방송등록 버튼 찾아 클릭 (여러 방법 시도)
            try:
                register_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//p[contains(@class, 'adminBtn02') and contains(text(), '방송등록')]"))
                )
                register_btn.click()
                time.sleep(10)  # 등록 완료 대기
                
                # 새로운 에디터 페이지로 이동
                self.driver.get("http://admin.harmony7hyo.com/core/admin/vod/write.php?1=1&pageCode=16&category=&keyfield=&key=")
                return True
                
            except Exception as e2:
                print(f"방송등록 버튼 클릭 실패: {e2}")
                try:
                    self.driver.execute_script("checkValue();")
                    time.sleep(2)
                    self.driver.get("http://admin.harmony7hyo.com/core/admin/vod/write.php?1=1&pageCode=16&category=&keyfield=&key=")
                    return True
                except Exception as e3:
                    print(f"JavaScript 실행 실패: {e3}")
                    return False
                
        except Exception as e:
            print(f"업로드 중 오류 발생: {e}")
            return False

    def get_category_value(self, bible_verse):
        """성경 구절에 따른 카테고리 값 반환"""
        category_mapping = {
            '창세기': '2',
            '출애굽기': '1',
            '레위기': '3', '민수기': '3',
            '신명기': '4', '여호수아': '4',
            '사사기': '5', '룻기': '5',
            '사무엘상': '6', '사무엘하': '6',
            '열왕기상': '7', '열왕기하': '7',
            '역대상': '8', '역대하': '8',
            '에스라': '9', '느헤미야': '9', '에스더': '9',
            '욥기': '10', '시편': '10',
            '잠언': '11', '전도서': '11',
            '아가': '12', '이사야': '12',
            '예레미야': '13', '예레미야애가': '13',
            '에스겔': '14', '다니엘': '14', '호세아': '14',
            '요엘': '15', '아모스': '15', '오바댜': '15',
            '요나': '16', '미가': '16', '나훔': '16',
            '하박국': '17', '스바냐': '17',
            '학개': '18', '스가랴': '18', '말라기': '18',
            '마태복음': '19',
            '마가복음': '20',
            '누가복음': '21',
            '요한복음': '22',
            '사도행전': '23',
            '로마서': '24',
            '고린도전서': '25', '고린도후서': '25',
            '갈라디아서': '26', '에베소서': '26',
            '빌립보서': '27', '골로새서': '27',
            '데살로니가전서': '28', '데살로니가후서': '28',
            '디모데전서': '29', '디모데후서': '29',
            '디도서': '30', '빌레몬서': '30',
            '히브리서': '31', '야고보서': '31',
            '베드로전서': '32', '베드로후서': '32',
            '요한일서': '33', '요한이서': '33', '요한삼서': '33',
            '유다서': '34', '요한계시록': '34'
        }
        
        # 성경 구절에서 책 이름 추출
        book_name = bible_verse.split(' ')[0]
        return category_mapping.get(book_name)

class SermonUploaderUI(QMainWindow):
    # 시그널 정의
    update_item_signal = pyqtSignal(QListWidgetItem)
    
    def __init__(self):
        super().__init__()
        self.processor = SermonProcessor()
        self.automation = WebsiteAutomation()
        self.sermon_cache = {}  # 설교 데이터 캐시 추가
        
        # OS 확인
        self.is_mac = platform.system() == 'Darwin'
        
        # 상태 변수
        self.click_count = 0
        self.last_paste_time = 0  # 마지막 붙여넣기 시간
        
        # 키보드 리스너 설정
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        self.keyboard_listener.start()

        # 매크로 컨트롤러
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
        # 클릭 위치 저장
        self.click_positions = []
        
        # 설정 파일에서 저장된 위치 로드
        self.load_click_positions()
        
        # UI 초기화
        self.init_ui()

        # 시그널 연결
        self.update_item_signal.connect(self._update_item_status)

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle('설교 업로드 도우미')
        self.setGeometry(100, 100, 1200, 800)
        
        # 매크로 버튼 초기화
        self.set_positions_button = QPushButton('입력 위치 설정')
        self.set_positions_button.clicked.connect(self.set_click_positions)
        self.set_positions_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3d8be6;
            }
        """)
        
        self.macro_button = QPushButton('자동 입력 매크로 실행')
        self.macro_button.clicked.connect(self.run_macro)
        self.macro_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # 병렬 업로드 버튼 추가
        self.parallel_upload_button = QPushButton('미등록 설교 일괄 업로드')
        self.parallel_upload_button.clicked.connect(self.parallel_upload)
        self.parallel_upload_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        
        # 왼쪽 패널 (파일 리스트)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # 검색 기능
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('검색어를 입력하세요')
        self.search_input.textChanged.connect(self.filter_list)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # 파일 카운트 레이블
        self.file_count_label = QLabel('설교 파일 목록 (0개)')
        left_layout.addWidget(self.file_count_label)
        
        # 파일 리스트 설정
        file_list_layout = self.setup_file_list()  # 한 번만 호출
        left_layout.addWidget(QLabel('설교 파일 목록'))
        left_layout.addLayout(file_list_layout)
        left_panel.setLayout(left_layout)
        
        # 오른쪽 패널 (설교 정보 입력)
        right_panel = QWidget()
        right_layout = QFormLayout()
        
        self.category = QComboBox()
        self.category.addItems(['주일설교', '수요설교', '금요설교'])
        
        self.date_edit = QDateEdit()
        self.title = QLineEdit()
        self.preacher = QLineEdit()
        self.bible_verse = QLineEdit()
        self.youtube_embed = QLineEdit()
        self.content = QTextEdit()
        
        # 썸네일 레이블
        self.thumbnail_label = ThumbnailLabel()
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QLabel:hover {
                border-color: #666;
            }
        """)
        self.thumbnail_label.setText("썸네일을 여기에\n드래그 앤 드롭하거나\nCtrl+V로 붙여넣기")
        self.thumbnail_label.thumbnailDropped.connect(self.handle_thumbnail_drop)
        
        right_layout.addRow('카테고리:', self.category)
        right_layout.addRow('날짜:', self.date_edit)
        right_layout.addRow('제목:', self.title)
        right_layout.addRow('설교자:', self.preacher)
        right_layout.addRow('성경구절:', self.bible_verse)
        right_layout.addRow('유튜브:', self.youtube_embed)
        right_layout.addRow('썸네일:', self.thumbnail_label)
        right_layout.addRow('내용:', self.content)
        
        # 클릭으로 적용하기 체크박스
        self.auto_input_checkbox = QCheckBox('클릭으로 적용하기')
        self.auto_input_checkbox.setStyleSheet("""
            QCheckBox {
                padding: 5px;
                font-weight: bold;
            }
            QCheckBox:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # 현재 단계 표시 레이블
        self.step_label = QLabel('')
        self.step_label.setStyleSheet("color: #666;")
        
        # 체크박스와 단계 표시를 위한 레이아웃
        auto_input_layout = QHBoxLayout()
        auto_input_layout.addWidget(self.auto_input_checkbox)
        auto_input_layout.addWidget(self.step_label)
        auto_input_layout.addWidget(self.set_positions_button)
        auto_input_layout.addWidget(self.macro_button)
        auto_input_layout.addWidget(self.parallel_upload_button)
        auto_input_layout.addStretch()
        
        right_layout.addRow('', auto_input_layout)  # 빈 레이블로 첫 번째 열 비워두기
        
        copy_button = QPushButton('클립보드에 복사')
        copy_button.clicked.connect(self.copy_to_clipboard)
        right_layout.addRow(copy_button)
        
        upload_button = QPushButton('웹사이트에 업로드')
        upload_button.clicked.connect(self.upload_to_website)
        right_layout.addRow(upload_button)
        
        right_panel.setLayout(right_layout)
        
        # 레이아웃 설정
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        main_widget.setLayout(layout)
        
        # 체크박스 상태 변경 시그널 연결
        self.auto_input_checkbox.stateChanged.connect(self.handle_auto_input_state)

    def setup_file_list(self):
        """파일 목록 설정"""
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e6f3ff;
                color: black;
            }
        """)
        self.file_list.itemClicked.connect(self.load_sermon)

        # 파일 새로고침 버튼
        refresh_btn = QPushButton('새로고침')
        refresh_btn.clicked.connect(self.refresh_files)
        
        # 완료 항목 토글 버튼
        self.toggle_completed_btn = QPushButton('완료 항목 표시/숨기기')
        self.toggle_completed_btn.clicked.connect(self.toggle_completed_items)
        
        # 버튼 레이아웃
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(self.toggle_completed_btn)
        
        # 파일 목록 레이아웃
        file_list_layout = QVBoxLayout()
        file_list_layout.addLayout(btn_layout)
        file_list_layout.addWidget(self.file_list)
        
        return file_list_layout

    def refresh_files(self):
        """파일 목록 새로고침"""
        self.file_list.clear()
        
        # 완료된 항목 목록 로드
        completed_items = self.load_completed_items()
        
        # 파일 정보를 저장할 리스트
        file_items = []
        
        # 파일 목록 가져오기
        for year_dir in os.listdir(os.path.join('contents', '내용')):
            year_path = os.path.join('contents', '내용', year_dir)
            if os.path.isdir(year_path):
                for file_name in os.listdir(year_path):
                    if file_name.endswith('.rtf'):
                        file_path = os.path.join(year_path, file_name)
                        
                        # 날짜 정보 추출 (YYYYMMDD)
                        try:
                            date_str = file_name.replace('.rtf', '')
                            # 파일명이 올바른 날짜 형식인지 확인
                            if len(date_str) == 8 and date_str.isdigit():
                                is_completed = file_path in completed_items
                                file_items.append({
                                    'path': file_path,
                                    'date': date_str,
                                    'completed': is_completed
                                })
                        except Exception as e:
                            print(f"날짜 파싱 오류 ({file_name}): {e}")
        
        # 날짜순으로 정렬하고 완료되지 않은 항목을 먼저 표시
        file_items.sort(key=lambda x: (x['completed'], x['date']))

        # 리스트에 아이템 추가
        visible_count = 0
        for idx, item_info in enumerate(file_items, 1):
            # 완료된 항목이고 숨김 설정인 경우 건너뛰기
            if item_info['completed'] and not self.show_completed:
                continue
                
            # 날짜 형식 변환
            date_str = item_info['date']
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            
            # 순번과 날짜를 포함한 표시 텍스트 생성
            display_text = f"{idx:03d}. [{formatted_date}] {os.path.basename(item_info['path'])}"
            
            item = QListWidgetItem(display_text)
            # 원본 파일 경로는 userData에 저장
            item.setData(Qt.UserRole, item_info['path'])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if item_info['completed'] else Qt.Unchecked)
            
            # 완료된 항목은 회색으로 표시
            if item_info['completed']:
                item.setForeground(QColor('#888888'))
            
            self.file_list.addItem(item)
            visible_count += 1

        # 파일 개수 업데이트
        total_count = len(file_items)
        self.file_count_label.setText(f'설교 파일 목록 ({visible_count}/{total_count}개)')

    def toggle_completed_items(self):
        """완료된 항목 표시/숨기기 토글"""
        self.show_completed = not getattr(self, 'show_completed', False)
        self.refresh_files()

    def load_completed_items(self):
        """완료된 항목 목록 로드"""
        try:
            if os.path.exists('completed_items.txt'):
                with open('completed_items.txt', 'r', encoding='utf-8') as f:
                    return set(line.strip() for line in f)
        except Exception as e:
            print(f"완료 항목 로드 중 오류: {e}")
        return set()

    def save_completed_items(self):
        """완료된 항목 목록 저장"""
        completed_items = set()
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.checkState() == Qt.Checked:
                completed_items.add(item.text())
                
        try:
            with open('completed_items.txt', 'w', encoding='utf-8') as f:
                for item in completed_items:
                    f.write(f"{item}\n")
        except Exception as e:
            print(f"완료 항목 저장 중 오류: {e}")

    def filter_list(self, text):
        """파일 목록 필터링"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
        
        # 보이는 항목 수 업데이트
        visible_count = sum(1 for i in range(self.file_list.count()) if not self.file_list.item(i).isHidden())
        
        total_count = self.file_list.count()
        self.file_count_label.setText(f'설교 파일 목록 ({visible_count}/{total_count}개)')

    def load_sermon(self, item):
        """설교 정보 로드"""
        try:
            # UserRole에서 실제 파일 경로를 가져옴
            file_path = item.data(Qt.UserRole)
            sermon_info = self.processor.extract_sermon_info(file_path)
            date = self.processor.parse_date(os.path.basename(file_path))
            
            # UI 업데이트
            self.date_edit.setDate(date)
            self.title.setText(sermon_info.get('title', ''))
            self.preacher.setText('최성규 목사')
            self.bible_verse.setText(sermon_info.get('bible_verse', ''))
            
            # 썸네일 표시
            if 'thumbnail' in sermon_info:
                self.thumbnail_label.set_image(sermon_info['thumbnail'])
            else:
                self.thumbnail_label.clear()
                self.thumbnail_label.setText('썸네일 없음')
            
            # YouTube 검색 - 선택된 설교에 대해서만 수행
            if sermon_info.get('title'):
                youtube_url = self.processor.youtube_api.search_sermon(sermon_info['title'], date)
                self.youtube_embed.setText(youtube_url if youtube_url else '')
            
            # 성경 구절 가져오기
            bible_text = self.processor.bible_api.get_verse(sermon_info.get('bible_verse', ''))
            
            # 내용 생성
            content = self.processor.generate_content(sermon_info, date, bible_text)
            self.content.setText(content)
            
        except Exception as e:
            print(f"설교 정보 로드 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    def on_key_press(self, key):
        """키보드 입력 감지"""
        try:
            current_time = time.time()
            
            # 맥에서 Command+V 감지
            if self.is_mac:
                if (isinstance(key, keyboard.Key) and 
                    key in (keyboard.Key.cmd, keyboard.Key.cmd_r)):
                    self.last_paste_time = current_time
                elif (hasattr(key, 'char') and 
                      key.char == 'v' and 
                      current_time - self.last_paste_time < 0.5):
                    self.handle_paste()
            
            # 윈도우에서 Ctrl+V 감지
            else:
                if isinstance(key, keyboard.Key) and key == keyboard.Key.ctrl:
                    self.last_paste_time = current_time
                elif (hasattr(key, 'char') and 
                      key.char == 'v' and 
                      current_time - self.last_paste_time < 0.5):
                    self.handle_paste()
                    
        except AttributeError:
            pass

    def handle_paste(self):
        """붙여넣기 동작 감지 시 처리"""
        if not self.auto_input_checkbox.isChecked() or self.click_count >= 5:
            return
            
        # 약간의 딜레이 후 다음 단계로
        QTimer.singleShot(300, self.move_to_next_step)
        print(f"붙여넣기 감지됨: 현재 단계 {self.click_count}")  # 디버깅용

    def move_to_next_step(self):
        """다음 단계로 이동"""
        if not self.auto_input_checkbox.isChecked():
            return
            
        self.click_count += 1
        print(f"다음 단계로 이동: {self.click_count}")  # 디버깅용
        
        # 모든 단계가 완료되면 체크박스 해제
        if self.click_count >= 5:
            self.auto_input_checkbox.setChecked(False)
            self.click_count = 0
        else:
            self.update_step_label()
            self.prepare_next_input()

    def prepare_next_input(self):
        """다음 입력 준비"""
        if not self.auto_input_checkbox.isChecked():
            return
            
        clipboard = QApplication.clipboard()
        
        # 클립보드에 복사
        if self.click_count == 0:
            clipboard.setText(self.title.text())
        elif self.click_count == 1:
            clipboard.setText(self.preacher.text())
        elif self.click_count == 2:
            clipboard.setText(self.bible_verse.text())
        elif self.click_count == 3:
            clipboard.setText(self.youtube_embed.text())
        elif self.click_count == 4:
            clipboard.setText(self.content.toPlainText())
        
        print(f"클립보드에 복사됨: {clipboard.text()[:30]}...")  # 디버깅용

    def handle_auto_input_state(self, state):
        """클릭으로 적용하기 상태 변경 처리"""
        if state == Qt.Checked:
            self.click_count = 0
            self.update_step_label()
            # 체크박스가 켜지면 바로 첫 번째 내용 복사
            self.prepare_next_input()
        else:
            self.step_label.clear()

    def update_step_label(self):
        """현재 단계 표시 업데이트"""
        steps = [
            '제목 입력 위치 클릭...',
            '설교자 입력 위치 클릭...',
            '본문 입력 위치 클릭...',
            '영상보기 입력 위치 클릭...',
            '내용 입력 위치 클릭...'
        ]
        if self.click_count < len(steps):
            self.step_label.setText(steps[self.click_count])
        else:
            self.step_label.clear()

    def handle_thumbnail_drop(self, image_path):
        """드롭된 썸네일 처리"""
        try:
            # 현재 선택된 파일의 날짜 정보 가져오기
            current_item = self.file_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, '경고', '먼저 설교 파일을 선택해주세요.')
                return

            file_path = current_item.text()
            date_str = os.path.basename(file_path).replace('.rtf', '')
            year = os.path.basename(os.path.dirname(file_path))

            # 썸네일 저장 경로 생성
            thumbnail_dir = os.path.join('contents', '썸네일', year)
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_path = os.path.join(thumbnail_dir, f"{date_str}.jpg")

            # 이미지 처리 및 저장
            image = QImage(image_path)
            if not image.isNull():
                if image.save(thumbnail_path, 'JPEG', 100):
                    # 썸네일 표시 업데이트
                    self.thumbnail_label.set_image(thumbnail_path)
                    QMessageBox.information(self, '성공', '썸네일이 저장되었습니다.')
                else:
                    QMessageBox.warning(None, '오류', '썸네일 저장에 실패했습니다.')
        except Exception as e:
            QMessageBox.warning(self, '오류', f'썸네일 처리 중 오류가 발생했습니다: {str(e)}')

    def copy_to_clipboard(self):
        """클립보드에 복사"""
        clipboard = QApplication.clipboard()
        text = f"""카테고리: {self.category.currentText()}
날짜: {self.date_edit.date().toString('yyyy-MM-dd')}
제목: {self.title.text()}
설교자: {self.preacher.text()}
성경구절: {self.bible_verse.text()}
유튜브: {self.youtube_embed.text()}
내용:
{self.content.toPlainText()}"""
        clipboard.setText(text)
        QMessageBox.information(self, '알림', '클립보드에 복사되었습니다.')

    def closeEvent(self, event):
        """프로그램 종료 시 키보드 리스너 정리"""
        self.keyboard_listener.stop()
        if self.automation:
            self.automation.close()
        event.accept()

    def set_click_positions(self):
        """클릭 위치 설정"""
        self.click_positions = []
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("각 입력 필드를 순서대로 클릭하세요.\n(제목 → 설교자 → 본문 → 영상보기 → 내용)")
        msg.setWindowTitle("입력 위치 설정")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        # 위치 설정 모드 시작
        self.setting_positions = True
        self.position_count = 0
        
        # 전역 마우스 이벤트 리스너 설정
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        """마우스 클릭 위치 저장"""
        if pressed and self.setting_positions:
            self.click_positions.append((x, y))
            self.position_count += 1
            
            if self.position_count >= 5:
                self.setting_positions = False
                self.mouse_listener.stop()
                self.save_click_positions()
                QMessageBox.information(self, '완료', '입력 위치가 저장되었습니다.')
                return False

    def save_click_positions(self):
        """클릭 위치 저장"""
        try:
            with open('click_positions.txt', 'w') as f:
                for pos in self.click_positions:
                    f.write(f"{pos[0]},{pos[1]}\n")
        except Exception as e:
            print(f"위치 저장 중 오류: {e}")

    def load_click_positions(self):
        """저장된 클릭 위치 로드"""
        try:
            if os.path.exists('click_positions.txt'):
                with open('click_positions.txt', 'r') as f:
                    self.click_positions = []
                    for line in f:
                        x, y = map(float, line.strip().split(','))
                        self.click_positions.append((x, y))
        except Exception as e:
            print(f"위치 로드 중 오류: {e}")

    def run_macro(self):
        """매크로 실행"""
        if not self.click_positions or len(self.click_positions) < 5:
            QMessageBox.warning(self, '경고', '먼저 입력 위치를 설정해주세요.')
            return
            
        # 현재 마우스 위치 저장
        original_position = self.mouse.position
        
        try:
            # 각 필드 순차적으로 입력
            for i, pos in enumerate(self.click_positions):
                # 클립보드에 내용 복사
                clipboard = QApplication.clipboard()
                if i == 0:
                    clipboard.setText(self.title.text())
                elif i == 1:
                    clipboard.setText(self.preacher.text())
                elif i == 2:
                    clipboard.setText(self.bible_verse.text())
                elif i == 3:
                    clipboard.setText(self.youtube_embed.text())
                elif i == 4:
                    clipboard.setText(self.content.toPlainText())
                
                # 해당 위치로 마우스 이동 및 클릭
                self.mouse.position = pos
                time.sleep(0.5)  # 잠시 대기
                self.mouse.click(mouse.Button.left)
                time.sleep(0.5)  # 잠시 대기
                
                # 붙여넣기 실행
                if self.is_mac:
                    self.keyboard.press(Key.cmd)
                else:
                    self.keyboard.press(Key.ctrl)
                self.keyboard.press('v')
                self.keyboard.release('v')
                if self.is_mac:
                    self.keyboard.release(Key.cmd)
                else:
                    self.keyboard.release(Key.ctrl)
                
                time.sleep(0.5)  # 다음 동작 전 대기
            
            # 원래 마우스 위치로 복귀
            self.mouse.position = original_position
            
            QMessageBox.information(self, '완료', '매크로 실행이 완료되었습니다.')
            
        except Exception as e:
            QMessageBox.warning(self, '오류', f'매크로 실행 중 오류가 발생했습니다: {str(e)}')

    def upload_to_website(self):
        """웹사이트에 업로드"""
        try:
            # 현재 선택된 아이템 가져오기
            current_item = self.file_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, '경고', '업로드할 설교를 선택해주세요.')
                return
            
            # 파일 경로 가져오기
            file_path = current_item.data(Qt.UserRole)
            date = self.processor.parse_date(os.path.basename(file_path))
            
            # 썸네일 경로 구성
            year = os.path.basename(os.path.dirname(file_path))
            date_str = os.path.splitext(os.path.basename(file_path))[0]
            thumbnail_path = os.path.join('contents', '썸네일', year, f"{date_str}.jpg")
            
            # jpg가 없다면 png 확인
            if not os.path.exists(thumbnail_path):
                thumbnail_path = thumbnail_path.replace('.jpg', '.png')
            
            print(f"썸네일 경로 확인: {thumbnail_path}")
            print(f"썸네일 존재 여부: {os.path.exists(thumbnail_path)}")
            
            # 업로드할 데이터 구성
            sermon_data = {
                'date': date,
                'title': self.title.text(),
                'preacher': self.preacher.text(),
                'bible_verse': self.bible_verse.text(),
                'youtube_url': self.processor.youtube_api.search_sermon(self.title.text(), date),
                'content': self.processor.generate_content(self.processor.extract_sermon_info(file_path), date, 
                    self.processor.bible_api.get_verse(self.bible_verse.text())),
                'thumbnail': thumbnail_path if os.path.exists(thumbnail_path) else None
            }
            
            print(f"업로드할 데이터: {sermon_data}")
            
            # 웹사이트 자동화 시작 (기존 세션 활용)
            self.automation.start_browser()
            
            # 로그인 (이미 로그인된 경우 스킵됨)
            username = os.getenv('WEBSITE_USERNAME')
            password = os.getenv('WEBSITE_PASSWORD')
            
            if self.automation.login(username, password):
                if self.automation.upload_sermon(sermon_data):
                    QMessageBox.information(self, '성공', '업로드가 완료되었습니다.')
                else:
                    QMessageBox.warning(self, '실패', '업로드 중 오류가 발생했습니다.')
            else:
                QMessageBox.warning(self, '실패', '로그인에 실패했습니다.')
            
        except Exception as e:
            print(f"업로드 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, '오류', f'업로드 중 오류가 발생했습니다.\n{str(e)}')
        
        finally:
            # 브라우저 종료 보장
            try:
                if self.automation:
                    self.automation.close()
                    time.sleep(1)  # 완전히 종료될 때까지 대기
            except Exception as e:
                print(f"브라우저 종료 중 추가 오류: {e}")

    def parallel_upload(self):
        """미등록 설교 일괄 업로드"""
        # 현재 선택된 항목 확인
        current_item = self.file_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '알림', '업로드를 시작할 설교를 선택해주세요.')
            return
        
        # 확인 대화상자
        current_number = int(current_item.text().split('.')[0])
        reply = QMessageBox.question(
            self, 
            '확인', 
            f'{current_number}번 설교부터 순차적으로 업로드하시겠습니까?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # 선택된 항목부터 끝까지의 항목들 수집
        upload_items = []
        found_current = False
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if not found_current:
                if item == current_item:
                    found_current = True
                else:
                    continue
            
            if item.checkState() == Qt.Unchecked:  # 미등록 항목만 추가
                upload_items.append(item)
        
        if not upload_items:
            QMessageBox.information(self, '알림', '업로드할 설교가 없습니다.')
            return
        
        print(f"업로드 대상: {len(upload_items)}개 (#{current_number}번부터)")
        
        # 업로드 스레드 시작
        self.upload_thread = threading.Thread(
            target=self.process_uploads, 
            args=(upload_items,)
        )
        self.upload_thread.start()

    def process_uploads(self, items):
        """설교 순차 업로드 처리"""
        try:
            self.current_automation = WebsiteAutomation()
            self.current_automation.start_browser()
            
            username = os.getenv('WEBSITE_USERNAME')
            password = os.getenv('WEBSITE_PASSWORD')
            if not self.current_automation.login(username, password):
                raise Exception("로그인 실패")
            
            for item in items:
                try:
                    file_path = item.data(Qt.UserRole)
                    
                    if file_path in self.sermon_cache:
                        sermon_data = self.sermon_cache[file_path]
                        print(f"캐시된 데이터 사용: {sermon_data['title']}")
                    else:
                        sermon_info = self.processor.extract_sermon_info(file_path)
                        date = self.processor.parse_date(os.path.basename(file_path))
                        youtube_url = self.processor.youtube_api.search_sermon(sermon_info.get('title', ''), date)
                        sermon_data = {
                            'date': date,
                            'title': sermon_info.get('title', ''),
                            'preacher': '최성규 목사',
                            'bible_verse': sermon_info.get('bible_verse', ''),
                            'youtube_url': youtube_url,  # 이미 기본값이 설정되어 있음
                            'content': self.processor.generate_content(sermon_info, date, 
                                self.processor.bible_api.get_verse(sermon_info.get('bible_verse', ''))),
                            'thumbnail': sermon_info.get('thumbnail')
                        }
                        self.sermon_cache[file_path] = sermon_data
                    
                    if self.current_automation.upload_sermon(sermon_data):
                        self.update_item_signal.emit(item)
                        print(f"업로드 성공: {sermon_data['title']}")
                    else:
                        print(f"업로드 실패: {sermon_data['title']}")
                    
                    gc.collect()
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"개별 업로드 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
                    
        except Exception as e:
            print(f"전체 업로드 프로세스 오류: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("업로드 프로세스 완료")
            self.current_automation = None
            gc.collect()

    @pyqtSlot(QListWidgetItem)
    def _update_item_status(self, item):
        """실제 UI 업데이트 수행"""
        try:
            if not sip.isdeleted(item):  # 객체가 유효한지 확인
                item.setCheckState(Qt.Checked)
                item.setForeground(QColor('#888888'))
                self.save_completed_items()
                print(f"항목 상태 업데이트 완료: {item.text()}")
        except Exception as e:
            print(f"UI 업데이트 중 오류: {e}")

class ThumbnailLabel(QLabel):
    """드래그 가능한 썸네일 레이블"""
    thumbnailDropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.current_image_path = None  # 현재 이미지 경로 저장

    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.LeftButton and self.current_image_path:
            # 드래그 시작
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # 파일 URL 설정
            url = QUrl.fromLocalFile(self.current_image_path)
            mime_data.setUrls([url])
            
            # 드래그 이미지 설정
            pixmap = self.pixmap()
            if pixmap:
                drag.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                drag.setHotSpot(QPoint(32, 32))
            
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)

    def dragEnterEvent(self, event):
        """드래그 진입 이벤트"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px solid #4a9eff;
                    border-radius: 5px;
                    background-color: #e6f3ff;
                }
            """)

    def dragLeaveEvent(self, event):
        """드래그 벗어남 이벤트"""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QLabel:hover {
                border-color: #666;
            }
        """)

    def dropEvent(self, event):
        """드롭 이벤트"""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QLabel:hover {
                border-color: #666;
            }
        """)
        
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            
            # 이미지 파일 확인
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.thumbnailDropped.emit(file_path)
            else:
                QMessageBox.warning(None, '오류', '이미지 파일만 허용됩니다.')

    def set_image(self, image_path):
        """이미지 설정"""
        self.current_image_path = image_path
        pixmap = QPixmap(image_path)
        self.setPixmap(pixmap.scaled(320, 180, Qt.KeepAspectRatio))

def main():
    app = QApplication([])
    window = SermonUploaderUI()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()