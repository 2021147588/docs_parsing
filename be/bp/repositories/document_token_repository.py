import pymysql
import json
from typing import List
import datetime

from be.bp.views.document_token import DocumentToken
from be.bp.dbms import get_db  
from be.bp.utils.loggers import setup_logger

logger = setup_logger()

class DocumentTokenRepository:
    def __init__(self):
        # 루트 DB에 먼저 접속해서 새 DB 생성
        try:
            self.conn = get_db()
            self.cursor = self.conn.cursor()
            
            self._create_table_if_not_exists()
        except Exception as e:
            logger.error(f"[DB 연결 오류] {e}")
            raise

    def _create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS document_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    value VARCHAR(255) NOT NULL,            -- 문서 내 단어
    document_name VARCHAR(255) NOT NULL,    -- 문서 이름
    col_id INT NOT NULL,                    -- 분할 정보 (seg_id)
    word_type VARCHAR(50) NOT NULL,         -- 품사
    cate1 VARCHAR(100) NOT NULL,            -- 분류1
    cate2 VARCHAR(100) NOT NULL,            -- 분류2
    document_path TEXT NOT NULL,            -- 문서 경로
    pii_type VARCHAR(100),                  -- 개인정보 유형 (nullable)

    total_cnt INT,                          -- 전체 도메인 발현 빈도
    domain_cnt INT,                         -- 도메인 내 발현 빈도
    cate1_cnt INT,                          -- 분류1 내 발현 빈도
    cate2_cnt INT,                          -- 분류2 내 발현 빈도
    doc_cnt INT,                            -- 문서 내 발현 빈도
    col_cnt INT,                            -- 해당 분할 내 발현 빈도

    regi_date DATE NOT NULL,                -- 등록일
    gap_avg FLOAT NOT NULL,                 -- 유격 평균
    gap_sd FLOAT NOT NULL,                  -- 유격 편차

    index_list JSON NOT NULL,               -- 인덱스 리스트
    `index` INT                         -- 단일 인덱스 값 (옵션)
);

        """
        self.cursor.execute(create_table_query)
    

    def insert_all_document_tokens(self, document_tokens_list: List[DocumentToken]) -> tuple[int, List[str]]:
        try: 
            query = """
            INSERT INTO document_tokens (
                value, document_name, col_id, word_type,
                cate1, cate2, document_path, pii_type,
                total_cnt, domain_cnt, cate1_cnt, cate2_cnt,
                doc_cnt, col_cnt, regi_date, gap_avg, gap_sd,
                index_list, `index`
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )
            """
            values = [
                (
                    token.value,
                    token.document_name,
                    token.col_id,  # List[int] → JSON 문자열
                    token.word_type,
                    token.cate1,
                    token.cate2,
                    token.document_path.replace("\\", "/"),
                    token.pii_type,

                    token.total_cnt,
                    token.domain_cnt,
                    token.cate1_cnt,
                    token.cate2_cnt,
                    token.doc_cnt,
                    token.col_cnt,

                    token.regi_date,
                    token.gap_avg,
                    token.gap_sd,
                    json.dumps(token.index_list),  # List[int] → JSON 문자열
                    token.index
                )
                for token in document_tokens_list
            ]

            self.cursor.executemany(query, values)
            self.conn.commit()
            row_count = self.cursor.rowcount 
            document_names = {token.document_name for token in document_tokens_list}

            return row_count, list(document_names)
        
        except Exception as e:
            logger.error(f"[데이터 삽입 오류] {e}")
            self.conn.rollback()
            raise

        
    def update_token_counts(self, updated_tokens: List[DocumentToken]):
        query = """
        UPDATE document_tokens
        SET 
            total_cnt = %s,
            domain_cnt = %s,
            cate1_cnt = %s,
            cate2_cnt = %s,
            doc_cnt = %s
        WHERE 
            value = %s AND
            document_name = %s AND
            col_id = %s
        """
        
        values = [
            (
                token.total_cnt,
                token.domain_cnt,
                token.cate1_cnt,
                token.cate2_cnt,
                token.doc_cnt,
                token.value,
                token.document_name,
                token.col_id
            )
            for token in updated_tokens
        ]

        self.cursor.executemany(query, values)
        self.conn.commit()
        return self.cursor.rowcount 

    def delete_token_by_id(self, token_id: int):
        query = "DELETE FROM document_tokens WHERE id = %s"
        self.cursor.execute(query, (token_id,))
        self.conn.commit()

        return self.cursor.rowcount


    def select_all_tokens(self) -> List[DocumentToken]:
        query = "SELECT * FROM document_tokens"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        columns = [desc[0] for desc in self.cursor.description]
        results = []

        for row in rows:
            row_dict = dict(zip(columns, row))

            # JSON 필드 복원
            row_dict['index_list'] = json.loads(row_dict['index_list']) if isinstance(row_dict['index_list'], str) else row_dict['index_list']

            # Pydantic 모델로 변환
            token = DocumentToken(**row_dict)
            results.append(token)

        return results
    
    def get_tokens_by_document_path(self, document_path: str) -> List[DocumentToken]:
        """
        특정 document_path를 가진 모든 DocumentToken을 조회하여 반환합니다.

        Args:
            document_path (str): 조회할 document_path.

        Returns:
            List[DocumentToken]: 조회된 DocumentToken 객체 리스트.
        """
        try:
            document_path = document_path.replace('\\', '\\\\')
            query = "SELECT * FROM document_tokens WHERE document_path = %s"
            self.cursor.execute(query, (document_path,))
            rows = self.cursor.fetchall()

            # 컬럼 이름 가져오기
            columns = [desc[0] for desc in self.cursor.description]
            results = []

            for row in rows:
                row_dict = dict(zip(columns, row))

                # JSON 필드 복원
                row_dict['index_list'] = json.loads(row_dict['index_list']) if isinstance(row_dict['index_list'], str) else list(row_dict['index_list'])

                # Pydantic 모델로 변환
                token = DocumentToken(**row_dict)
                results.append(token)

            return results

        except Exception as e:
            logger.error(f"[데이터 조회 오류] {e}")
            raise
    
    def get_tokens_by_word_and_document_path(self, word: str, seg_id:int, document_path: str) -> List[DocumentToken]:
        """
        특정 단어와 document_path를 가진 DocumentToken을 조회하여 반환합니다.

        Args:
            word (str): 조회할 단어.
            document_path (str): 조회할 document_path.

        Returns:
            List[DocumentToken]: 조회된 DocumentToken 객체 리스트.
        """
        try:
            query = "SELECT * FROM document_tokens WHERE value = %s AND document_path = %s AND col_id = %s"
            self.cursor.execute(query, (word, document_path, seg_id))
            rows = self.cursor.fetchall()

            # 컬럼 이름 가져오기
            columns = [desc[0] for desc in self.cursor.description]
            results = []

            for row in rows:
                row_dict = dict(zip(columns, row))

                # JSON 필드 복원
                row_dict['index_list'] = json.loads(row_dict['index_list']) if isinstance(row_dict['index_list'], str) else list(row_dict['index_list'])

                # Pydantic 모델로 변환
                token = DocumentToken(**row_dict)
                results.append(token)
            logger.info(f"[조회된 데이터 개수] {len(results)}")

            return results

        except Exception as e:
            logger.error(f"[데이터 조회 오류] {e}")
            raise

    def close(self):
        self.conn.close()  # 명시적으로 닫는 메서드 정의
if __name__=="__main__":
    
    document_token_list = [
        {'value': 'Google', 'document_name': 'AGI', 'col_id': 1, 'word_type': 'alphabet', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [0], 'index': 0},
        {'value': 'AI', 'document_name': 'AGI', 'col_id': 1, 'word_type': 'alphabet', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [1], 'index': 1},
        {'value': '분야', 'document_name': 'AGI', 'col_id': 1, 'word_type': 'noun', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [2], 'index': 2},
        {'value': '선도', 'document_name': 'AGI', 'col_id': 1, 'word_type': 'noun', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 3, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 2.0, 'gap_sd': 0.0, 'index_list': [3, 5, 7], 'index': 7},
        {'value': '있', 'document_name': 'AGI', 'col_id': 1, 'word_type': 'adjective', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [8], 'index': 8},
        {'value': 'Google', 'document_name': 'AGI', 'col_id': 2, 'word_type': 'alphabet', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [10], 'index': 10},
        {'value': 'AI', 'document_name': 'AGI', 'col_id': 2, 'word_type': 'alphabet', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [11], 'index': 11},
        {'value': '분야', 'document_name': 'AGI', 'col_id': 2, 'word_type': 'noun', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [12], 'index': 12},
        {'value': '선도', 'document_name': 'AGI', 'col_id': 2, 'word_type': 'noun', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 2, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 4.0, 'gap_sd': 0.0, 'index_list': [13, 17], 'index': 17},
        {'value': '있', 'document_name': 'AGI', 'col_id': 2, 'word_type': 'adjective', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [18], 'index': 18},
        {'value': 'Google', 'document_name': 'AGI', 'col_id': 3, 'word_type': 'alphabet', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [20], 'index': 20},
        {'value': 'AI', 'document_name': 'AGI', 'col_id': 3, 'word_type': 'alphabet', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [21], 'index': 21},
        {'value': '선도', 'document_name': 'AGI', 'col_id': 3, 'word_type': 'noun', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [23], 'index': 23},
        {'value': '있', 'document_name': 'AGI', 'col_id': 3, 'word_type': 'adjective', 'cate1': '기술', 'cate2': 'AI', 'document_path': 'D:/2025/parsing', 'pii_type': None, 'total_cnt': None, 'domain_cnt': None, 'cate1_cnt': None, 'cate2_cnt': None, 'doc_cnt': None, 'col_cnt': 1, 'regi_date': datetime.date(2025, 3, 26), 'gap_avg': 0.0, 'gap_sd': 0.0, 'index_list': [28], 'index': 28},
            ]
    document_token_objects: List[DocumentToken] = [DocumentToken(**item) for item in document_token_list]

    document_token_repository = DocumentTokenRepository()
    r_c, document_name = document_token_repository.insert_all_document_tokens(document_token_objects)
    print(r_c,document_name)
    breakpoint()
    document_token_repository.close()  # 연결 닫기!
    # document_token_list_updated = [DocumentToken(value='Google', document_name='AGI', col_id=1, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=3, domain_cnt=3, cate1_cnt=3, cate2_cnt=3, doc_cnt=3, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[0], index=0), DocumentToken(value='AI', document_name='AGI', col_id=1, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=2, domain_cnt=2, cate1_cnt=2, cate2_cnt=2, doc_cnt=2, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[1], index=1), DocumentToken(value='분야', document_name='AGI', col_id=1, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=2, domain_cnt=2, cate1_cnt=2, cate2_cnt=2, doc_cnt=2, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[2], index=2), DocumentToken(value='선도', document_name='AGI', col_id=1, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=6, domain_cnt=6, cate1_cnt=6, cate2_cnt=6, doc_cnt=6, col_cnt=3, regi_date=datetime.date(2025, 3, 26), gap_avg=2.0, gap_sd=0.0, index_list=[3, 5, 7], index=7), DocumentToken(value='있', document_name='AGI', col_id=1, word_type='adjective', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=3, domain_cnt=3, cate1_cnt=3, cate2_cnt=3, doc_cnt=3, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[8], index=8), DocumentToken(value='Google', document_name='AGI', col_id=2, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=3, domain_cnt=3, cate1_cnt=3, cate2_cnt=3, doc_cnt=3, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[10], index=10), DocumentToken(value='AI', document_name='AGI', col_id=2, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=2, domain_cnt=2, cate1_cnt=2, cate2_cnt=2, doc_cnt=2, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[11], index=11), DocumentToken(value='분야', document_name='AGI', col_id=2, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=2, domain_cnt=2, cate1_cnt=2, cate2_cnt=2, doc_cnt=2, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[12], index=12), DocumentToken(value='선도', document_name='AGI', col_id=2, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=6, domain_cnt=6, cate1_cnt=6, cate2_cnt=6, doc_cnt=6, col_cnt=2, regi_date=datetime.date(2025, 3, 26), gap_avg=4.0, gap_sd=0.0, index_list=[13, 17], index=17), DocumentToken(value='있', document_name='AGI', col_id=2, word_type='adjective', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=3, domain_cnt=3, cate1_cnt=3, cate2_cnt=3, doc_cnt=3, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[18], index=18), DocumentToken(value='Google', document_name='AGI', col_id=3, word_type='alphabet', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=3, domain_cnt=3, cate1_cnt=3, cate2_cnt=3, doc_cnt=3, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[20], index=20), DocumentToken(value='선도', document_name='AGI', col_id=3, word_type='noun', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=6, domain_cnt=6, cate1_cnt=6, cate2_cnt=6, doc_cnt=6, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[23], index=23), DocumentToken(value='있', document_name='AGI', col_id=3, word_type='adjective', cate1='기술', cate2='AI', document_path='D:/2025/parsing', pii_type=None, total_cnt=3, domain_cnt=3, cate1_cnt=3, cate2_cnt=3, doc_cnt=3, col_cnt=1, regi_date=datetime.date(2025, 3, 26), gap_avg=0.0, gap_sd=0.0, index_list=[28], index=28)]
    
    # print(document_token_repository.update_token_counts(document_token_list_updated))
    
    # print(document_token_repository.select_all_tokens())