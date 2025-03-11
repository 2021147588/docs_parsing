from typing import List, Dict
from pathlib import Path

from ...views.tokens import SegmentTokens



from collections import defaultdict


stopwords_file = '../stopwords/stopwords-ko.txt'

class DictionaryBuilder: 
    """
    의미사전, 불용어 사전에 토큰 저장하는 클래스
    """
    
    def __init__(self, tokens: List[Dict[str, SegmentTokens]]):
        
        """
        param
        tokens: 전체 문서를 문단 단위로 """
       
        self.tokens = tokens
        self.stopwords = self._make_stopword_set()
        self.semantic_dict = []
        self.file_path = file_path
        self.doc_cate1, self.doc_cate2 = self._extract_category()
        
    def _make_stopword_set(self) -> set[str]:
        """
        기본 불용어 사전 제작작
        """
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            stopwords = set(f.read().splitlines())  # 불용어를 집합(set)으로 저장
        return stopwords
    
    def _extract_category(self) -> tuple[str]:
        """
        상위디렉토리 두개(cate1, cate2) 반환
        """
        p = Path(self.file_pah).resolve()  # 절대 경로 변환
        
        return p.parents[1].name, p.parents[0].name  # 상위 두 개 디렉토리 이름 반환

        
    def count_word_freq(self):
        
        
        result = []
        
        # 토큰 리스트에서 각 세그먼트 처리
        for seg_id, token in enumerate(self.tokens, start=1):
            word_counts = defaultdict(lambda: {
                'count': 0, 'tag': '', 'type1': self.doc_type1, 'type2': self.doc_type2, 'id': seg_id
            })

            for t in token:
                word = t['text']
                tag = t['tag']
                category = pos_tag_map.get(tag)  # 태그에 따른 카테고리 매핑
                
                if category:
                    word_counts[word]['count'] += 1
                    word_counts[word]['tag'] = category

            result.append(dict(word_counts))  # defaultdict을 일반 dict로 변환 후 저장


        return result
                
                
    
    
if __name__=='__main__':
    # 주어진 데이터
    data = [
        [{'text': '받', 'tag': 'VV-R', 'lang': 'kor'}, {'text': '고', 'tag': 'EC', 'lang': 'kor'},
        {'text': '있', 'tag': 'VX', 'lang': 'kor'}, {'text': '습니다', 'tag': 'EF', 'lang': 'kor'},
        {'text': '.', 'tag': 'SF', 'lang': 'kor'}, {'text': '주요', 'tag': 'NNG', 'lang': 'kor'},
        {'text': 'AI', 'tag': 'SL', 'lang': 'kor'}, {'text': '연구', 'tag': 'NNG', 'lang': 'kor'},
        {'text': '기관', 'tag': 'NNG', 'lang': 'kor'}, {'text': '들', 'tag': 'XSN', 'lang': 'kor'},
        {'text': '은', 'tag': 'JX', 'lang': 'kor'}, {'text': 'AGI', 'tag': 'SL', 'lang': 'kor'}],
        [{'text': '개발', 'tag': 'NNG', 'lang': 'kor'}, {'text': '을', 'tag': 'JKO', 'lang': 'kor'},
        {'text': '최', 'tag': 'XPN', 'lang': 'kor'}, {'text': '우선', 'tag': 'NNG', 'lang': 'kor'},
        {'text': '목표', 'tag': 'NNG', 'lang': 'kor'}, {'text': '로', 'tag': 'JKB', 'lang': 'kor'},
        {'text': '설정', 'tag': 'NNG', 'lang': 'kor'}, {'text': '하', 'tag': 'XSV', 'lang': 'kor'},
        {'text': '고', 'tag': 'EC', 'lang': 'kor'}, {'text': ',', 'tag': 'SP', 'lang': 'kor'},
        {'text': '이', 'tag': 'NP', 'lang': 'kor'}, {'text': '를', 'tag': 'JKO', 'lang': 'kor'}],
        [{'text': '위하', 'tag': 'VV', 'lang': 'kor'}, {'text': 'ᆫ', 'tag': 'ETM', 'lang': 'kor'},
        {'text': '다양', 'tag': 'NNG', 'lang': 'kor'}, {'text': '하', 'tag': 'XSA', 'lang': 'kor'},
        {'text': 'ᆫ', 'tag': 'ETM', 'lang': 'kor'}, {'text': '접근법', 'tag': 'NNG', 'lang': 'kor'},
        {'text': '을', 'tag': 'JKO', 'lang': 'kor'}, {'text': '모색', 'tag': 'NNG', 'lang': 'kor'},
        {'text': '중', 'tag': 'NNB', 'lang': 'kor'}, {'text': '이', 'tag': 'VCP', 'lang': 'kor'},
        {'text': 'ᆸ니다', 'tag': 'EF', 'lang': 'kor'}, {'text': '.', 'tag': 'SF', 'lang': 'kor'}]
    ]
    
    