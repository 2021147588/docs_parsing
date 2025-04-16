from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DocumentTokenDB(Base):
    __tablename__ = 'document_tokens'

    id = Column(Integer, primary_key=True)
    value = Column(String(255), nullable=False)
    word_type = Column(String(50))
    col_id = Column(Integer)
    col_cnt = Column(Integer)
    total_cnt = Column(Integer)  # 전체 문서에서의 발생 횟수
    cate1_cnt = Column(Integer)  # 대분류1에서의 발생 횟수
    cate2_cnt = Column(Integer)  # 대분류2에서의 발생 횟수
    doc_cnt = Column(Integer)    # 현재 문서에서의 발생 횟수
    cate1 = Column(String(255))
    cate2 = Column(String(255))
    document_path = Column(String(255))
    document_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    pii_type = Column(String(50))
    regi_date = Column(DateTime)
    gap_avg = Column(Float)
    gap_sd = Column(Float)
    index_list = Column(JSON)
    index = Column(Integer)

class DocumentToken(BaseModel):
    value: str = Field(..., description="문서 내 등장하는 단어")
    document_name: str = Field(..., description="해당 단어가 포함된 문서의 이름")
    col_id: int = Field(..., description="단어가 속한 문서 내 분할 정보")
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