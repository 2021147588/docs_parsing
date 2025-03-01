from flask import Blueprint, request, jsonify

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/check', methods=["GET"])
def test_check():
    return jsonify({
        'success': True
    }), 200

