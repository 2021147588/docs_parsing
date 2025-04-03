from flask import Flask, request
from flask_cors import CORS

from bp.dbms import get_db
from bp import (
    dbms, test, routes
)
from bp.utils.loggers import setup_logger
from bp.routes import document_token


logger = setup_logger()

blueprints = [
    dbms.bp,
    test.bp,
    document_token.bp  # Add this line to register the document_token blueprint
]

app = Flask(__name__)
CORS(app)



for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == '__main__':
    logger.info("API server is running")
    app.run(host="0.0.0.0", port=9999, debug=True)
