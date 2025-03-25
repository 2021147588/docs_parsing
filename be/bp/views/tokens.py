from typing import Optional, List
from pydantic import BaseModel, Field

class Token(BaseModel):
    """
    하나의 토큰 정보를 담는 모델입니다.
    """
    idx: int = Field(..., description="문서 내 토큰의 순서 인덱스")
    word: str = Field(..., description="토큰 문자열")
    tag: str = Field(..., description="토큰의 품사 태그 (예: 고유명사, 일반명사, 형용사, 동사 등)")
    lang: str = Field(..., description="언어 정보 (예: kor, eng)")
    seg_id: int = Field(..., description="문서 내 분할 인덱스 ID")
    pii_type: Optional[str] = Field(None, description="개인정보 유형 (예: email, phone number 등)")

class SegmentTokens(BaseModel):
    """
    하나의 세그먼트(분할) 안에 있는 토큰 리스트를 담는 모델입니다.
    """
    segment_tokens: List[Token] = Field(..., description="해당 세그먼트 내의 토큰 리스트")
