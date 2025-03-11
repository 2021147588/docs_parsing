from typing import List
import os

def input_data(directory: str) -> List[str]:
    file_paths = []  # 파일 경로를 저장할 리스트

    # 디렉토리 내의 모든 항목을 탐색
    for root, dir, files in os.walk(directory):
        
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    return file_paths

if __name__ == "__main__":
    print(input_data("/root/parsing/data"))