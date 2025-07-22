from app import app, db

with app.app_context():
    db.create_all()


'''
実行は
py create_db.py
'''