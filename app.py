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

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')

    from_user = db.relationship('User', foreign_keys=[from_user_id])
    to_user = db.relationship('User', foreign_keys=[to_user_id])
    
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

@app.route('/GroupCreatePage', methods=['GET', 'POST'])
def group_create():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        group_name = request.form['group_name']
        description = request.form['description']
        return render_template('GroupCreateConfirmPage.html', group_name=group_name, description=description)

    return render_template('GroupCreatePage.html')

@app.route('/GroupCreateConfirmPage', methods=['POST'])
def confirm_group_creation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    group_name = request.form['group_name']
    description = request.form['description']

    # モデルがある場合はここで保存処理（例）
    new_group = Group(name=group_name, description=description, owner_id=session['user_id'])
    db.session.add(new_group)
    db.session.commit()

    return redirect(url_for('home'))  # またはグループ詳細ページなど

@app.route('/FriendApplyPage/<int:target_id>', methods=['GET'])
def friend_apply_page(target_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    target_user = User.query.get_or_404(target_id)
    return render_template('FriendApplyPage.html', target_user=target_user)

@app.route('/FriendApplyConfirmPage/<int:target_id>', methods=['POST'])
def friend_apply_confirm(target_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    from_id = session['user_id']
    to_id = target_id

    # 重複確認（既に申請済みや友達関係など）
    existing_request = FriendRequest.query.filter_by(from_user_id=from_id, to_user_id=to_id).first()
    if existing_request:
        message = "すでに申請済みです。"
    else:
        new_request = FriendRequest(from_user_id=from_id, to_user_id=to_id)
        db.session.add(new_request)
        db.session.commit()
        message = "友達申請を送信しました。"

    return render_template('FriendApplyConfirmPage.html', message=message)

@app.route('/FriendApplyAcceptPage', methods=['GET'])
def friend_apply_accept():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # 自分宛てで、まだ未承諾の申請を取得
    pending_requests = FriendRequest.query.filter_by(to_user_id=user_id, status='pending').all()

    return render_template('FriendApplyAcceptPage.html', requests=pending_requests)

@app.route('/FriendApplyReceptPage/<int:request_id>', methods=['POST'])
def friend_apply_recept(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    friend_request = FriendRequest.query.get(request_id)

    if not friend_request or friend_request.to_user_id != session['user_id']:
        return "無効なリクエストです", 403

    action = request.form.get('action')

    if action == 'accept':
        friend_request.status = 'accepted'
        db.session.commit()
        message = f"{friend_request.from_user.username}さんの申請を承諾しました！"
    elif action == 'reject':
        friend_request.status = 'rejected'
        db.session.commit()
        message = f"{friend_request.from_user.username}さんの申請を拒否しました。"
    else:
        message = "不正なアクションです。"

    return render_template('FriendApplyReceptPage.html', message=message)

# --- ログアウト ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- アプリ起動 ---
if __name__ == '__main__':
    app.run(debug=True)
    
#---活動報告投稿---

