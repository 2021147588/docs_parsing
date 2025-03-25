from typing import List, Dict
import json

from be.bp.services.document_parsing.input_data import input_data
from be.bp.services.document_parsing.document_parsor import DocumentParser
from be.bp.services.document_parsing.word_tokenizer import WordTokenizer
from be.bp.services.document_parsing.analysis_document import compute_token_stats_by_word
from be.bp.views.tokens import SegmentTokens

class DocumentParsingService:
    def __init__(self):
        pass
    
    def tokenize_documents(self, path:str, lang: str) -> List[List[Dict[str, SegmentTokens]]]:
        file_paths = input_data(dir)
        tokens_per_file = []
            
        # 1. 문서를 분할별로 파싱
        parsor = DocumentParser(path)
        segs = parsor.parse_doc_to_seg()
        
        # 2. 분할을 토큰화
        tokenizer = WordTokenizer(segs, lang)
        tokens = tokenizer.tokenization()
        tokens_per_file.append(tokens)
        
        cate1 = 'abc'
        cate2 = 'abcd'
        # 3. 단어 분석
        result = compute_token_stats_by_word(tokens_per_file, path, path, cate1, cate2)
        return tokens_per_file
        
        
if __name__ =="__main__":
    dir = 'D:/2025/parsing/docs_parsing/data/report.pdf'
    process_service = DocumentParsingService()
    data = process_service.tokenize_docs(dir, 'kor')

    # JSON 파일로 저장
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
