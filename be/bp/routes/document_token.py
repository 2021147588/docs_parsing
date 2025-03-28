from flask import Blueprint, request, jsonify
import pandas as pd
import io

from be.bp.services.document_token_service import DocumentParsingService
from be.bp.repositories.document_token_repository import DocumentTokenRepository

bp = Blueprint('token', __name__, url_prefix='/token')

@bp.route('/upload', methods=['POST'])
def upload_files_and_make_token_tables(lang: str):
    if 'files' not in request.files or 'metadata' not in request.files:
        return jsonify({
            'success': False,
            'message': '파일이 누락되었습니다.'
        }), 400
    
    pdf_files = request.files.getlist('files')
    metadata_file = request.files['metadata']
    
    # PDF 파일 확인
    for pdf in pdf_files:
        if not pdf.filename.endswith('.pdf'):
            return jsonify({
                'success': False,
                'message': 'PDF 파일만 업로드 가능합니다.'
            }), 400
    
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
                'file_loc': row['file_loc'],
                'url': row['url']
            }
            metadata.append(metadata_item)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'엑셀 파일 처리 중 오류가 발생했습니다: {str(e)}'
        }), 400

    document_parsing_service = DocumentParsingService()
    row_count = document_parsing_service.create_document_token(lang, metadata)
    
    return jsonify({
        'success': True,
        'row_count': row_count
    }), 200
    
@bp.route('/document/<int:id>', methods=["GET"])
def make_token_tables(id: int):
    
    
    return jsonify({
        'success': True
    }), 200

@bp.route('/document/statistics/<int:id>', methods=["GET"])
def make_token_tables(id):
    
    
    return jsonify({
        'success': True
    }), 200

