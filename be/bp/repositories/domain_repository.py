from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from bp.dbms import get_db
from bp.utils.loggers import setup_logger
from bp.views.domain import Domain
logger = setup_logger()


# Repository 클래스
class DomainRepository:
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
        CREATE TABLE IF NOT EXISTS domains (
            domain_id TEXT PRIMARY KEY,
            domain TEXT,
            source TEXT,
            platform TEXT,
            cate1 TEXT,
            cate2 TEXT,
            file_loc TEXT,
            url TEXT DEFAULT 'None',
            regi_date TEXT,
            up_data_time TEXT
        )
        """
        self.cursor.execute(query)

    def insert_domain(self, domain: Domain) -> str:
        try:
            query = """
            INSERT INTO domains (
                domain_id, domain, source, platform, cate1,
                cate2, file_loc, url, regi_date, up_data_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                domain.domain_id, domain.domain, domain.source, domain.platform,
                domain.cate1, domain.cate2, domain.file_loc, domain.url,
                domain.regi_date or datetime.now().isoformat(),
                domain.up_data_time or datetime.now().isoformat()
            )
            self.cursor.execute(query, values)
            self.conn.commit()
            return domain.domain_id
        except Exception as e:
            logger.error(f"[도메인 삽입 오류] {e}")
            self.conn.rollback()
            raise

    def update_domain(self, domain_id: str, updates: dict) -> int:
        try:
            if not updates:
                return 0

            updates['up_data_time'] = datetime.now().isoformat()
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [domain_id]

            query = f"UPDATE domains SET {set_clause} WHERE domain_id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[도메인 업데이트 오류] {e}")
            self.conn.rollback()
            raise

    def get_domain_by_id(self, domain_id: str) -> Optional[Domain]:
        try:
            query = "SELECT * FROM domains WHERE domain_id = ?"
            self.cursor.execute(query, (domain_id,))
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return Domain(**dict(zip(columns, row)))
            return None
        except Exception as e:
            logger.error(f"[도메인 조회 오류] {e}")
            raise

    def delete_domain(self, domain_id: str) -> int:
        try:
            query = "DELETE FROM domains WHERE domain_id = ?"
            self.cursor.execute(query, (domain_id,))
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"[도메인 삭제 오류] {e}")
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()