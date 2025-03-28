from flask import Blueprint, request, jsonify
from be.bp.dbms.mariadb import get_db  # 🔹 DB 접속 함수 불러오기

bp = Blueprint('dbms', __name__, url_prefix='/dbms')

# @bp.route('/check', methods=["POST"])
# def dbms_check():
#     try:
#         conn = get_db()
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT 1")  # 간단한 쿼리로 DB 확인
#         return jsonify({'success': True, 'db_status': 'connected'}), 200
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500
