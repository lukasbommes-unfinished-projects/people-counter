from flask import make_response, jsonify
from server.errors import bp


@bp.app_errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
