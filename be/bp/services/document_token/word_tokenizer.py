from typing import List, Literal, Dict

from kiwipiepy import Kiwi

from bp.views.tokens import Token, SegmentTokens
from config import stopwords_file
from bp.utils.loggers import setup_logger

logger = setup_logger()
pos_tag_dict = {
    "NNG": "noun",        # 일반 명사
    "NNP": "proper_noun",  # 고유 명사
    "VV": "verb",          # 동사
    "SL": "alphabet",
    "VA": "adjective"
}
personal_information_tag_dict = {
    "W_EMAIL": "이메일 주소",       # 이메일 주소
    "W_SERIAL": "일련번호(전화번호, 통장번호, IP주소 등)",  # 일련번호 (전화번호, IP 등)
}


class WordTokenizer:
    """
    1. 일반명사, 고유명사, 용언 추출
    2. 기본 불용어 사전으로 불용어 제거
    """
    
    def __init__(self, segments: List[str], lang: Literal['kor', 'eng']):
        self.segments = segments
        self.kiwi = Kiwi()
        self.lang = lang
        self.stopword = self._make_stopword_set()
        self.token_positions = {}  # {token: 마지막 등장 인덱스} 저장

    def tokenization(self) -> List[SegmentTokens]:
        
        if self.lang == 'kor': 
            tokens = self.tokenization_kor()
        # elif self.lang == 'eng':
        #     tokens = self.tokenization_eng()
        else: 
            raise ValueError(f"Not supported language: {self.lang}")
        
        return tokens
    
    def _make_stopword_set(self) -> set[str]:
        """
        기본 불용어 사전 제작
        """
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            stopwords = set(f.read().splitlines())  # 불용어를 집합(set)으로 저장
        return stopwords
    
    def _tokenize_seg(self, start_index: int, seg: str, seg_id: int) -> SegmentTokens: 
        
        words = seg.split(' ')

        index = start_index # 단어 인덱스
        seg_tokens=[]
        for word in words: 
            tokens = self.kiwi.tokenize(word)
            for t in tokens:
                # 불용어 제거
                if t.form in self.stopword: continue 
    
                self.token_positions[t.form] = index
                    
                if t.tag in pos_tag_dict.keys(): # 명사, 동사 추출
                    
                    s_t = Token(idx=index, word=t.form, tag=pos_tag_dict[t.tag], lang=self.lang, seg_id=seg_id)
                    seg_tokens.append(s_t)
                elif t.tag in personal_information_tag_dict.keys(): # 개인정보 추출
                    s_t = Token(idx=index, word=t.form, tag="개인 정보", lang=self.lang, seg_id=seg_id, personal_infromation=personal_information_tag_dict[t.tag])
                    seg_tokens.append(s_t)
                else:
                    s_t = Token(idx=index, word=t.form, tag="기타", lang=self.lang, seg_id=seg_id)
                    seg_tokens.append(s_t)
                    
            index+=1

        return SegmentTokens(segment_tokens=seg_tokens), index
    


    def tokenization_kor(self) -> List[SegmentTokens]:
        """
        한국어 문장을 형태소 분석하고, 명사(Noun), 형용사, 동사(Verb), 개인정보보 토큰만 추출하는 함수
        :return: 문장과 해당 문장의 토큰 정보를 포함하는 리스트
        예시:
        [{'sentence': "'Google DeepMind 는  AI 분야를 선도하고 있습니다.'", 
        'tokens': [
            {'word': '분야', 'tag': 'noun', 'lang': 'kor', 'seg_id': 1, 'gap': 0}, 
            {'word': '선도', 'tag': 'noun', 'lang': 'kor', 'seg_id': 1, 'gap': 0}]}
        """
        
        doc_tokens = []
        seg_i = 1 # 분할 index는 1부터 시작
        start_index = 0 # 단어의 index
        logger.info(f"[word_tokenizer.py] 문서 토큰화 시작")

        for seg in self.segments:
            seg_tokens, index = self._tokenize_seg(start_index, seg, seg_i)
            start_index = index+1
            doc_tokens.append(seg_tokens)           
            seg_i+=1
        logger.info(f"[word_tokenizer.py] 문서 토큰화 완료. {len(doc_tokens)}개의 문서 토큰 생성")

        
        return doc_tokens
     

    
if __name__=='__main__':
    segments_kor = [
        """Google은 AI 분야를 선도하고, 또 선도하고, 계속 선도하고 있습니다.""",
        """Google은 AI 분야를 선도하고, 또 선도하고, 계속 선도하고 있습니다.""",
        """Google은 AI 분야를 선도하고, 또 선도하고, 계속 선도하고 있습니다."""
    ]
    
    wt = WordTokenizer(segments_kor, 'kor')
    result = wt.tokenization()
    print(result)
    
    # sentence_data = {
    #     "sentence": "저는 키위를 좋아하는 형태소 분석기 키위입니다.",
    #     "tokens": [
    #         {"token": "저", "tag": "대명사", "lang": "kor", "seg_id": 1, "personal_information": None},
    #         {"token": "키위", "tag": "일반명사", "lang": "kor", "seg_id": 1, "personal_information": None},
    #         {"token": "형태소", "tag": "일반명사", "lang": "kor", "seg_id": 1, "personal_information": None},
    #         {"token": "분석기", "tag": "일반명사", "lang": "kor", "seg_id": 1, "personal_information": None},
    #         {"token": "키위", "tag": "일반명사", "lang": "kor", "seg_id": 1, "personal_information": None},
    #     ]
    # }

    # 첫 번째 문장이므로 start_index = 0
    # print(wt._calculate_token_index(0, sentence_data))
