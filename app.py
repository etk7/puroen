from flask import Flask, render_template, request, redirect, session, url_for
from models import db, User, FriendRequest, Achievement
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import os
import calendar
from datetime import datetime
import sqlite3

app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')  # セッションキー
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'users.db')

db.init_app(app)
migrate = Migrate(app, db)

# DB接続用の関数（SQLiteの生SQLを使う場合のみ）
def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# 歩数に応じた色を返す関数
def get_color_for_steps(steps):
    if steps >= 10000:
        return "#4caf50"  # 緑
    elif steps >= 5000:
        return "#ffeb3b"  # 黄
    elif steps > 0:
        return "#f44336"  # 赤
    else:
        return "#e0e0e0"  # グレー（データなしや0歩）

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

# ---友達申請---
@app.route('/FriendApplyPage', methods=['POST'])
def friend_apply():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    target_id = int(request.form['target_id'])

    # 双方向の既存申請確認
    existing = FriendRequest.query.filter(
        ((FriendRequest.from_user_id == session['user_id']) & (FriendRequest.to_user_id == target_id)) |
        ((FriendRequest.from_user_id == target_id) & (FriendRequest.to_user_id == session['user_id']))
    ).first()

    if not existing:
        new_request = FriendRequest(
            from_user_id=session['user_id'],
            to_user_id=target_id,
            status='pending'
        )
        db.session.add(new_request)
        db.session.commit()

    return redirect(url_for('friend_apply_confirm', target_id=target_id))

# ---友達申請確認---
@app.route('/FriendApplyConfirmPage/<int:target_id>', methods=['GET'])
def friend_apply_confirm(target_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    target_user = User.query.get(target_id)
    if not target_user:
        return "ユーザーが存在しません", 404

    return render_template('FriendApplyConfirmPage.html', target_user=target_user)

# ---友達申請承認---
@app.route('/FriendApplyReceptPage', methods=['GET'])
def friend_apply_recept():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # 自分宛てで、まだ未承諾の申請を取得
    pending_requests = FriendRequest.query.filter_by(to_user_id=user_id, status='pending').all()

    return render_template('FriendApplyReceptPage.html', requests=pending_requests)

# ---友達申請受信---
@app.route('/FriendApplyAcceptPage/<int:request_id>', methods=['POST'])
def friend_apply_accept(request_id):
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

    return render_template('FriendApplyAcceptPage.html', message=message)

# ---友達一覧---
@app.route('/FriendListPage')
def friend_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # 友達リスト取得（双方向で検索）
    friends = db.session.query(User).join(
        FriendRequest,
        ((FriendRequest.from_user_id == user_id) & (FriendRequest.to_user_id == User.id)) |
        ((FriendRequest.to_user_id == user_id) & (FriendRequest.from_user_id == User.id))
    ).filter(FriendRequest.status == 'accepted').all()

    return render_template('FriendListPage.html', friends=friends)

# ---友達のプロフィール---
@app.route('/FriendInfoPage/<int:user_id>')
def friend_info(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    friend = User.query.get_or_404(user_id)
    return render_template('FriendInfoPage.html', user=friend)

# ---申請相手ユーザー画面---
@app.route('/ApplicantPage/<int:user_id>')
def applicant_page(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    return render_template('ApplicantPage.html', user=user)

# --- 成果入力ページ ---
@app.route('/AchievementCreatePage', methods=['GET', 'POST'])
def achievement_create():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form['date']
        steps = request.form['steps']
        weight = request.form['weight']

        return render_template('AchievementConfirmPage.html',
                               date=date,
                               steps=steps,
                               weight=weight)

    return render_template('AchievementCreatePage.html')

# --- 成果入力確認ページ ---
@app.route('/AhievementConfirmPage', methods=['GET', 'POST'])
def achievement_confirm():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        date = request.form['date']
        steps = request.form['steps']
        weight = request.form['weight']
        user_id = session['user_id']

        new_achievement = Achievement(
            user_id=user_id,
            date=date,
            steps=int(steps),
            weight=float(weight)
        )
        db.session.add(new_achievement)
        db.session.commit()
        return redirect(url_for('my_achievements'))

    # GET時は確認画面表示
    date = request.args.get('date')
    steps = request.args.get('steps')
    weight = request.args.get('weight')
    return render_template('AchievementConfirmPage.html', date=date, steps=steps, weight=weight)

# ---成果一覧---
@app.route('/MyAchievementsPage')
def my_achievements():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    achievements = Achievement.query.filter_by(user_id=user_id).order_by(Achievement.date.desc()).all()
    return render_template('MyAchievementsPage.html', achievements=achievements)

# ---歩数カレンダー---
@app.route('/step_calendar')
def step_calendar():
    # 本来はsessionからログインユーザーIDを取得
    user_id = session.get('user_id', 1)  # 仮で1を使う

    today = datetime.today()
    year = today.year
    month = today.month

    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, steps FROM achievement
        WHERE user_id = ? AND date BETWEEN ? AND ?
    """, (user_id, first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))
    rows = cur.fetchall()

    step_map = {}
    for row in rows:
        step_map[row['date']] = get_color_for_steps(row['steps'])

    cal = calendar.Calendar(firstweekday=6)  # 日曜始まり
    weeks = cal.monthdatescalendar(year, month)

    return render_template('StepCalendarPage.html',
                           weeks=weeks,
                           step_map=step_map,
                           year=year,
                           month=month)
# --- ログアウト ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- アプリ起動 ---
if __name__ == '__main__':
    app.run(debug=True)
