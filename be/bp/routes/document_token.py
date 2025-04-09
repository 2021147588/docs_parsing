from flask import Blueprint, request, jsonify
import pandas as pd
import io

from bp.services.document_token_service import DocumentParsingService
from bp.services.dictionary_service import DictionaryService

from bp.utils.loggers import setup_logger
logger = setup_logger()

bp = Blueprint('token', __name__, url_prefix='/token')

@bp.route('/upload', methods=['POST'])
def upload_files_and_make_token_tables():
    
    metadata_file = request.files['metadata']
    lang = request.form['lang']
    
    # 엑셀 파일 확인
    if not metadata_file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({
            'success': False,
            'message': '메타데이터는 엑셀 파일이어야 합니다.'
        }), 400
    
    # 엑셀 파일 처리
    try:
        df = pd.read_excel(io.BytesIO(metadata_file.read()))
        required_columns = ['source', 'platform', 'cate1', 'cate2', 'file_loc', 'url']
        
        # 필수 컬럼 확인
        if not all(col in df.columns for col in required_columns):
            return jsonify({
                'success': False,
                'message': '필수 컬럼이 누락되었습니다.'
            }), 400
        
        # 메타데이터 리스트 생성
        metadata = []
        for _, row in df.iterrows():
            metadata_item = {
                'source': row['source'],
                'platform': row['platform'],
                'cate1': row['cate1'],
                'cate2': row['cate2'],
                'file_loc': row['file_loc'].replace('\\', '/'),
                'url': row['url']
            }
            metadata.append(metadata_item)

        all_document_counts = 0
        all_word_counts = 0
        total_file_path_lists = []
        all_documents = []
        
        for meta in metadata:
            document_parsing_service = DocumentParsingService()
            document_counts, word_counts, file_path_lists = document_parsing_service.create_document_token(lang, meta)
            all_document_counts += document_counts
            all_word_counts += word_counts
            total_file_path_lists.extend(file_path_lists)
            
            # 각 파일에 대한 문서 정보 가져오기
            for file_path in file_path_lists:
                try:
                    document = document_parsing_service.get_segmented_tokens(file_path)
                    all_documents.append({
                        'file_path': file_path,
                        'document': document
                    })
                except Exception as e:
                    logger.error(f"문서 {file_path} 처리 중 오류: {str(e)}")

        return jsonify({
            'success': True,
            'document_counts': all_document_counts,
            'word_counts': all_word_counts,
            'total_file_path_lists': total_file_path_lists,
            'documents': all_documents,
            'message': '엑셀 파일 처리 완료'
        }), 200
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f'엑셀 파일 처리 중 오류가 발생했습니다: {str(error_details)}')
        return jsonify({
            'success': False,
            'message': f'엑셀 파일 처리 중 오류가 발생했습니다: {str(e)}',
        }), 400

@bp.route('document/word/', methods=["POST"])
def get_word_info_by_word():
    data = request.get_json()
    file_path = data.get('file_path')
    word = data.get('word')
    seg_id = data.get('seg_id')
    logger.info(f"data: {data}")

    document_parsing_service = DocumentParsingService()
    dictionary_service = DictionaryService()
    document = document_parsing_service.get_tokens_by_word_and_document_path(word, seg_id, file_path)
    meaning_dictionary_result = dictionary_service.search_meaning_dictionary(word)
    stopwords_result = dictionary_service.search_stopwords(word)
    
    return jsonify({
        'success': True,
        'document': document,
        'meaning_dictionary': meaning_dictionary_result,
        'stopwords': stopwords_result
    }), 200


@bp.route('/document', methods=["POST"])
def get_document_by_id():
    data = request.get_json()
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({
            'success': False,
            'message': '파일 경로가 제공되지 않았습니다.'
        }), 400
    
    logger.info(f"요청된 파일 경로: {file_path}")
    
    try:
        document_parsing_service = DocumentParsingService()
        document = document_parsing_service.get_segmented_tokens(file_path)
        
        return jsonify({
            'success': True,
            'document': document
        }), 200
    except FileNotFoundError as e:
        logger.error(f"파일을 찾을 수 없습니다: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'파일을 찾을 수 없습니다: {str(e)}'
        }), 404
    except Exception as e:
        logger.error(f"문서 처리 중 오류가 발생했습니다: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'문서 처리 중 오류가 발생했습니다: {str(e)}'
        }), 500


@bp.route('/document/statistics/<int:id>', methods=["GET"])
def get_document_statistics(id: int):
    return jsonify({
        'success': True
    }), 200

@bp.route('/document/batch_update', methods=["POST"])
def batch_update_dictionaries():
    data = request.get_json()
    file_path = data.get('file_path')
    tokens = data.get('tokens', [])
    
    if not file_path or not tokens:
        return jsonify({
            'success': False,
            'message': '파일 경로와 토큰 정보가 필요합니다.'
        }), 400
    
    try:
        dictionary_service = DictionaryService()
        meaning_count = 0
        stopwords_count = 0
        
        for token in tokens:
            word = token.get('word')
            word_type = token.get('word_type')
            cate1 = token.get('cate1')
            cate2 = None
            dictionary = token.get('dictionary')
            if dictionary == 'stopwords':
                # 불용어사전에 추가 (카운트 증가 없이)
                result = dictionary_service.add_to_stopwords(word, increment_count=False)
                if result.get('success'):
                    stopwords_count += 1
            else:
                # 의미사전에 추가 (카운트 증가 없이)
                result = dictionary_service.add_to_dictionary(word, cate1, cate2, increment_count=False)
                if result.get('success'):
                    meaning_count += 1
        
        return jsonify({
            'success': True,
            'meaning_count': meaning_count,
            'stopwords_count': stopwords_count,
            'message': f'의미사전에 {meaning_count}개, 불용어사전에 {stopwords_count}개의 단어가 추가되었습니다.'
        }), 200
        
    except Exception as e:
        logger.error(f'사전 일괄 업데이트 중 오류 발생: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'사전 업데이트 중 오류가 발생했습니다: {str(e)}'
        }), 400

@bp.route('/dictionary/add', methods=['POST'])
def add_to_dictionary():
    """
    의미사전에 단어를 추가합니다.
    
    요청 본문:
    {
        "word": "추가할 단어",
        "cate1": "1차 카테고리",
        "cate2": "2차 카테고리"
    }
    
    응답:
    {
        "success": true/false,
        "message": "결과 메시지"
    }
    """
    data = request.get_json()
    
    if not data or 'word' not in data:
        return jsonify({
            'success': False,
            'message': '단어 정보가 필요합니다.'
        }), 400
    
    word = data.get('word')
    cate1 = data.get('cate1')
    cate2 = None
    
    try:
        dictionary_service = DictionaryService()
        result = dictionary_service.add_to_dictionary(word, cate1, cate2, increment_count=True)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', '단어가 추가되었습니다.')
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '단어 추가에 실패했습니다.')
            }), 400
            
    except Exception as e:
        logger.error(f'의미사전에 단어 추가 중 오류 발생: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'의미사전에 단어를 추가하는 중 오류가 발생했습니다: {str(e)}'
        }), 500

@bp.route('/dictionary/remove', methods=['POST'])
def remove_from_dictionary():
    """
    의미사전에서 단어를 삭제합니다.
    
    요청 본문:
    {
        "word": "삭제할 단어",
        "cate1": "1차 카테고리",
        "cate2": "2차 카테고리"
    }
    
    응답:
    {
        "success": true/false,
        "message": "결과 메시지"
    }
    """
    data = request.get_json()
    
    if not data or 'word' not in data:
        return jsonify({
            'success': False,
            'message': '단어 정보가 필요합니다.'
        }), 400
    
    word = data.get('word')
    cate1 = data.get('cate1')
    cate2 = None
    
    try:
        dictionary_service = DictionaryService()
        result = dictionary_service.remove_from_dictionary(word, cate1, cate2)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', '단어가 삭제되었습니다.')
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '단어 삭제에 실패했습니다.')
            }), 400
            
    except Exception as e:
        logger.error(f'의미사전에서 단어 삭제 중 오류 발생: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'의미사전에서 단어를 삭제하는 중 오류가 발생했습니다: {str(e)}'
        }), 500

@bp.route('/stopwords/add', methods=['POST'])
def add_to_stopwords():
    """
    불용어사전에 단어를 추가합니다.
    
    요청 본문:
    {
        "word": "추가할 단어",
        "cate1": "1차 카테고리",
        "cate2": "2차 카테고리"
    }
    
    응답:
    {
        "success": true/false,
        "message": "결과 메시지"
    }
    """
    data = request.get_json()
    
    if not data or 'word' not in data:
        return jsonify({
            'success': False,
            'message': '단어 정보가 필요합니다.'
        }), 400
    
    word = data.get('word')
    cate1 = data.get('cate1')
    cate2 = None
    
    try:
        dictionary_service = DictionaryService()
        result = dictionary_service.add_to_stopwords(word, cate1, cate2, increment_count=True)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', '단어가 추가되었습니다.')
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '단어 추가에 실패했습니다.')
            }), 400
            
    except Exception as e:
        logger.error(f'불용어사전에 단어 추가 중 오류 발생: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'불용어사전에 단어를 추가하는 중 오류가 발생했습니다: {str(e)}'
        }), 500

@bp.route('/stopwords/remove', methods=['POST'])
def remove_from_stopwords():
    """
    불용어사전에서 단어를 삭제합니다.
    
    요청 본문:
    {
        "word": "삭제할 단어",
        "cate1": "1차 카테고리",
        "cate2": "2차 카테고리"
    }
    
    응답:
    {
        "success": true/false,
        "message": "결과 메시지"
    }
    """
    data = request.get_json()
    
    if not data or 'word' not in data:
        return jsonify({
            'success': False,
            'message': '단어 정보가 필요합니다.'
        }), 400
    
    word = data.get('word')
    cate1 = data.get('cate1')
    cate2 = None
    try:
        dictionary_service = DictionaryService()
        result = dictionary_service.remove_from_stopwords(word, cate1, cate2, increment_count=True)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', '단어가 삭제되었습니다.')
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', '단어 삭제에 실패했습니다.')
            }), 400
            
    except Exception as e:
        logger.error(f'불용어사전에서 단어 삭제 중 오류 발생: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'불용어사전에서 단어를 삭제하는 중 오류가 발생했습니다: {str(e)}'
        }), 500

@bp.route('/document/tokens', methods=['GET'])
def get_document_tokens():
    """
    문서 토큰 테이블의 모든 데이터를 조회합니다.
    
    응답:
    {
        "success": true/false,
        "tokens": [
            {
                "id": 1,
                "word": "단어",
                "word_type": "품사",
                "cate1": "1차 카테고리",
                "cate2": "2차 카테고리",
                "total_cnt": 10,
                "domain_cnt": 2,
                "doc_cnt": 3
            },
            ...
        ],
        "total_count": 100
    }
    """
    try:
        # 페이지네이션 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 필터링 파라미터
        word = request.args.get('word', '')
        word_type = request.args.get('word_type', '')
        cate1 = request.args.get('cate1', '')
        cate2 = request.args.get('cate2', '')
        
        # 정렬 파라미터
        sort_by = request.args.get('sort_by', 'total_cnt')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 서비스 호출
        dictionary_service = DictionaryService()
        result = dictionary_service.get_document_tokens(
            page=page,
            per_page=per_page,
            word=word,
            word_type=word_type,
            cate1=cate1,
            cate2=cate2,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return jsonify({
            'success': True,
            'tokens': result['tokens'],
            'total_count': result['total_count'],
            'page': page,
            'per_page': per_page,
            'total_pages': result['total_pages']
        }), 200
        
    except Exception as e:
        logger.error(f'문서 토큰 조회 중 오류 발생: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'문서 토큰을 조회하는 중 오류가 발생했습니다: {str(e)}'
        }), 500

