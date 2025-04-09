from pydantic import BaseModel
from typing import Optional

# Pydantic 모델 정의
class DistinctValue(BaseModel):
    log_id: Optional[int] = None
    col_id: int
    table_id: str
    table_src: Optional[str] = None
    cate1: Optional[str] = None
    cate2: Optional[str] = None
    value: str
    distinct_value: Optional[int] = None
    cate1_list: Optional[str] = None
    cate2_list: Optional[str] = None
