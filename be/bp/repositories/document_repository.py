from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from bp.dbms import get_db
from bp.utils.loggers import setup_logger
from bp.views.document import Document

logger = setup_logger()



# Repository 클래스
class DocumentRepository:
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
        CREATE TABLE IF NOT EXISTS documents (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_id TEXT,
            table_id TEXT,
            table_nm TEXT,
            table_source TEXT,
            table_src_platform TEXT,
            cate1 TEXT,
            cate2 TEXT,
            file_loc TEXT,
            url TEXT DEFAULT 'None',
            column_cnt INTEGER,
            categorical_cnt INTEGER,
            numerical_cnt INTEGER,
            rec_cnt INTEGER,
            table_qty_index INTEGER,
            regi_date TEXT,
            cum_search_num INTEGER,
            language TEXT,
            up_data_time TEXT,
            before_parsing_cnt INTEGER,
            after_parsing_cnt INTEGER,
            insert_flag INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(query)

    def insert_document(self, doc: Document) -> int:
        try:
            query = """
            INSERT INTO documents (
                domain_id, table_id, table_nm, table_source, table_src_platform,
                cate1, cate2, file_loc, url, column_cnt,
                categorical_cnt, numerical_cnt, rec_cnt, table_qty_index, regi_date,
                cum_search_num, language, up_data_time, before_parsing_cnt,
                after_parsing_cnt, insert_flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                doc.domain_id, doc.table_id, doc.table_nm, doc.table_source, doc.table_src_platform,
                doc.cate1, doc.cate2, doc.file_loc, doc.url, doc.column_cnt,
                doc.categorical_cnt, doc.numerical_cnt, doc.rec_cnt, doc.table_qty_index, doc.regi_date,
                doc.cum_search_num, doc.language, doc.up_data_time, doc.before_parsing_cnt,
                doc.after_parsing_cnt, doc.insert_flag
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            logger.error(f"[문서 삽입 오류] {e}")
            self.conn.rollback()
            raise

    def update_insert_flag(self, table_id: str, flag: int = 1) -> int:
        try:
            query = """
            UPDATE documents SET insert_flag = ?, up_data_time = ? WHERE table_id = ?
            """
            self.cursor.execute(query, (flag, datetime.now().isoformat(), table_id))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[문서 업데이트 오류] {e}")
            self.conn.rollback()
            raise

    def get_document_by_table_id(self, table_id: str) -> Optional[Document]:
        try:
            query = "SELECT * FROM documents WHERE table_id = ?"
            self.cursor.execute(query, (table_id,))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return Document(**dict(zip(columns, row)))
            return None
        except Exception as e:
            logger.error(f"[문서 조회 오류] {e}")
            raise

    def delete_document_by_table_id(self, table_id: str) -> int:
        try:
            query = "DELETE FROM documents WHERE table_id = ?"
            self.cursor.execute(query, (table_id,))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[문서 삭제 오류] {e}")
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()