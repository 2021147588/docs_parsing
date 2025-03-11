from flask import Blueprint, request, jsonify

bp = Blueprint('token', __name__, url_prefix='/token')

@bp.route('/', methods=["POST"])
def make_token_tables():
    
    
    return jsonify({
        'success': True
    }), 200

