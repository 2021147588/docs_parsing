from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from bp.dbms import get_db
from bp.utils.loggers import setup_logger

logger = setup_logger()


# Repository 클래스
class ColumnMapRepository:
    def __init__(self):
        try:
            self.conn = get_db()
            self.cursor = self.conn.cursor()
            self._create_table_if_not_exists()
        except Exception as e:
            logger.error(f"[DB 연결 오류] {e}")
            raise

    def _create_table_if_not_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS column_map (
            log_id INTEGER,
            land_no INTEGER,
            col_id INTEGER,
            col_name TEXT,
            table_id TEXT,
            table_name TEXT,
            url TEXT,
            table_source TEXT,
            table_src_platform TEXT,
            cate1 TEXT,
            cate2 TEXT,
            num_cat_flag TEXT,
            distinct_cnt INTEGER,
            min_val REAL,
            q1_val REAL,
            ave_val REAL,
            q4_val REAL,
            max_val REAL,
            null_ratio TEXT,
            same_ratio REAL,
            column_cnt INTEGER,
            categorical_cnt INTEGER DEFAULT 0,
            numerical_cnt INTEGER DEFAULT 0,
            rec_cnt INTEGER,
            table_qty_index INTEGER DEFAULT 0,
            table_dom_sum INTEGER,
            median_val REAL,
            language TEXT,
            pk_ratio REAL,
            regi_date TEXT,
            cum_search_num INTEGER,
            column_val_file_loc TEXT,
            up_data_time TEXT
        )
        """
        self.cursor.execute(query)

    def insert_column_map(self, col: ColumnMap) -> int:
        try:
            query = """
            INSERT INTO column_map (
                log_id, land_no, col_id, col_name, table_id, table_name, url,
                table_source, table_src_platform, cate1, cate2, num_cat_flag,
                distinct_cnt, min_val, q1_val, ave_val, q4_val, max_val, null_ratio,
                same_ratio, column_cnt, categorical_cnt, numerical_cnt, rec_cnt,
                table_qty_index, table_dom_sum, median_val, language, pk_ratio,
                regi_date, cum_search_num, column_val_file_loc, up_data_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                col.log_id, col.land_no, col.col_id, col.col_name, col.table_id, col.table_name, col.url,
                col.table_source, col.table_src_platform, col.cate1, col.cate2, col.num_cat_flag,
                col.distinct_cnt, col.min_val, col.q1_val, col.ave_val, col.q4_val, col.max_val, col.null_ratio,
                col.same_ratio, col.column_cnt, col.categorical_cnt, col.numerical_cnt, col.rec_cnt,
                col.table_qty_index, col.table_dom_sum, col.median_val, col.language, col.pk_ratio,
                col.regi_date or datetime.now().isoformat(),
                col.cum_search_num, col.column_val_file_loc, col.up_data_time or datetime.now().isoformat()
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"[컬럼 지도 삽입 오류] {e}")
            self.conn.rollback()
            raise

    def get_column_by_id(self, table_id: str, col_id: int) -> Optional[ColumnMap]:
        try:
            query = "SELECT * FROM column_map WHERE table_id = ? AND col_id = ?"
            self.cursor.execute(query, (table_id, col_id))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return ColumnMap(**dict(zip(columns, row)))
            return None
        except Exception as e:
            logger.error(f"[컬럼 지도 조회 오류] {e}")
            raise

    def delete_column_by_id(self, table_id: str, col_id: int) -> int:
        try:
            query = "DELETE FROM column_map WHERE table_id = ? AND col_id = ?"
            self.cursor.execute(query, (table_id, col_id))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[컬럼 지도 삭제 오류] {e}")
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()
