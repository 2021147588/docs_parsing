from typing import List, Dict, Tuple
import json
import pandas as pd
import os

from be.bp.services.document_token.input_data import input_data
from be.bp.services.document_token.document_parsor import DocumentParser
from be.bp.services.document_token.word_tokenizer import WordTokenizer
from be.bp.services.document_token.analysis_document import compute_token_stats_by_word, enrich_token_frequencies
from be.bp.views.document_token import DocumentToken
from be.bp.repositories.document_token_repository import DocumentTokenRepository
from be.bp.services.document_token.input_data import input_data
from be.bp.utils.loggers import setup_logger

logger = setup_logger()

class DocumentParsingService:
    def __init__(self):
        self.document_token_repository = DocumentTokenRepository()

    
    def create_document_token(self, lang, metadata) -> Tuple[int, int]:
        logger.info(f"Start creating document token: {metadata['file_loc']}")

        name = metadata["file_loc"]
        source = metadata['source']
        platform = metadata['platform']
        cate1 = metadata['cate1']
        cate2 = metadata['cate2']
        file_loc = metadata['file_loc']
        url = metadata['url']

        file_dir = file_loc + '/' + cate1 
        logger.info(f"file_dir: {file_dir}")

        file_path_list = input_data(file_dir)
        logger.info(f"{file_dir}에서 찾은 문서 개수: {len(file_path_list)}")

        row_counts = []
        for file_path in file_path_list:
            document_token_list = self._tokenize_document(file_path, lang, name, cate1, cate2)
        
            row_count = self.document_token_repository.insert_all_document_tokens(document_token_list)

            # 전체 문서 내 토큰 테이블 수치 업데이트
            all_document_tokens = self.document_token_repository.select_all_tokens()
            all_document_tokens_update = enrich_token_frequencies(all_document_tokens)
            
            row_count = self.document_token_repository.update_token_counts(all_document_tokens_update)
            row_counts.append(row_count)

        return len(row_counts), sum(row_counts), file_path_list
        
    def _tokenize_document(self, file_path:str, lang: str, name: str, cate1:str, cate2:str) -> List[DocumentToken]:
        """
        path: 폴더 디렉토리
        lang: kor or eng
        metadata: source, platform, cate1, cate2, file_loc, url
        """
        
        tokens_per_file = []
        logger.info(f"Start tokenizing document: {file_path}")
        # 1. 문서를 분할별로 파싱
        parsor = DocumentParser(file_path)
        segs = parsor.parse_doc_to_seg()
        logger.info(f"분할 개수: {len(segs)}")

        # Seg 데이터를 JSON 파일로 저장
        seg_file_path = f"segs/{os.path.basename(file_path)}.json"
        os.makedirs(os.path.dirname(seg_file_path), exist_ok=True)
        with open(seg_file_path, "w", encoding="utf-8") as seg_file:
            json.dump(segs, seg_file, ensure_ascii=False, indent=4)

        # 2. 분할을 토큰화
        tokenizer = WordTokenizer(segs, lang)
        tokens = tokenizer.tokenization()
        tokens_per_file.append(tokens)
        logger.info(f"문서의 토큰 개수: {len(tokens)}")

        # 3. 단어 분석
        document_token_list = compute_token_stats_by_word(tokens_per_file, name, file_path, cate1, cate2)
        logger.info(f"문서의 토큰 테이블 개수: {len(document_token_list)}")

        return document_token_list
    
    def get_segmented_tokens(self, file_path: str) -> List[dict]:
        """
        특정 file_path에 해당하는 DocumentToken과 Seg 데이터를 기반으로
        각 segment에 대해 {segment: segment 내용, tokens: []} 형태의 리스트를 반환합니다.
        """
        # 1. DocumentToken 데이터베이스에서 조회
        document_tokens = self.document_token_repository.get_tokens_by_document_path(file_path)

        # 2. Seg 데이터 JSON 파일에서 로드
        seg_file_path = f"segs/{os.path.basename(file_path)}.json"
        if not os.path.exists(seg_file_path):
            raise FileNotFoundError(f"Seg file not found for path: {seg_file_path}")

        with open(seg_file_path, "r", encoding="utf-8") as seg_file:
            file_segs = json.load(seg_file)  # JSON 파일에서 Seg 데이터 로드

        # 3. 각 segment에 대해 {segment: segment 내용, tokens: []} 생성
        result = []
        for segment_index, segment in enumerate(file_segs):
            col_id = segment_index + 1  # segment index + 1
            segment_dict = {
                "segment": segment,
                "tokens": []
            }

            # DocumentToken 중 col_id가 현재 segment의 col_id와 일치하는 token 추가
            for document_token in document_tokens:
                if document_token.col_id == col_id:
                    segment_dict["tokens"].append([document_token.value, document_token.word_type])

            result.append(segment_dict)

        return result

    def get_tokens_by_word_and_document_path(self, word: str, seg_id: int,  file_path: str) -> List[DocumentToken]:
        """
        특정 file_path에 해당하는 DocumentToken을 반환합니다.
        """
        # DocumentToken 데이터베이스에서 조회
        document_tokens = self.document_token_repository.get_tokens_by_word_and_document_path(word,seg_id, file_path)
        document_tokens_dict = [token.to_dict() for token in document_tokens]


        return document_tokens_dict

    
if __name__ =="__main__":
    dir = 'D:/2025/parsing/docs_parsing/data/report.pdf'
    process_service = DocumentParsingService()
    metadata = {
        "source": "소스",
        "platform": "플랫폼",
        "cate1": "대분류1", 
        "cate2": "대분류2",
        "file_loc": dir,
        "url": "url"
    }
    results = process_service.create_document_token('kor', metadata )

    # JSON 파일로 저장
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)
