import sqlite3
from typing import List, Optional
from pydantic import BaseModel

# Pydantic 모델 정의

# Pydantic 모델 정의
class Domain(BaseModel):
    domain_id: str
    domain: str
    source: Optional[str] = None
    platform: Optional[str] = None
    cate1: Optional[str] = None
    cate2: Optional[str] = None
    file_loc: Optional[str] = None
    url: str = "None"
    regi_date: Optional[str] = None
    up_data_time: Optional[str] = None
