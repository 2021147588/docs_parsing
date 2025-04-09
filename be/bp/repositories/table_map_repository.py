from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from bp.dbms import get_db
from bp.utils.loggers import setup_logger
from bp.views.table_map import TableMap
logger = setup_logger()



# Repository 클래스
class TableMapRepository:
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
        CREATE TABLE IF NOT EXISTS table_map (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id TEXT,
            table_nm TEXT,
            table_source TEXT,
            table_src_platform TEXT,
            cate1 TEXT,
            cate2 TEXT,
            file_loc TEXT,
            url TEXT DEFAULT 'None',
            column_cnt INTEGER,
            categorical_cnt INTEGER DEFAULT 0,
            numerical_cnt INTEGER DEFAULT 0,
            rec_cnt INTEGER,
            table_qty_index INTEGER DEFAULT 0,
            regi_date TEXT,
            cum_search_num INTEGER,
            language TEXT,
            up_data_time TEXT,
            insert_flag INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(query)

    def insert_table_map(self, table: TableMap) -> int:
        try:
            query = """
            INSERT INTO table_map (
                table_id, table_nm, table_source, table_src_platform, cate1, cate2,
                file_loc, url, column_cnt, categorical_cnt, numerical_cnt, rec_cnt,
                table_qty_index, regi_date, cum_search_num, language, up_data_time, insert_flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                table.table_id, table.table_nm, table.table_source, table.table_src_platform,
                table.cate1, table.cate2, table.file_loc, table.url, table.column_cnt,
                table.categorical_cnt, table.numerical_cnt, table.rec_cnt,
                table.table_qty_index, table.regi_date or datetime.now().isoformat(),
                table.cum_search_num, table.language,
                table.up_data_time or datetime.now().isoformat(), table.insert_flag
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"[테이블 지도 삽입 오류] {e}")
            self.conn.rollback()
            raise

    def update_insert_flag(self, table_id: str, flag: int = 1) -> int:
        try:
            query = """
            UPDATE table_map SET insert_flag = ?, up_data_time = ? WHERE table_id = ?
            """
            self.cursor.execute(query, (flag, datetime.now().isoformat(), table_id))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[테이블 지도 업데이트 오류] {e}")
            self.conn.rollback()
            raise

    def get_table_by_id(self, table_id: str) -> Optional[TableMap]:
        try:
            query = "SELECT * FROM table_map WHERE table_id = ?"
            self.cursor.execute(query, (table_id,))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return TableMap(**dict(zip(columns, row)))
            return None
        except Exception as e:
            logger.error(f"[테이블 지도 조회 오류] {e}")
            raise

    def delete_table_by_id(self, table_id: str) -> int:
        try:
            query = "DELETE FROM table_map WHERE table_id = ?"
            self.cursor.execute(query, (table_id,))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[테이블 지도 삭제 오류] {e}")
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()
