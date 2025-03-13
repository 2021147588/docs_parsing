from typing import List, Dict
import tqdm

from be.bp.services.tokenize_docs.input_data import input_data
from be.bp.services.tokenize_docs.document_parsor import DocumentParser
from be.bp.services.tokenize_docs.word_tokenizer import WordTokenizer
from be.bp.views.tokens import SegmentTokens
import json

class ProcessService:
    def __init__(self):
        pass
    
    def tokenize_docs(self, path:str, lang: str) -> List[List[Dict[str, SegmentTokens]]]:
        file_paths = input_data(dir)
        tokens_per_file = []
            
        # 1. 문서를 분할별로 파싱
        parsor = DocumentParser(path)
        segs = parsor.parse_doc_to_seg()
        
        # 2. 분할을 토큰화
        tokenizer = WordTokenizer(segs, lang)
        tokens = tokenizer.tokenization()
        tokens_per_file.append(tokens)
        
        return tokens_per_file
            
            
if __name__ =="__main__":
    dir = '/root/docs_parsing/data/report.pdf'
    process_service = ProcessService()
    data = process_service.tokenize_docs(dir, 'kor')

    # JSON 파일로 저장
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
