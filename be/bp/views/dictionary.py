from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class MeaningWords(BaseModel):
    word: str = Field(..., description="의미사전에 등록된 단어")
    cate1: str = Field(..., description="단어의 대분류 (예: 전문용어, 키워드, 업종)")
    cate2: str = Field(..., description="단어의 세부 분류 (예: 의료 용어, 법률 용어)")
    importance: Optional[int] = Field(None, description="사용자가 입력한 중요도 (1~5 등급 등)")
    regi_date: date = Field(..., description="최초 단어가 등록된 날짜")
    domain: str = Field(..., description="단어가 속한 도메인")
    domain_id: str = Field(..., description="도메인의 고유 ID")
    add_count: Optional[int] = Field(0, description="단어가 추가된 총 횟수")
    delete_count: Optional[int] = Field(0, description="단어가 삭제된 총 횟수")

class StopWords(BaseModel):
    word: str = Field(..., description="불용어 사전에 사전에 등록된 단어")
    cate1: str = Field(..., description="단어의 대분류 (예: 키워드, 업종)")
    cate2: str = Field(..., description="단어의 세부 분류 (예: 의료 용어, 법률 용어)")
    regi_date: date = Field(..., description="단어가 처음 등록된 날짜 또는 갱신된 날짜")
    domain: str = Field(..., description="단어가 속한 도메인 이름")
    domain_id: str = Field(..., description="도메인의 고유 ID")
    add_count: Optional[int] = Field(0, description="단어가 추가된 총 횟수")
    delete_count: Optional[int] = Field(0, description="단어가 삭제된 총 횟수")