# Pydantic 모델 정의
from pydantic import BaseModel
from typing import Optional

class ColumnMap(BaseModel):
    log_id: Optional[int] = None
    land_no: Optional[int] = None
    col_id: int
    col_name: str
    table_id: str
    table_name: str
    url: Optional[str] = None
    table_source: Optional[str] = None
    table_src_platform: Optional[str] = None
    cate1: Optional[str] = None
    cate2: Optional[str] = None
    num_cat_flag: Optional[str] = None
    distinct_cnt: Optional[int] = None
    min_val: Optional[float] = None
    q1_val: Optional[float] = None
    ave_val: Optional[float] = None
    q4_val: Optional[float] = None
    max_val: Optional[float] = None
    null_ratio: Optional[str] = None
    same_ratio: Optional[float] = None
    column_cnt: Optional[int] = None
    categorical_cnt: Optional[int] = 0
    numerical_cnt: Optional[int] = 0
    rec_cnt: Optional[int] = None
    table_qty_index: Optional[int] = 0
    table_dom_sum: Optional[int] = None
    median_val: Optional[float] = None
    language: Optional[str] = None
    pk_ratio: Optional[float] = None
    regi_date: Optional[str] = None
    cum_search_num: Optional[int] = None
    column_val_file_loc: Optional[str] = None
    up_data_time: Optional[str] = None
