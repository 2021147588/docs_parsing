from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class DocumentToken(BaseModel):
    # 문서 토큰 테이블 
    value: str = Field(..., description="문서 내 등장하는 단어")
    document_name: str = Field(..., description="해당 단어가 포함된 문서의 이름")
    col_id: int = Field(..., description="단어가 속한 문서 내 분할 정보 ")
    word_type: str = Field(..., description="단어의 품사 (예: 명사, 동사 등)")
    cate1: str = Field(..., description="문서의 주요 분류 1")
    cate2: str = Field(..., description="문서의 주요 분류 2")
    document_path: str = Field(..., description="해당 문서의 저장 위치")
    pii_type: Optional[str] = Field(None, description="개인정보 여부 (없을 경우 null, 있을 경우 유형 입력)")

    total_cnt: Optional[int] = Field(None, description="전체 도메인에서 단어 발현 빈도")
    domain_cnt: Optional[int] = Field(None, description="도메인 내에서 단어 발현 빈도")
    cate1_cnt: Optional[int] = Field(None, description="문서 분류 1에서 단어 발현 빈도")
    cate2_cnt: Optional[int] = Field(None, description="문서 분류 2에서 단어 발현 빈도")
    doc_cnt: Optional[int] = Field(None, description="문서 내에서 단어 발현 빈도")
    col_cnt: Optional[int] = Field(None, description="해당 단어가 분할 내 등장하는 횟수")

    regi_date: date = Field(..., description="처음 등록된 날짜")
    gap_avg: float = Field(..., description="해당 단어 유격의 평균값")
    gap_sd: float = Field(..., description="해당 단어 유격의 편차값")
    index_list: List[int] = Field(..., description="단어의 유격값 리스트 (등장 인덱스 리스트)")
    index: int