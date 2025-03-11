from tokenize_docs.input_data import input_data
from tokenize_docs.document_parsor import DocumentParser
from tokenize_docs.word_tokenizer import WordTokenizer
class ProcessService:
    def __init__(self):
        pass
    
    def tokenize_docs(self, dir:str, lang: str) -> List[List[Dict[str, SegmentTokens]]]:
        file_paths = input_data(dir)
        tokens_per_file = []
        for path in file_paths:
            
            # 1. 문서를 분할별로 파싱
            parsor = DocumentParser(path)
            segs = parsor.parse_doc_to_seg()
            
            # 2. 분할을 토큰화
            tokenizer = WordTokenizer(segs, lang)
            tokens = tokenizer.tokenization()
            tokens_per_file.append(tokens)
        
        return tokens_per_file
            