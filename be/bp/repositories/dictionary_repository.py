import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from bp.dbms import get_db
import logging

logger = logging.getLogger(__name__)

class DictionaryRepository:
    def __init__(self):
        self.conn = get_db()
        self.cursor = self.conn.cursor()
            
        self._create_tables()

    
    def _create_tables(self):
        """의미사전 테이블과 사용자 정의 불용어 사전 테이블을 생성합니다."""
        
        # 의미사전 테이블 생성
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS dictionary (
            word TEXT,
            cate1 TEXT,
            cate2 TEXT,
            importance INTEGER DEFAULT 1,
            regi_date TEXT,
            domain TEXT,
            domain_id TEXT,
            user_id TEXT,
            add_count INTEGER DEFAULT 0,
            delete_count INTEGER DEFAULT 0,
            PRIMARY KEY (word, cate1, cate2, user_id)
        )
        ''')
        
    def add_to_dictionary(self, word: str, cate1: str = None, cate2: str = None, increment_count: bool = True) -> Dict:
        """
        의미사전에 단어를 추가합니다.
        
        Args:
            word (str): 추가할 단어
            cate1 (str, optional): 1차 카테고리
            cate2 (str, optional): 2차 카테고리
            increment_count (bool, optional): 추가 카운트를 증가시킬지 여부. 기본값은 True.
            
        Returns:
            Dict: 추가 결과
        """
        try:
            logger.info(f"단어: {word}, 카테고리1: {cate1}, 카테고리2: {cate2}, 증가 여부: {increment_count}")
            
            # 단어가 이미 존재하는지 확인
            self.cursor.execute("SELECT word FROM dictionary WHERE word = %s", (word,))            
            
            existing_word = self.cursor.fetchone()
            
            if existing_word:
                # 단어가 이미 존재하면 카운트만 증가 (increment_count가 True인 경우)
                if increment_count:
                    self.cursor.execute("""
                        UPDATE dictionary 
                        SET add_count = add_count + 1 
                        WHERE word = %s
                    """, [word])
                return {
                    'success': True,
                    'message': '단어가 이미 존재합니다.'
                }
            
            # 새 단어 추가
            self.cursor.execute("""
                INSERT INTO dictionary (word, cate1, cate2, add_count)
                VALUES (%s, %s, %s, %s)
            """, [word, cate1, cate2, 1 if increment_count else 0])
            
            self.conn.commit()
            return {
                'success': True,
                'message': '단어가 추가되었습니다.'
            }
        except Exception as e:
            logger.error(f"의미사전에 단어 추가 중 오류: {str(e)}")
            return {
                'success': False,
                'message': f'의미사전에 단어를 추가하는 중 오류가 발생했습니다: {str(e)}'
            }
    
    def remove_from_dictionary(self, word: str, cate1: str = None, cate2: str = None, increment_count: bool = True) -> Dict:
        """
        의미사전에서 단어를 삭제합니다.
        
        Args:
            word (str): 삭제할 단어
            cate1 (str, optional): 1차 카테고리
            cate2 (str, optional): 2차 카테고리
            increment_count (bool, optional): 삭제 카운트를 증가시킬지 여부. 기본값은 True.
            
        Returns:
            성공 여부
        """
        try:
            # 단어가 있는지 확인
            if not self.check_word_in_dictionary(word):
                return {
                    'success': False,
                    'message': '의미사전에 존재하지 않는 단어입니다.'
                }
            
            # 삭제 카운트 증가
            if increment_count:
                self.cursor.execute(
                    "UPDATE dictionary SET delete_count = delete_count + 1 WHERE word = %s",
                    (word,)
                )
                self.conn.commit()
            
            return {
                'success': True,
                'message': '의미사전에서 단어가 삭제되었습니다.'
            }
            
        except Exception as e:
            logger.error(f'의미사전에서 단어 삭제 중 오류 발생: {str(e)}')
            return {
                'success': False,
                'message': f'의미사전에서 단어를 삭제하는 중 오류가 발생했습니다: {str(e)}'
            }
    
    def get_dictionary(self, domain: str = None, domain_id: str = None, user_id: str = None) -> List[Dict]:
        """
        의미사전의 모든 단어를 가져옵니다.
        
        Args:
            domain: 도메인 필터
            domain_id: 도메인 ID 필터
            user_id: 사용자 ID 필터
            
        Returns:
            의미사전 단어 목록
        """
        
        try:
            query = "SELECT * FROM dictionary"
            params = []
            
            conditions = []
            
            if domain:
                conditions.append("domain = %s")
                params.append(domain)
            
            if domain_id:
                conditions.append("domain_id = %s")
                params.append(domain_id)
                
            if user_id:
                conditions.append("user_id = %s")
                params.append(user_id)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            self.cursor.execute(query, params)
            
            columns = [description[0] for description in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            print(f"의미사전 조회 중 오류 발생: {e}")
            return []
    
    def search_dictionary(self, keyword: str, user_id: str = None) -> Dict:
        """
        의미사전에서 키워드로 검색합니다.
        
        Args:
            keyword: 검색 키워드
            user_id: 사용자 ID 필터
            
        Returns:
            검색 결과 목록과 추가/삭제 횟수 합계를 담은 딕셔너리
        """
        
        try:
            # 검색 결과를 가져오는 쿼리
            query = """
            SELECT * FROM dictionary 
            WHERE word LIKE %s OR cate1 LIKE %s OR cate2 LIKE %s
            """
            params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            self.cursor.execute(query, params)
            
            columns = [description[0] for description in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            # 추가/삭제 횟수 합계를 계산하는 쿼리
            sum_query = """
            SELECT SUM(add_count) as total_add_count, SUM(delete_count) as total_delete_count
            FROM dictionary 
            WHERE word LIKE %s OR cate1 LIKE %s OR cate2 LIKE %s
            """
            sum_params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
            
            if user_id:
                sum_query += " AND user_id = %s"
                sum_params.append(user_id)
            
            self.cursor.execute(sum_query, sum_params)
            sum_row = self.cursor.fetchone()
            
            total_add_count = sum_row[0] if sum_row and sum_row[0] is not None else 0
            total_delete_count = sum_row[1] if sum_row and sum_row[1] is not None else 0
            
            return {
                'word': keyword,
                'total_add_count': total_add_count,
                'total_delete_count': total_delete_count
            }
        except Exception as e:
            print(f"의미사전 검색 중 오류 발생: {e}")
            return {
                'results': [],
                'total_add_count': 0,
                'total_delete_count': 0
            }
    
    def update_dictionary_word(self, word: str, cate1: str = None, cate2: str = None, 
                             importance: int = None, user_id: str = None) -> bool:
        """
        의미사전의 단어 정보를 업데이트합니다.
        
        Args:
            word: 업데이트할 단어
            cate1: 새로운 대분류
            cate2: 새로운 세부 분류
            importance: 새로운 중요도
            user_id: 사용자 ID
            
        Returns:
            성공 여부
        """
        
        try:
            update_fields = []
            params = []
            
            if cate1 is not None:
                update_fields.append("cate1 = %s")
                params.append(cate1)
            
            if cate2 is not None:
                update_fields.append("cate2 = %s")
                params.append(cate2)
            
            if importance is not None:
                update_fields.append("importance = %s")
                params.append(importance)
                
            if user_id is not None:
                update_fields.append("user_id = %s")
                params.append(user_id)
            
            if not update_fields:
                return False
            
            params.append(word)
            query = f"UPDATE dictionary SET {', '.join(update_fields)} WHERE word = %s"
            
            self.cursor.execute(query, params)
            self.conn.commit()
            
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"의미사전 단어 업데이트 중 오류 발생: {e}")
            return False

    def check_word_in_dictionary(self, word):
        """
        단어가 의미사전에 있는지 확인합니다.
        
        Args:
            word (str): 확인할 단어
            
        Returns:
            bool: 단어가 의미사전에 있으면 True, 없으면 False
        """
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM dictionary WHERE word = %s",
                (word,)
            )
            count = self.cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            logger.error(f'의미사전 단어 확인 중 오류 발생: {str(e)}')
            return False

    def remove_from_stopwords(self, word, cate1=None, cate2=None, increment_count=True):
        """
        불용어사전에서 단어를 삭제합니다.
        
        Args:
            word (str): 삭제할 단어
            cate1 (str, optional): 1차 카테고리
            cate2 (str, optional): 2차 카테고리
            increment_count (bool, optional): 삭제 카운트를 증가시킬지 여부. 기본값은 True.
            
        Returns:
            Dict: 삭제 결과
        """
        try:
            # None 값을 빈 문자열로 변환
            cate1 = '' if cate1 is None else cate1
            cate2 = '' if cate2 is None else cate2
            
            # 단어가 존재하는지 확인
            sql = "SELECT * FROM stopwords WHERE word = ? AND cate1 = ? AND cate2 = ?"
            self.cursor.execute(sql, (word, cate1, cate2))
            result = self.cursor.fetchone()
            
            if not result:
                return {
                    'success': False,
                    'message': '해당 단어가 불용어사전에 존재하지 않습니다.'
                }
            
            # 삭제 카운트 증가
            if increment_count:
                sql = "UPDATE stopwords SET delete_count = delete_count + 1 WHERE word = ? AND cate1 = ? AND cate2 = ?"
                self.cursor.execute(sql, (word, cate1, cate2))
                self.conn.commit()
            
            # 단어 삭제
            sql = "DELETE FROM stopwords WHERE word = ? AND cate1 = ? AND cate2 = ?"
            self.cursor.execute(sql, (word, cate1, cate2))
            self.conn.commit()
            
            return {
                'success': True,
                'message': '단어가 불용어사전에서 삭제되었습니다.'
            }
        except Exception as e:
            logger.error(f'불용어사전에서 단어 삭제 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'불용어사전에서 단어를 삭제하는 중 오류가 발생했습니다: {str(e)}'
            }
    
    def get_document_tokens(self, page=1, per_page=20, word='', word_type='', 
                           cate1='', cate2='', sort_by='total_cnt', sort_order='desc'):
        """
        문서 토큰 테이블의 데이터를 조회합니다.
        
        Args:
            page (int, optional): 페이지 번호. 기본값은 1.
            per_page (int, optional): 페이지당 항목 수. 기본값은 20.
            word (str, optional): 단어 필터. 기본값은 빈 문자열.
            word_type (str, optional): 품사 필터. 기본값은 빈 문자열.
            cate1 (str, optional): 1차 카테고리 필터. 기본값은 빈 문자열.
            cate2 (str, optional): 2차 카테고리 필터. 기본값은 빈 문자열.
            sort_by (str, optional): 정렬 기준. 기본값은 'total_cnt'.
            sort_order (str, optional): 정렬 순서. 기본값은 'desc'.
            
        Returns:
            Dict: 토큰 목록과 총 개수
        """
        try:
            # 기본 쿼리 구성
            base_query = "FROM document_tokens WHERE 1=1"
            params = []
            
            # 필터 조건 추가
            if word:
                base_query += " AND word LIKE ?"
                params.append(f'%{word}%')
            if word_type:
                base_query += " AND word_type = ?"
                params.append(word_type)
            if cate1:
                base_query += " AND cate1 = ?"
                params.append(cate1)
            if cate2:
                base_query += " AND cate2 = ?"
                params.append(cate2)
            
            # 총 개수 조회
            count_query = f"SELECT COUNT(*) {base_query}"
            self.cursor.execute(count_query, params)
            total_count = self.cursor.fetchone()[0]
            
            # 정렬 및 페이지네이션 적용
            offset = (page - 1) * per_page
            query = f"""
                SELECT word, word_type, cate1, cate2, total_cnt, meaning_cnt, stopwords_cnt
                {base_query}
                ORDER BY {sort_by} {sort_order}
                LIMIT ? OFFSET ?
            """
            params.extend([per_page, offset])
            
            # 데이터 조회
            self.cursor.execute(query, params)
            tokens = self.cursor.fetchall()
            
            # 결과 포맷팅
            formatted_tokens = []
            for token in tokens:
                formatted_tokens.append({
                    'word': token[0],
                    'word_type': token[1],
                    'cate1': token[2],
                    'cate2': token[3],
                    'total_cnt': token[4],
                    'meaning_cnt': token[5],
                    'stopwords_cnt': token[6]
                })
            
            return {
                'success': True,
                'tokens': formatted_tokens,
                'total_count': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        except Exception as e:
            logger.error(f'문서 토큰 조회 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'문서 토큰을 조회하는 중 오류가 발생했습니다: {str(e)}',
                'tokens': [],
                'total_count': 0,
                'total_pages': 0
            }
