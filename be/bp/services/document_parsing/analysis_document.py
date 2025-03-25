from collections import defaultdict
from typing import List
from datetime import date

import numpy as np

from datetime import datetime
from be.bp.views.tokens import SegmentTokens, Token
from be.bp.views.document_token import DocumentToken

def compute_token_stats_by_word(
    parsed_segments: List[SegmentTokens],
    document_name: str,
    document_path: str,
    cate1: str,
    cate2: str
) -> List[DocumentToken]:

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
        "col_id": set()
    })

    # 1. 단어별 정보 수집
    for segment in parsed_segments:
        for token in segment.segment_tokens:
            word = token.word
            tag = token.tag
            seg_id = token.seg_id
            idx = token.idx
            pii_type = token.pii_type

            entry = word_map[word]
            entry["value"] = word
            entry["word_type"] = tag
            entry["pii_type"] = pii_type
            entry["index_list"].append(idx)
            entry["col_id"].add(seg_id)

    # 2. 통계 계산 및 모델 생성
    results = []
    for word, info in word_map.items():
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
            col_id=list(info["col_id"])
        ))

    return results

if __name__ == "__main__":
    
    parsed_segments = [
        SegmentTokens(segment_tokens=[
            Token(idx=0, word='Google', tag='alphabet', lang='kor', seg_id=1),
            Token(idx=1, word='AI', tag='alphabet', lang='kor', seg_id=1),
            Token(idx=2, word='분야', tag='noun', lang='kor', seg_id=1),
            Token(idx=3, word='선도', tag='noun', lang='kor', seg_id=1),
            Token(idx=5, word='선도', tag='noun', lang='kor', seg_id=1),
            Token(idx=7, word='선도', tag='noun', lang='kor', seg_id=1),
            Token(idx=8, word='있', tag='adjective', lang='kor', seg_id=1),
        ]),
        SegmentTokens(segment_tokens=[
            Token(idx=10, word='Google', tag='alphabet', lang='kor', seg_id=2),
            Token(idx=11, word='AI', tag='alphabet', lang='kor', seg_id=2),
            Token(idx=12, word='분야', tag='noun', lang='kor', seg_id=2),
            Token(idx=13, word='선도', tag='noun', lang='kor', seg_id=2),
            Token(idx=17, word='선도', tag='noun', lang='kor', seg_id=2),
            Token(idx=18, word='있', tag='adjective', lang='kor', seg_id=2),
        ]),
        SegmentTokens(segment_tokens=[
            Token(idx=20, word='Google', tag='alphabet', lang='kor', seg_id=3),
            Token(idx=21, word='AI', tag='alphabet', lang='kor', seg_id=3),
            Token(idx=22, word='분야', tag='noun', lang='kor', seg_id=3),
            Token(idx=23, word='선도', tag='noun', lang='kor', seg_id=3),
            Token(idx=28, word='있', tag='adjective', lang='kor', seg_id=3),
        ])
    ]

    stats = compute_token_stats_by_word(
        parsed_segments=parsed_segments,
        document_name='AGI',
        document_path='D:/2025/parsing',
        cate1='기술',
        cate2='AI'
    )

    for stat in stats:
        print(stat.model_dump())  # model_dump()는 Pydantic v2 기준