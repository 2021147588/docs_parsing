from flask import Blueprint, request, jsonify
import pandas as pd
import io

from be.bp.services.document_token_service import DocumentParsingService
from be.bp.repositories.document_token_repository import DocumentTokenRepository
from be.bp.utils.loggers import setup_logger
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
        for meta in metadata:
            document_parsing_service = DocumentParsingService()
            document_counts, word_counts, file_path_lists = document_parsing_service.create_document_token(lang, meta)
            all_document_counts += document_counts
            all_word_counts += word_counts
            total_file_path_lists.extend(file_path_lists)   

        return jsonify({
            'success': True,
            'document_counts': document_counts,
            'word_counts': word_counts,
            'total_file_path_lists': total_file_path_lists,
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

@bp.route('/document/word', methods=["POST"])
def get_word_info_by_word():
    data = request.get_json()
    file_path = data.get('file_path')
    word = data.get('word')
    seg_id = data.get('seg_id')
    logger.info(f"data: {data}")

    document_parsing_service = DocumentParsingService()
    document = document_parsing_service.get_tokens_by_word_and_document_path(word, seg_id, file_path)

    return jsonify({
        'success': True,
        'document': document
    }), 200


@bp.route('/document', methods=["POST"])
def get_document_by_id():
    data = request.get_json()
    file_path = data.get('file_path')
    document_parsing_service = DocumentParsingService()
    document = document_parsing_service.get_segmented_tokens(file_path)

    return jsonify({
        'success': True,
        'document': document
    }), 200


@bp.route('/document/statistics/<int:id>', methods=["GET"])
def get_document_statistics(id: int):
    return jsonify({
        'success': True
    }), 200

