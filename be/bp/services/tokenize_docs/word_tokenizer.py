from typing import List, Literal, Dict
from collections import defaultdict

from kiwipiepy import Kiwi

import spacy
import re

from be.bp.views.tokens import SegmentTokens
from be.config import stopwords_file

pos_tag_dict = {
    "NNG": "noun",        # 일반 명사
    "NNP": "proper_noun",  # 고유 명사
    "VV": "verb",          # 동사
    "VA": "adjective",     # 형용사
    "SL": "alphabet"
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
    
    def tokenization(self) -> List[Dict[str, SegmentTokens]]:
        
        if self.lang == 'kor': 
            tokens = self.tokenization_kor()
        # elif self.lang == 'eng':
        #     tokens = self.tokenization_eng()
        else: 
            raise ValueError(f"Not supported language: {self.lang}")
        
        return tokens
    
    def _make_stopword_set(self) -> set[str]:
        """
        기본 불용어 사전 제작작
        """
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            stopwords = set(f.read().splitlines())  # 불용어를 집합(set)으로 저장
        return stopwords
    
    def _split_seg_to_sentences(self, seg: str):
        """
        문단을 문장으로 나눔
        """
        sentences = re.split(r'(?<!\w\.\w)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s', seg)
        
        return [s.strip() for s in sentences if s.strip()]
        
    def _tokenize_sentence(self, sentence: str, seg_id: int): 
        
        tokens = self.kiwi.tokenize(sentence)

        seg_tokens = []
        for t in tokens:
            if t.form in self.stopword: continue # 불용어 제거
            
            if t.tag in pos_tag_dict.keys(): # 명사, 동사, 형용사 추출
                seg_t = SegmentTokens(word=t.form, tag=pos_tag_dict[t.tag], lang=self.lang, seg_id=seg_id)
                seg_tokens.append(seg_t)
            elif t.tag in personal_information_tag_dict.keys(): # 개인정보 추출
                seg_t = SegmentTokens(word=t.form, tag="개인 정보", lang=self.lang, seg_id=seg_id, personal_infromation=personal_information_tag_dict[t.tag])
                seg_tokens.append(seg_t)
        return seg_tokens
    
    def _calculate_token_gap(self, sentence_tokens:List[Dict[str, SegmentTokens]]):
        """
        동일한 단어가 문장에서 여러 번 등장할 경우, 앞서 나온 단어와의 위치 차이를 'gap' 키에 저장하는 함수.
        :param sentence_tokens: 문장과 해당 문장의 토큰 리스트가 포함된 리스트
        :return: 각 단어의 'gap' 값을 포함한 새로운 리스트
        """
        for sentence_data in sentence_tokens:
            token_positions = {}  # 단어별 마지막 등장 위치 저장
            for idx, token in enumerate(sentence_data["tokens"]):
                word = token["word"]

                if word in token_positions:
                    # 이전 위치와의 차이를 gap으로 설정
                    token["gap"] = idx - token_positions[word]
                else:
                    # 처음 등장하는 단어는 gap을 0으로 설정
                    token["gap"] = 0

                # 단어의 마지막 등장 위치 업데이트
                token_positions[word] = idx

        return sentence_tokens
    
    def tokenization_kor(self) -> List[Dict[str, SegmentTokens]]:
        """
        한국어 문장을 형태소 분석하고, 명사(Noun), 형용사, 동사(Verb), 개인정보보 토큰만 추출하는 함수
        :return: 문장과 해당 문장의 토큰 정보를 포함하는 리스트
        예시:
        [{'sentence': "'Google DeepMind 는  AI 분야를 선도하고 있습니다.'", 
        'tokens': [
            {'word': '분야', 'tag': 'noun', 'lang': 'kor', 'seg_id': 1, 'gap': 0}, 
            {'word': '선도', 'tag': 'noun', 'lang': 'kor', 'seg_id': 1, 'gap': 0}]}
        """
        
        sentence_tokens = []
        seg_i = 1 # 분할 index는 1부터 시작
        for seg in self.segments:
             
            # 1. 문단을 문장으로 나눔
            sentences = self._split_seg_to_sentences(seg)
            
            # 2. 문장별로 kiwi를 돌림 & 명사, 동사 토큰만 추출
            for sentence in sentences:
                seg_tokens = self._tokenize_sentence(sentence, seg_i)
                
            sentence_tokens.append({
                    "sentence": sentence,
                    "tokens": seg_tokens
                })
            seg_i+=1
        result = self._calculate_token_gap(sentence_tokens)
            
        return result
    
if __name__=='__main__':
    segments_kor = [
        """
        'Google DeepMind는 AI 분야를 선도하고, 또 선도하고, 계속 선도하고 있습니다.' """
    ]
    
    wt = WordTokenizer(segments_kor, 'kor')
    print(wt.tokenization())