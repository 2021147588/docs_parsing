from typing import List, Dict
import json
import pandas as pd

from be.bp.services.document_token.input_data import input_data
from be.bp.services.document_token.document_parsor import DocumentParser
from be.bp.services.document_token.word_tokenizer import WordTokenizer
from be.bp.services.document_token.analysis_document import compute_token_stats_by_word, enrich_token_frequencies
from be.bp.views.document_token import DocumentToken
from be.bp.repositories.document_token_repository import DocumentTokenRepository

class DocumentParsingService:
    def __init__(self):
        self.document_token_repository = DocumentTokenRepository()

    
    def create_document_token(self, lang, metadata) -> List[DocumentToken]:
        
        name = metadata["file_loc"] # ? document가 필요한 이유유
        source = metadata['source']
        platform = metadata['platform']
        cate1 = metadata['cate1']
        cate2 = metadata['cate2']
        file_loc = metadata['file_loc']
        url = metadata['url']
    
        document_token_list = self._tokenize_document(lang, file_loc, lang, name, cate1, cate2)
        
        row_count = self.document_token_repository.insert_all_document_tokens(document_token_list)

        # 전체 문서 내 토큰 테이블 수치 업데이트
        all_document_tokens = self.document_token_repository.select_all_tokens()
        all_document_tokens_update = enrich_token_frequencies(all_document_tokens)
        
        row_count = self.document_token_repository.update_token_counts(all_document_tokens_update)
        
        return row_count
        
    def _tokenize_document(self, file_path:str, lang: str, name: str, cate1:str, cate2:str) -> List[DocumentToken]:
        """
        path: 폴더 디렉토리
        lang: kor or eng
        metadata: source, platform, cate1, cate2, file_loc, url
        """
        
        tokens_per_file = []
            
        # 1. 문서를 분할별로 파싱
        parsor = DocumentParser(file_path)
        segs = parsor.parse_doc_to_seg()
        
        # 2. 분할을 토큰화
        tokenizer = WordTokenizer(segs, lang)
        tokens = tokenizer.tokenization()
        tokens_per_file.append(tokens)
        
        # 3. 단어 분석
        document_token_list = compute_token_stats_by_word(tokens_per_file, name, file_path, cate1, cate2)
        
        return document_token_list
        
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
