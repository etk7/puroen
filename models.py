from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.String(10))
    tall = db.Column(db.Float)
    gender = db.Column(db.String(10))
    goalweight = db.Column(db.Float)

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')

    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])

class Achievement(db.Model):
    __tablename__ = 'achievement'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('achievements', lazy=True))

'''
実行は
py models.py
既に同じテーブルがある場合、無視されて何も起きない

モデルを編集したら
flask db migrate -m
flask db upgrade
'''