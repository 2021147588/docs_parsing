from flask import Flask, request
from flask_cors import CORS

from bp.dbms import get_db, close_db
from bp import (
    dbms, test, routes
)
from bp.utils.loggers import setup_logger

logger = setup_logger()

blueprints = [
    dbms.bp,
    test.bp
]

app = Flask(__name__)
CORS(app)

get_db()

app.teardown_appcontext(close_db)

for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == '__main__':
    logger.info("API server is running")
    app.run(host="0.0.0.0", port=9999)
