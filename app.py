from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # セッション用のキー
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
    return render_template('index.html')

# --- ログインページ ---
@app.route('/login', methods=['GET', 'POST'])
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
    return render_template('login.html', message=message)

# --- 新規登録ページ ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        birthdate = request.form['birthdate']
        tall = float(request.form['tall'])
        gender = request.form['gender']
        goalweight = float(request.form['goalweight'])

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
    return render_template('signup.html', message=message)

# --- プロフィール確認ページ ---
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# --- アカウント情報変更ページ ---
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    message = ''

    if request.method == 'POST':
        user.email = request.form['email']
        user.birthdate = request.form['birthdate']
        user.tall = float(request.form['tall'])
        user.gender = request.form['gender']
        user.goalweight = float(request.form['goalweight'])

        db.session.commit()
        message = '情報を更新しました！'
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=user, message=message)

# --- ホーム画面（ログイン後） ---
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])

# --- ログアウト ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- アプリ起動 ---
if __name__ == '__main__':
    app.run(debug=True)
