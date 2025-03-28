import pymysql

from be.config import host, port, user, password, db_name


import pymysql
from flask import g, current_app

# def get_db():
#     if 'db' not in g:
#         g.db = pymysql.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=db_name,
#             charset='utf8mb4',
#             autocommit=True
#         )
#     return g.db

def get_db():
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name,
        charset='utf8mb4',
        autocommit=True
    )

# def close_db(e=None):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()

