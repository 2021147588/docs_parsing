# Pydantic 모델 정의
from pydantic import BaseModel
from typing import Optional

class TableMap(BaseModel):
    log_id: Optional[int] = None
    table_id: str
    table_nm: str
    table_source: Optional[str] = None
    table_src_platform: Optional[str] = None
    cate1: Optional[str] = None
    cate2: Optional[str] = None
    file_loc: Optional[str] = None
    url: str = "None"
    column_cnt: Optional[int] = None
    categorical_cnt: Optional[int] = 0
    numerical_cnt: Optional[int] = 0
    rec_cnt: Optional[int] = None
    table_qty_index: Optional[int] = 0
    regi_date: Optional[str] = None
    cum_search_num: Optional[int] = None
    language: Optional[str] = None
    up_data_time: Optional[str] = None
    insert_flag: int = 0