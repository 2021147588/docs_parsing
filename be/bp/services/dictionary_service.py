from bp.repositories.dictionary_repository import DictionaryRepository
from bp.repositories.stopwords_dictionary_repository import StopwordsRepository
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class DictionaryService:
    def __init__(self):
        self.dictionary_repository = DictionaryRepository()
        self.stopwords_repository = StopwordsRepository()

    def create_meaning_dictionary(self):
        pass
    
    def create_stopwords_dictionary(self):
        pass
    
    def search_meaning_dictionary(self, keyword: str, user_id: str = None):
        """
        의미사전에서 단어를 검색합니다.
        
        Args:
            keyword (str): 검색할 키워드
            user_id (str, optional): 사용자 ID
            
        Returns:
            Dict: 검색 결과 목록과 추가/삭제 횟수 합계
        """
        try:
            result = self.dictionary_repository.search_dictionary(keyword, user_id)
            return {
                'meaning_word': result['word'],
                'total_add_count': result['total_add_count'],
                'total_delete_count': result['total_delete_count']
            }
        except Exception as e:
            logger.error(f"의미사전 검색 중 오류 발생: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'의미사전 검색 중 오류가 발생했습니다: {str(e)}'
            }
    def search_stopwords(self, keyword: str, user_id: str = None):
        """
        불용어사전에서 단어를 검색합니다.
        
        Args:
            keyword (str): 검색할 키워드
            user_id (str, optional): 사용자 ID
            
        Returns:
            Dict: 검색 결과 목록과 추가/삭제 횟수 합계
        """
        try:
            result = self.stopwords_repository.search_stopwords(keyword, user_id)
            return {
                'stopword_word': result['word'],
                'total_add_count': result['total_add_count'],
                'total_delete_count': result['total_delete_count']
            }
        except Exception as e:
            logger.error(f"불용어사전 검색 중 오류 발생: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'불용어사전 검색 중 오류가 발생했습니다: {str(e)}'
            }
    
    
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
           
            # 의미사전에 추가
            result = self.dictionary_repository.add_to_dictionary(word, cate1, cate2, increment_count)
            return result
        except Exception as e:
            logger.error(f'의미사전에 단어 추가 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'의미사전에 단어를 추가하는 중 오류가 발생했습니다: {str(e)}'
            }

    def add_to_stopwords(self, word: str, cate1: str = None, cate2: str = None, increment_count: bool = True) -> Dict:
        """
        불용어사전에 단어를 추가합니다.
        
        Args:
            word (str): 추가할 단어
            increment_count (bool, optional): 추가 카운트를 증가시킬지 여부. 기본값은 True.
            
        Returns:
            Dict: 추가 결과
        """
        try:
            
        
            # 불용어사전에 추가
            result = self.stopwords_repository.add_to_stopwords(word, cate1, cate2, increment_count)
            return result
        except Exception as e:
            logger.error(f'불용어사전에 단어 추가 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'불용어사전에 단어를 추가하는 중 오류가 발생했습니다: {str(e)}'
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
            Dict: 삭제 결과
        """
        try:
            # 의미사전에서 삭제
            result = self.dictionary_repository.remove_from_dictionary(word, cate1, cate2, increment_count)
            return result
        except Exception as e:
            logger.error(f'의미사전에서 단어 삭제 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'의미사전에서 단어를 삭제하는 중 오류가 발생했습니다: {str(e)}'
            }

    def remove_from_stopwords(self, word: str, cate1: str = None, cate2: str = None, increment_count: bool = True) -> Dict:
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
            # 불용어사전에서 삭제
            result = self.stopwords_repository.remove_from_stopwords(word, cate1, cate2, increment_count)
            return result
        except Exception as e:
            logger.error(f'불용어사전에서 단어 삭제 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'불용어사전에서 단어를 삭제하는 중 오류가 발생했습니다: {str(e)}'
            }
    
    def get_document_tokens(self, page: int = 1, per_page: int = 20, word: str = '', 
                           word_type: str = '', cate1: str = '', cate2: str = '',
                           sort_by: str = 'total_cnt', sort_order: str = 'desc') -> Dict:
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
            # 문서 토큰 테이블에서 데이터 조회
            result = self.dictionary_repository.get_document_tokens(
                page=page,
                per_page=per_page,
                word=word,
                word_type=word_type,
                cate1=cate1,
                cate2=cate2,
                sort_by=sort_by,
                sort_order=sort_order
            )
            return result
        except Exception as e:
            logger.error(f'문서 토큰 조회 중 오류: {str(e)}')
            return {
                'success': False,
                'message': f'문서 토큰을 조회하는 중 오류가 발생했습니다: {str(e)}',
                'tokens': [],
                'total_count': 0,
                'total_pages': 0
            }
    