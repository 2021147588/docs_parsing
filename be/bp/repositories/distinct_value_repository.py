from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from bp.dbms import get_db
from bp.utils.loggers import setup_logger
from bp.views.distinct_value import DistinctValue
logger = setup_logger()

# Repository 클래스
class DistinctValueRepository:
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
        CREATE TABLE IF NOT EXISTS distinct_value (
            log_id INTEGER,
            col_id INTEGER,
            table_id TEXT,
            table_src TEXT,
            cate1 TEXT,
            cate2 TEXT,
            value TEXT,
            distinct_value INTEGER,
            cate1_list TEXT,
            cate2_list TEXT
        )
        """
        self.cursor.execute(query)

    def insert_distinct_value(self, attr: DistinctValue) -> int:
        try:
            query = """
            INSERT INTO distinct_value (
                log_id, col_id, table_id, table_src, cate1, cate2,
                value, distinct_value, cate1_list, cate2_list
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                attr.log_id, attr.col_id, attr.table_id, attr.table_src,
                attr.cate1, attr.cate2, attr.value, attr.distinct_value,
                attr.cate1_list, attr.cate2_list
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"[속성값 삽입 오류] {e}")
            self.conn.rollback()
            raise

    def get_distinct_value_by_col(self, table_id: str, col_id: int) -> list[DistinctValue]:
        try:
            query = "SELECT * FROM distinct_value WHERE table_id = ? AND col_id = ?"
            self.cursor.execute(query, (table_id, col_id))
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            return [DistinctValue(**dict(zip(columns, row))) for row in rows]
        except Exception as e:
            logger.error(f"[속성값 조회 오류] {e}")
            raise

    def delete_distinct_value_by_col(self, table_id: str, col_id: int) -> int:
        try:
            query = "DELETE FROM distinct_value WHERE table_id = ? AND col_id = ?"
            self.cursor.execute(query, (table_id, col_id))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[속성값 삭제 오류] {e}")
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()