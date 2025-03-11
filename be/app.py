from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__)
# enable CORS
CORS(app)

@app.after_request
def after_request_callback(response):
  print(f'[{request.method}] {request.path} {response.status}')
  return response


from bp import (
    dbms, test, routes
)

blueprints = [
    dbms.bp,
    test.bp
]

for bp in blueprints:
    app.register_blueprint(bp)

if __name__ == '__main__':
    print("API server is running")
    app.run(host="0.0.0.0", port=9999)