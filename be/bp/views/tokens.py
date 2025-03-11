from typing import TypedDict, Optional

class SegmentTokens(TypedDict):
    """
    분할 안에 있는 토큰"""
    token: str # 토큰
    tag: str # 토큰 type (고유명사 or 일반명사 or 형용사 or 동사 or 개인정보보)
    lang: str # eng or kor
    seg_id: int # 분할 index
    personal_information: Optional[str] # 개인정보 typer email, phone number 등등

