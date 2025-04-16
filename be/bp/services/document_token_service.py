from typing import List, Dict, Tuple
import json
import pandas as pd
import os

from bp.services.document_token.input_data import input_data
from bp.services.document_token.document_parsor import DocumentParser
from bp.services.document_token.word_tokenizer import WordTokenizer
from bp.services.document_token.analysis_document import compute_token_stats_by_word, enrich_token_frequencies
from bp.views.document_token import DocumentToken, DocumentTokenDB
from bp.repositories.document_token_repository import DocumentTokenRepository
from bp.services.document_token.input_data import input_data
from bp.utils.loggers import setup_logger
from bp.services.dictionary_service import DictionaryService

logger = setup_logger()

class DocumentParsingService:
    def __init__(self):
        self.document_token_repository = DocumentTokenRepository()
        self.dictionary_service = DictionaryService()

    def _convert_to_db_model(self, token: DocumentToken) -> DocumentTokenDB:
        return DocumentTokenDB(
            value=token.value,
            word_type=token.word_type,
            col_id=token.col_id,
            col_cnt=token.col_cnt,
            total_cnt=token.total_cnt,
            cate1_cnt=token.cate1_cnt,
            cate2_cnt=token.cate2_cnt,
            doc_cnt=token.doc_cnt,
            cate1=token.cate1,
            cate2=token.cate2,
            document_path=token.document_path,
            document_name=token.document_name,
            pii_type=token.pii_type,
            regi_date=token.regi_date,
            gap_avg=token.gap_avg,
            gap_sd=token.gap_sd,
            index_list=token.index_list,
            index=token.index
        )

    def _convert_to_pydantic_model(self, token: DocumentTokenDB) -> DocumentToken:
        return DocumentToken(
            value=token.value,
            word_type=token.word_type,
            col_id=token.col_id,
            col_cnt=token.col_cnt,
            total_cnt=token.total_cnt,
            cate1_cnt=token.cate1_cnt,
            cate2_cnt=token.cate2_cnt,
            doc_cnt=token.doc_cnt,
            cate1=token.cate1,
            cate2=token.cate2,
            document_path=token.document_path,
            document_name=token.document_name,
            pii_type=token.pii_type,
            regi_date=token.regi_date,
            gap_avg=token.gap_avg,
            gap_sd=token.gap_sd,
            index_list=token.index_list,
            index=token.index
        )
    
    def create_document_token(self, lang, metadata) -> Tuple[int, int]:
        logger.info(f"Start creating document token: {metadata['file_loc']}")

        name = metadata["file_loc"]
        source = metadata['source']
        platform = metadata['platform']
        cate1 = metadata['cate1']
        cate2 = metadata['cate2']
        file_loc = metadata['file_loc']
        url = metadata['url']

        file_dir = file_loc + '/' + cate1 
        logger.info(f"file_dir: {file_dir}")

        file_path_list = input_data(file_dir)
        # /data/ 이후의 경로만 추출
        logger.info(f"{file_dir}에서 찾은 문서 개수: {len(file_path_list)}")

        row_counts = []
        for file_path in file_path_list:
            document_token_list = self._tokenize_document(file_path, lang, name, cate1, cate2)
        
            row_count = self.document_token_repository.insert_all_document_tokens(document_token_list)

            # # 전체 문서 내 토큰 테이블 수치 업데이트
            # all_document_tokens = self.document_token_repository.select_all_tokens()
            # all_document_tokens_update = enrich_token_frequencies(all_document_tokens)
            
            # row_count = self.document_token_repository.update_token_counts(all_document_tokens_update)
            row_counts.append(row_count)

        return len(row_counts), sum(row_counts), file_path_list
        
    def _tokenize_document(self, file_path:str, lang: str, name: str, cate1:str, cate2:str) -> List[DocumentToken]:
        """
        path: 폴더 디렉토리
        lang: kor or eng
        metadata: source, platform, cate1, cate2, file_loc, url
        """
        
        tokens_per_file = []
        logger.info(f"Start tokenizing document: {file_path}")
        # 1. 문서를 분할별로 파싱
        parsor = DocumentParser(file_path)
        segs = parsor.parse_doc_to_seg()
        logger.info(f"[document_token_service.py] 분할 개수: {len(segs)}")

        # Seg 데이터를 JSON 파일로 저장
        seg_file_path = f"segs/{os.path.basename(file_path)}.json"
        os.makedirs(os.path.dirname(seg_file_path), exist_ok=True)
        with open(seg_file_path, "w", encoding="utf-8") as seg_file:
            json.dump(segs, seg_file, ensure_ascii=False, indent=4)

        # 2. 분할을 토큰화
        tokenizer = WordTokenizer(segs, lang)
        tokens = tokenizer.tokenization()
        tokens_per_file.append(tokens)
        logger.info(f"[document_token_service.py] 문서의 토큰 개수: {len(tokens)}")

        # 3. 단어 분석
        document_token_list = compute_token_stats_by_word(tokens_per_file, name, file_path, cate1, cate2)
        logger.info(f"[document_token_service.py] 문서의 토큰 테이블 개수: {len(document_token_list)}")

        return document_token_list
    
    def get_segmented_tokens(self, file_path: str) -> List[dict]:
        """
        특정 file_path에 해당하는 DocumentToken과 Seg 데이터를 기반으로
        각 segment에 대해 {segment: segment 내용, tokens: []} 형태의 리스트를 반환합니다.
        """
        # 1. DocumentToken 데이터베이스에서 조회
        document_tokens = self.document_token_repository.get_tokens_by_document_path(file_path)

        # 2. Seg 데이터 JSON 파일에서 로드
        seg_file_path = f"segs/{os.path.basename(file_path)}.json"
        if not os.path.exists(seg_file_path):
            raise FileNotFoundError(f"Seg file not found for path: {seg_file_path}")

        with open(seg_file_path, "r", encoding="utf-8") as seg_file:
            file_segs = json.load(seg_file)  # JSON 파일에서 Seg 데이터 로드

        # 3. 각 segment에 대해 {segment: segment 내용, tokens: []} 생성
        result = []
        for segment_index, segment in enumerate(file_segs):
            col_id = segment_index + 1  # segment index + 1
            segment_dict = {
                "segment": segment,
                "tokens": []
            }

            # DocumentToken 중 col_id가 현재 segment의 col_id와 일치하는 token 추가
            for document_token in document_tokens:
                if document_token.col_id == col_id:
                    # 의미사전과 불용어사전 조회
                    meaning_result = self.dictionary_service.search_meaning_dictionary(document_token.value)
                    stopwords_result = self.dictionary_service.search_stopwords(document_token.value)
                    
                    # 기타 토큰은 불용어사전으로 취급
                    if document_token.word_type == '기타':
                        dictionary = 'stopwords'
                    else:
                        # 사전 조회 결과에 따라 dictionary 태그 결정
                        dictionary = "both" if meaning_result and stopwords_result else "meaning" if meaning_result else "stopwords" if stopwords_result else "other"
                        
                        
                    segment_dict["tokens"].append({
                        "word": document_token.value,
                        "word_type": document_token.word_type, 
                        "dictionary": dictionary
                    })

            result.append(segment_dict)

        return result

    def get_tokens_by_word_and_document_path(self, word, seg_id, file_path):
        """특정 단어와 문서 경로에 대한 토큰 정보를 조회합니다."""
        try:
            # 문서 경로로부터 카테고리 정보 추출
            path_parts = file_path.split('/')
            cate1 = path_parts[-2] if len(path_parts) >= 2 else None
            cate2 = None
            
            # 해당 단어의 토큰 정보 조회
            tokens = self.document_token_repository.get_tokens_by_word_and_document_path(word, seg_id, file_path)
            
            if not tokens:
                logger.info(f"'{word}' 단어에 대한 토큰 정보가 없습니다.")
                return {
                    'value': word,
                    'word_type': None,
                    'total_cnt': 0,
                    'domain_cnt': 0,
                    'doc_cnt': 0,
                    'col_cnt': 0,
                    'cate1': cate1,
                    'cate2': cate2,
                    'document_path': file_path,
                    'document_name': os.path.basename(file_path),
                    'col_id': seg_id
                }
            
            # 첫 번째 토큰 정보 사용 (동일한 단어는 동일한 통계 정보를 가짐)
            token = tokens[0]
            
            return {
                'value': token.value,
                'word_type': token.word_type,
                'total_cnt': token.total_cnt,
                'domain_cnt': token.domain_cnt,
                'doc_cnt': token.doc_cnt,
                'col_cnt': token.col_cnt,
                'cate1': token.cate1 or cate1,
                'cate2': token.cate2 or cate2,
                'document_path': token.document_path,
                'document_name': token.document_name,
                'col_id': token.col_id
            }
            
        except Exception as e:
            logger.error(f"단어 정보 조회 중 오류 발생: {str(e)}")
            raise

    def get_document_statistics(self, file_path: str) -> Dict:
        try:
            # 1. DocumentToken 데이터베이스에서 조회
            document_tokens = self.document_token_repository.get_tokens_by_document_path(file_path)
            if not document_tokens:
                return {
                    "success": True,
                    "statistics": {
                        "total_words": 0,
                        "word_types": {},
                        "word_statistics": {},
                        "overall_statistics": {
                            "average": 0,
                            "std_dev": 0
                        }
                    }
                }

            # 2. DataFrame 생성 (기타 단어 제외)
            df = pd.DataFrame([{
                'word': token.value,
                'word_type': token.word_type,
                'col_id': token.col_id,
                'col_cnt': token.col_cnt or 0,
                'total_cnt': token.total_cnt or 0,
                'cate1_cnt': token.cate1_cnt or 0,
                'cate2_cnt': token.cate2_cnt or 0,
                'doc_cnt': token.doc_cnt or 0,
                'cate1': token.cate1,
                'cate2': token.cate2
            } for token in document_tokens if token.word_type != '기타'])

            if len(df) == 0:
                return {
                    "success": True,
                    "statistics": {
                        "total_words": 0,
                        "word_types": {},
                        "word_statistics": {},
                        "overall_statistics": {
                            "average": 0,
                            "std_dev": 0
                        }
                    }
                }

            # 3. 기본 통계 계산
            statistics = {
                "total_words": int(len(df)),
                "word_types": df['word_type'].value_counts().to_dict(),
                "word_statistics": {},
                "overall_statistics": {}
            }

            # 4. 분할별 단어 빈도 계산 및 데이터베이스 업데이트
            updated_tokens = []
            
            # 모든 분할의 고유 ID 목록
            all_col_ids = sorted(df['col_id'].unique())
            
            # 전체 단어의 빈도 데이터를 저장하기 위한 리스트
            all_word_frequencies = []
            
            # 각 단어별로 분할별 빈도 계산
            for word, word_group in df.groupby('word'):
                # 각 분할별 빈도 계산
                frequencies = word_group.groupby('col_id')['col_cnt'].sum()
                
                # 모든 분할에 대해 빈도 계산 (없는 경우 0)
                all_frequencies = pd.Series(0, index=all_col_ids)
                all_frequencies.update(frequencies)
                
                # 전체 단어 빈도 데이터에 추가
                all_word_frequencies.extend(all_frequencies.values)
                
                # 평균과 표준편차 계산
                avg = float(all_frequencies.mean())
                std_dev = float(all_frequencies.std())
                
                # 첫 번째 행의 정보 사용 (모든 행이 동일한 정보를 가짐)
                first_row = word_group.iloc[0]
                
                # 전체 문서에서의 단어 빈도
                total_count = int(df[df['word'] == word]['col_cnt'].sum())
                
                # 대분류1에서의 단어 빈도
                cate1_count = int(df[(df['word'] == word) & (df['cate1'] == first_row['cate1'])]['col_cnt'].sum())
                
                # 대분류2에서의 단어 빈도
                cate2_count = int(df[(df['word'] == word) & (df['cate2'] == first_row['cate2'])]['col_cnt'].sum())
                
                # 현재 문서에서의 단어 빈도
                doc_count = int(df[df['word'] == word]['col_cnt'].sum())

                # 토큰 업데이트
                for token in document_tokens:
                    if token.value == word:
                        token.total_cnt = total_count
                        token.cate1_cnt = cate1_count
                        token.cate2_cnt = cate2_count
                        token.doc_cnt = doc_count
                        updated_tokens.append(token)
                
                # 단어 통계 정보 저장
                statistics["word_statistics"][word] = {
                    'average': avg,
                    'std_dev': std_dev,
                    'word_type': first_row['word_type'],
                    'total_cnt': total_count,
                    'cate1_cnt': cate1_count,
                    'cate2_cnt': cate2_count,
                    'doc_cnt': doc_count,
                    'segment_frequencies': all_frequencies.to_dict()
                }

            # 5. 전체 단어 통계 계산
            if all_word_frequencies:
                overall_avg = float(pd.Series(all_word_frequencies).mean())
                overall_std_dev = float(pd.Series(all_word_frequencies).std())
                
                statistics["overall_statistics"] = {
                    "average": overall_avg,
                    "std_dev": overall_std_dev
                }

            # 6. 데이터베이스 업데이트
            if updated_tokens:
                self.document_token_repository.update_token_counts(updated_tokens)

            return {
                "success": True,
                "statistics": statistics
            }

        except Exception as e:
            error_msg = f"문서 통계 계산 중 오류 발생: {str(e)}"
            logger.error(error_msg)
            logger.error(f"오류 상세 정보: {type(e).__name__}, {e.__traceback__.tb_lineno}번 줄")
            return {
                "success": False,
                "message": error_msg,
                "error_type": type(e).__name__,
                "error_line": e.__traceback__.tb_lineno
            }

    
if __name__ =="__main__":
    dir = 'D:/2025/parsing/docs_parsing/data/report.pdf'
    process_service = DocumentParsingService()
    metadata = {
        "source": "소스",
        "platform": "플랫폼",
        "cate1": "대분류1", 
        "cate2": "대분류2",
        "file_loc": dir,
        "url": "url"
    }
    results = process_service.create_document_token('kor', metadata )

    # JSON 파일로 저장
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)
