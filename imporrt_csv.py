import csv
from datetime import datetime
from flask import Flask
from models import db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def load_users(csv_file):
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User(
                id=int(row['id']),
                username=row['username'],
                email=row['email'],
                password=row['password'],
                height=float(row['height']),
                birthdate=datetime.strptime(row['birthdate'], '%Y-%m-%d').date(),
                gender=row['gender'],
                goal_weight=float(row['goal_weight'])
            )
            db.session.add(user)

def load_posts(csv_file):
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            post = Post(
                id=int(row['id']),
                user_id=int(row['user_id']),
                group_id=int(row['group_id']),
                content=row['content'],
                timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
            )
            db.session.add(post)

with app.app_context():
    db.drop_all()  # ← 既存のDBを一度リセット（必要に応じて）
    db.create_all()
    load_users('users.csv')
    load_posts('contents.csv')
    db.session.commit()
    print("CSVデータをインポートしました。")
