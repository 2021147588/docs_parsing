from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from bp.dbms import get_db
from bp.utils.loggers import setup_logger
from bp.views.column import ColumnTable

logger = setup_logger()

# Repository 클래스
class ColumnTableRepository:
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
        CREATE TABLE IF NOT EXISTS column_table (
            log_id INTEGER,
            domain_id TEXT,
            col_id INTEGER,
            col_name TEXT,
            table_name TEXT,
            table_id TEXT,
            url TEXT NOT NULL DEFAULT 'None',
            table_source TEXT,
            table_src_platform TEXT,
            cate1 TEXT,
            cate2 TEXT,
            num_cat_flag TEXT NOT NULL DEFAULT 'None',
            distinct_cnt INTEGER,
            min_val REAL,
            q1_val REAL,
            ave_val REAL,
            median_val REAL,
            q4_val REAL,
            max_val REAL,
            null_ratio TEXT NOT NULL DEFAULT 'None',
            same_ratio REAL,
            rec_cnt INTEGER,
            pk_ratio REAL,
            regi_date TEXT,
            cum_search_num INTEGER,
            column_val_file_loc TEXT,
            language TEXT,
            up_data_time TEXT
        )
        """
        self.cursor.execute(query)

    def insert_column_table(self, col: ColumnTable) -> int:
        try:
            query = """
            INSERT INTO column_table (
                log_id, domain_id, col_id, col_name, table_name, table_id, url,
                table_source, table_src_platform, cate1, cate2, num_cat_flag,
                distinct_cnt, min_val, q1_val, ave_val, median_val, q4_val,
                max_val, null_ratio, same_ratio, rec_cnt, pk_ratio,
                regi_date, cum_search_num, column_val_file_loc, language, up_data_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                col.log_id, col.domain_id, col.col_id, col.col_name, col.table_name, col.table_id, col.url,
                col.table_source, col.table_src_platform, col.cate1, col.cate2, col.num_cat_flag,
                col.distinct_cnt, col.min_val, col.q1_val, col.ave_val, col.median_val, col.q4_val,
                col.max_val, col.null_ratio, col.same_ratio, col.rec_cnt, col.pk_ratio,
                col.regi_date or datetime.now().isoformat(),
                col.cum_search_num, col.column_val_file_loc, col.language,
                col.up_data_time or datetime.now().isoformat()
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"[분할 테이블 삽입 오류] {e}")
            self.conn.rollback()
            raise

    def get_column_by_table_and_col_id(self, table_id: str, col_id: int) -> Optional[ColumnTable]:
        try:
            query = "SELECT * FROM column_table WHERE table_id = ? AND col_id = ?"
            self.cursor.execute(query, (table_id, col_id))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return ColumnTable(**dict(zip(columns, row)))
            return None
        except Exception as e:
            logger.error(f"[분할 테이블 조회 오류] {e}")
            raise

    def delete_column_by_table_and_col_id(self, table_id: str, col_id: int) -> int:
        try:
            query = "DELETE FROM column_table WHERE table_id = ? AND col_id = ?"
            self.cursor.execute(query, (table_id, col_id))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[분할 테이블 삭제 오류] {e}")
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()
