# Pydantic 모델 정의
from pydantic import BaseModel
from typing import Optional

class ColumnTable(BaseModel):
    log_id: int
    domain_id: str
    col_id: int
    col_name: str
    table_name: str
    table_id: str
    url: str = "None"
    table_source: Optional[str] = None
    table_src_platform: Optional[str] = None
    cate1: Optional[str] = None
    cate2: Optional[str] = None
    num_cat_flag: str = "None"
    distinct_cnt: Optional[int] = None
    min_val: Optional[float] = None
    q1_val: Optional[float] = None
    ave_val: Optional[float] = None
    median_val: Optional[float] = None
    q4_val: Optional[float] = None
    max_val: Optional[float] = None
    null_ratio: str = "None"
    same_ratio: Optional[float] = None
    rec_cnt: Optional[int] = None
    pk_ratio: Optional[float] = None
    regi_date: Optional[str] = None
    cum_search_num: Optional[int] = None
    column_val_file_loc: Optional[str] = None
    language: Optional[str] = None
    up_data_time: Optional[str] = None
