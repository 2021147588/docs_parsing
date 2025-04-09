# Pydantic 모델 정의

import sqlite3
from typing import List, Optional
from pydantic import BaseModel


class Document(BaseModel):
    log_id: Optional[int] = None
    domain_id: str
    table_id: str
    table_nm: str
    table_source: Optional[str] = None
    table_src_platform: Optional[str] = None
    cate1: Optional[str] = None
    cate2: Optional[str] = None
    file_loc: Optional[str] = None
    url: str = "None"
    column_cnt: Optional[int] = None
    categorical_cnt: Optional[int] = None
    numerical_cnt: Optional[int] = None
    rec_cnt: Optional[int] = None
    table_qty_index: Optional[int] = None
    regi_date: Optional[str] = None
    cum_search_num: Optional[int] = None
    language: Optional[str] = None
    up_data_time: Optional[str] = None
    before_parsing_cnt: Optional[int] = None
    after_parsing_cnt: Optional[int] = None
    insert_flag: int = 0