from typing import List
import os

def input_data(directory: str) -> List[str]:
    file_paths = []  # 파일 경로를 저장할 리스트

    # 디렉토리 내의 모든 항목을 탐색
    for root, dir, files in os.walk(directory):
        
        for file in files:
            # 파일의 절대 경로를 생성하여 리스트에 추가
            file_paths.append(file)

    return file_paths

if __name__ == "__main__":
    print(input_data("/root/data"))