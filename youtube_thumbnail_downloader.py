import os
import requests
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
import re

class YouTubeAPI:
    def __init__(self):
        self.api_keys = [
            'API_KEY를 넣으세요.',
        ]
        self.current_key_index = 0
        self.youtube = self.create_youtube_service()
        self.channel_id = 'UCgeZJWROaoIP3VV2_d7CJlQ'  # @hyotv4508
    
    def create_youtube_service(self):
        return build('youtube', 'v3', developerKey=self.api_keys[self.current_key_index])
    
    def switch_to_next_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.youtube = self.create_youtube_service()
        print(f"YouTube API 키 전환: {self.current_key_index + 1}번째 키로 전환")
    
    def search_sermon(self, title, date):
        for _ in range(len(self.api_keys)):
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
                    return video_id
                    
            except Exception as e:
                if 'quota' in str(e).lower() or '403' in str(e):
                    print(f"API 키 할당량 초과 또는 403 에러. 다음 키로 전환 시도")
                    self.switch_to_next_key()
                    continue
                else:
                    print(f"YouTube API 에러: {e}")
                    break
        return None

def download_thumbnail(video_id, output_path):
    if not video_id:
        return False
    
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(thumbnail_url)
    
    # maxresdefault.jpg가 없는 경우 hqdefault.jpg 시도
    if response.status_code != 200:
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        response = requests.get(thumbnail_url)
    
    if response.status_code == 200:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

def process_sermon_files(base_path, youtube_api):
    target_year = "1986"
    year_path = os.path.join(base_path, '변환', target_year)
    
    if not os.path.isdir(year_path):
        print(f"{target_year}년도 폴더를 찾을 수 없습니다.")
        return
        
    print(f"처리 중인 연도: {target_year}")
    
    # 해당 연도의 썸네일 폴더 생성
    thumbnail_year_path = os.path.join(base_path, '썸네일', target_year)
    os.makedirs(thumbnail_year_path, exist_ok=True)
    
    for file_name in os.listdir(year_path):
        if file_name.endswith('.txt'):
            # 이미 썸네일이 있는지 확인
            thumbnail_path = os.path.join(thumbnail_year_path, file_name.replace('.txt', '.jpg'))
            if os.path.exists(thumbnail_path):
                print(f"이미 존재하는 썸네일 건너뛰기: {file_name}")
                continue
            
            try:
                # TXT 파일에서 제목 추출
                with open(os.path.join(year_path, file_name), 'r', encoding='utf-8') as f:
                    content = f.read()
                    title_match = re.search(r"설교제목\s*:\s*(.*?)[\r\n]", content)
                    if title_match:
                        title = title_match.group(1).strip()
                        
                        # 날짜 파싱
                        date_str = file_name.replace('.txt', '')
                        date = datetime.strptime(date_str, '%Y%m%d')
                        
                        print(f"검색 중: {title} ({date_str})")
                        
                        # YouTube 검색 및 썸네일 다운로드
                        video_id = youtube_api.search_sermon(title, date)
                        if video_id:
                            if download_thumbnail(video_id, thumbnail_path):
                                print(f"썸네일 다운로드 성공: {file_name}")
                            else:
                                print(f"썸네일 다운로드 실패: {file_name}")
                        else:
                            print(f"동영상을 찾을 수 없음: {title}")
                            
            except Exception as e:
                print(f"파일 처리 중 오류 발생 ({file_name}): {e}")

def main():
    load_dotenv()
    youtube_api = YouTubeAPI()
    base_path = 'contents'
    process_sermon_files(base_path, youtube_api)

if __name__ == "__main__":
    main() 