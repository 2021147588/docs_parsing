from collections import defaultdict
from typing import List
from datetime import date

import numpy as np

from be.bp.views.tokens import SegmentTokens, Token
from be.bp.views.document_token import DocumentToken
from be.bp.utils.loggers import setup_logger

logger = setup_logger()

def compute_token_stats_by_word(
    parsed_segments: List[SegmentTokens],
    document_name: str,
    document_path: str,
    cate1: str,
    cate2: str
) -> List[DocumentToken]:
    logger.info(f"[analysis_document.py] 문서 내 토큰 테이블 생성 중")
    word_map = defaultdict(lambda: {
            "value": "",
            "word_type": "",
            "document_name": document_name,
            "document_path": document_path,
            "cate1": cate1,
            "cate2": cate2,
            "pii_type": None,
            "regi_date": date.today(),
            "index_list": [],
            "index": 0
        })


    # 1. 단어별 정보 수집
    for segment in parsed_segments:
        for seg in segment:
            for token in seg.segment_tokens:

                word = token.word
                tag = token.tag
                seg_id = token.seg_id
                idx = token.idx
                pii_type = token.pii_type

                entry = word_map[(word, seg_id)]
                entry["value"] = word
                entry["word_type"] = tag
                entry["pii_type"] = pii_type
                entry["index_list"].append(idx)
                entry["index"] = idx
                
            
    # 2. 통계 계산 및 모델 생성
    results = []
    for (word, seg_id), info in word_map.items():
        sorted_indices = sorted(info["index_list"])
        gap_values = [j - i for i, j in zip(sorted_indices[:-1], sorted_indices[1:])]
        gap_avg = float(np.mean(gap_values)) if gap_values else 0.0
        gap_sd = float(np.std(gap_values)) if len(gap_values) > 1 else 0.0

        results.append(DocumentToken(
            value=info["value"],
            word_type=info["word_type"],
            document_name=info["document_name"],
            document_path=info["document_path"],
            cate1=info["cate1"],
            cate2=info["cate2"],
            pii_type=info["pii_type"],
            regi_date=info["regi_date"],
            gap_avg=gap_avg,
            gap_sd=gap_sd,
            index_list=sorted_indices,
            col_id=seg_id,                  # ✅ 하나의 seg_id만
            col_cnt=len(sorted_indices) ,     # ✅ 해당 분할 내 등장 횟수
            index=info['index']
        ))
    logger.info(f"[analysis_document.py] 총 {len(results)}개의 문서 내 토큰 테이블 행 생성")

    return results


def enrich_token_frequencies(tokens: List[DocumentToken]) -> List[DocumentToken]:
    # 1. 그룹핑: 단어별 등장 횟수 통계용
    total_counter = defaultdict(int)
    domain_counter = defaultdict(int)
    cate1_counter = defaultdict(int)
    cate2_counter = defaultdict(int)
    doc_counter = defaultdict(int)

    # 먼저 각 그룹에 대해 단어별로 count 누적
    for token in tokens:
        key = token.value

        total_counter[key] += token.col_cnt or 0
        domain_counter[(key, token.document_name)] += token.col_cnt or 0
        cate1_counter[(key, token.cate1)] += token.col_cnt or 0
        cate2_counter[(key, token.cate2)] += token.col_cnt or 0
        doc_counter[(key, token.document_name)] += token.col_cnt or 0  # 문서 내 count

    # 2. 각 토큰에 해당 통계정보 넣기
    for token in tokens:
        key = token.value

        token.total_cnt = total_counter[key]
        token.domain_cnt = domain_counter[(key, token.document_name)]
        token.cate1_cnt = cate1_counter[(key, token.cate1)]
        token.cate2_cnt = cate2_counter[(key, token.cate2)]
        token.doc_cnt = doc_counter[(key, token.document_name)]

    return tokens

if __name__ == "__main__":
    
    # parsed_segments = [
    #     SegmentTokens(segment_tokens=[
    #         Token(idx=0, word='Google', tag='alphabet', lang='kor', seg_id=1),
    #         Token(idx=1, word='AI', tag='alphabet', lang='kor', seg_id=1),
    #         Token(idx=2, word='분야', tag='noun', lang='kor', seg_id=1),
    #         Token(idx=3, word='선도', tag='noun', lang='kor', seg_id=1),
    #         Token(idx=5, word='선도', tag='noun', lang='kor', seg_id=1),
    #         Token(idx=7, word='선도', tag='noun', lang='kor', seg_id=1),
    #         Token(idx=8, word='있', tag='adjective', lang='kor', seg_id=1),
    #     ]),
    #     SegmentTokens(segment_tokens=[
    #         Token(idx=10, word='Google', tag='alphabet', lang='kor', seg_id=2),
    #         Token(idx=11, word='AI', tag='alphabet', lang='kor', seg_id=2),
    #         Token(idx=12, word='분야', tag='noun', lang='kor', seg_id=2),
    #         Token(idx=13, word='선도', tag='noun', lang='kor', seg_id=2),
    #         Token(idx=17, word='선도', tag='noun', lang='kor', seg_id=2),
    #         Token(idx=18, word='있', tag='adjective', lang='kor', seg_id=2),
    #     ]),
    #     SegmentTokens(segment_tokens=[
    #         Token(idx=20, word='Google', tag='alphabet', lang='kor', seg_id=3),
    #         Token(idx=21, word='AI', tag='alphabet', lang='kor', seg_id=3),
    #         Token(idx=22, word='분야', tag='noun', lang='kor', seg_id=3),
    #         Token(idx=23, word='선도', tag='noun', lang='kor', seg_id=3),
    #         Token(idx=28, word='있', tag='adjective', lang='kor', seg_id=3),
    #     ])
    # ]

    # stats = compute_token_stats_by_word(
    #     parsed_segments=parsed_segments,
    #     document_name='AGI',
    #     document_path='D:/2025/parsing',
    #     cate1='기술',
    #     cate2='AI'
    # )

    # for stat in stats:
    #     print(stat.model_dump())  # model_dump()는 Pydantic v2 기준
    
    all_document_token_list = [
        DocumentToken(value='Google', document_name='AGI', col_id=1, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[0], index=0), 
        DocumentToken(value='AI', document_name='AGI', col_id=1, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[1], index=1), 
        DocumentToken(value='분야', document_name='AGI', col_id=1, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[2], index=2), 
        DocumentToken(value='선도', document_name='AGI', col_id=1, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=3, regi_date=date(2025, 3, 26), gap_avg=2.0, gap_sd=0.0, index_list=[3, 5, 7], index=7), 
        DocumentToken(value='있', document_name='AGI', col_id=1, word_type='adjective', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[8], index=8), 
        DocumentToken(value='Google', document_name='AGI', col_id=2, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[10], index=10), 
        DocumentToken(value='AI', document_name='AGI', col_id=2, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[11], index=11), 
        DocumentToken(value='분야', document_name='AGI', col_id=2, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[12], index=12), 
        DocumentToken(value='선도', document_name='AGI', col_id=2, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=2, regi_date=date(2025, 3, 26), gap_avg=4.0, gap_sd=0.0, index_list=[13, 17], index=17), 
        DocumentToken(value='있', document_name='AGI', col_id=2, word_type='adjective', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[18], index=18), 
        DocumentToken(value='Google', document_name='AGI', col_id=3, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[20], index=20), 
        DocumentToken(value='선도', document_name='AGI', col_id=3, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[23], index=23), 
        DocumentToken(value='있', document_name='AGI', col_id=3, word_type='adjective', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=None, domain_cnt=None, cate1_cnt=None, cate2_cnt=None, doc_cnt=None, col_cnt=1, regi_date=date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[28], index=28)
        ]
    
    result = enrich_token_frequencies(all_document_token_list)
    print(result)