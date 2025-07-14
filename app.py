from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')  # セッションキー
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# --- モデル定義 ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.String(10))
    tall = db.Column(db.Float)
    gender = db.Column(db.String(10))
    goalweight = db.Column(db.Float)

# --- データベース初期化（初回起動時） ---
with app.app_context():
    db.create_all()

# --- トップページ（ログイン or 登録選択） ---
@app.route('/')
def index():
    return render_template('LoginOrSignupPage.html')

# --- ログインページ ---
@app.route('/LoginPage', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('profile'))
        else:
            message = 'ユーザー名またはパスワードが違います'
    return render_template('LoginPage.html', message=message)

# --- 新規登録ページ ---
@app.route('/SignupPage', methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        birthdate = request.form['birthdate']
        gender = request.form['gender']

        try:
            tall = float(request.form['tall'])
            goalweight = float(request.form['goalweight'])
        except ValueError:
            message = '身長と目標体重には数字を入力してください'
            return render_template('SignupPage.html', message=message)

        if User.query.filter_by(username=username).first():
            message = 'このユーザー名はすでに使われています'
        elif User.query.filter_by(email=email).first():
            message = 'このメールアドレスはすでに使われています'
        else:
            new_user = User(
                username=username,
                email=email,
                password=password,
                birthdate=birthdate,
                tall=tall,
                gender=gender,
                goalweight=goalweight
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            return redirect(url_for('profile'))
    return render_template('SignupPage.html', message=message)

# --- プロフィール確認ページ ---
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('Profile.html', user=user)

# --- アカウント情報変更ページ ---
@app.route('/account/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    message = ''

    if request.method == 'POST':
        user.email = request.form['email']
        user.birthdate = request.form['birthdate']
        user.gender = request.form['gender']

        try:
            user.tall = float(request.form['tall'])
            user.goalweight = float(request.form['goalweight'])
        except ValueError:
            message = '身長と目標体重には数字を入力してください'
            return render_template('AccountInfoChangePage.html', user=user, message=message)

        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('AccountInfoChangePage.html', user=user, message=message)

# --- ホーム画面（ログイン後） ---
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('HomePage.html', username=session['username'])

# ---ユーザ検索画面---
@app.route('/UserSearchPage', methods=['GET'])
def user_search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('UserSearchPage.html')   

# ---ユーザ検索結果---
@app.route('/SearchResultPage', methods=['POST'])
def search_result():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    keyword = request.form['keyword']
    results = User.query.filter(
        ((User.username.contains(keyword)) | (User.email.contains(keyword))) &
        (User.id != session['user_id'])
    ).all()


    return render_template('SearchResultPage.html', keyword=keyword, results=results)

# --- ログアウト ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- アプリ起動 ---
if __name__ == '__main__':
    app.run(debug=True)
