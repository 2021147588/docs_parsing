from flask import Blueprint, request, jsonify

bp = Blueprint('dbms', __name__, url_prefix='/dbms')

@bp.route('/check', methods=["POST"])
def dbms_check():
    return jsonify({
        'success': True
    }), 200

