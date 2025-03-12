from typing import TypedDict, Optional, List

class Token(TypedDict):
    """
    토큰
    """
    idx: int # 문서 내 토큰 순서
    token: str # 토큰
    tag: str # 토큰 type (고유명사 or 일반명사 or 형용사 or 동사 or 개인정보보)
    lang: str # eng or kor
    seg_id: int # 분할 index
    personal_information: Optional[str] # 개인정보 typer email, phone number 등등
    gap: int

class SentenceTokens(TypedDict):
    """
    문장별별 토큰
    """
    sentence: str
    tokens: List[Token]
    
class SegmentTokens(TypedDict):
    """
    분할별 토큰
    """
    segment_tokens: List[SentenceTokens]