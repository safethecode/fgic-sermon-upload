import os
import sys
import striprtf.striprtf as striprtf
from datetime import datetime

def convert_rtf_to_txt(input_base_path, output_base_path):
    # 입력 폴더 내의 모든 연도 폴더 확인
    for year_folder in os.listdir(input_base_path):
        year_path = os.path.join(input_base_path, year_folder)
        
        # 폴더가 아닌 경우 건너뛰기
        if not os.path.isdir(year_path):
            continue
            
        # 출력 폴더에 연도 폴더 생성
        output_year_path = os.path.join(output_base_path, year_folder)
        os.makedirs(output_year_path, exist_ok=True)
        
        # 해당 연도 폴더 내의 모든 RTF 파일 처리
        for file_name in os.listdir(year_path):
            if file_name.endswith('.rtf'):
                rtf_path = os.path.join(year_path, file_name)
                
                # RTF 파일 읽기
                with open(rtf_path, 'r', encoding='utf-8') as file:
                    rtf_text = file.read()
                
                # RTF를 일반 텍스트로 변환
                plain_text = striprtf.rtf_to_text(rtf_text)
                
                # 파일명에서 날짜 추출 (YYYYMMDD 형식 가정)
                try:
                    date_str = ''.join(filter(str.isdigit, file_name))[:8]
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    new_file_name = date_obj.strftime('%Y%m%d') + '.txt'
                except:
                    # 날짜 추출 실패시 원본 파일명 사용
                    new_file_name = os.path.splitext(file_name)[0] + '.txt'
                
                # 변환된 텍스트를 새 파일로 저장
                output_path = os.path.join(output_year_path, new_file_name)
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(plain_text)
                
                print(f'Converted: {file_name} -> {new_file_name}')

if __name__ == "__main__":
    # 커맨드 라인 인자 처리
    if len(sys.argv) != 3:
        print("Usage: python3 rtf_to_txt_converter.py <input_path> <output_path>")
        sys.exit(1)
    
    input_base_path = sys.argv[1]
    output_base_path = sys.argv[2]
    
    # 입력 경로가 존재하는지 확인
    if not os.path.exists(input_base_path):
        print(f"Error: Input path '{input_base_path}' does not exist")
        sys.exit(1)
    
    # 출력 기본 폴더가 없다면 생성
    os.makedirs(output_base_path, exist_ok=True)
    
    # 변환 실행
    convert_rtf_to_txt(input_base_path, output_base_path)
    print("Conversion completed!") 