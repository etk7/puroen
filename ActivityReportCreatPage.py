from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models import db, DailyRecord

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DB設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 初回だけDB作成
@app.before_first_request
def create_tables():
    db.create_all()

# 成果入力ページ
@app.route('/daily_input', methods=['GET', 'POST'])
def daily_input():
    if request.method == 'POST':
        # 入力取得
        input_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        weight = float(request.form['weight'])
        steps = int(request.form['steps'])

        # 仮のuser_id=1
        record = DailyRecord(user_id=1, date=input_date, weight=weight, steps=steps)
        db.session.add(record)
        db.session.commit()

        return redirect(url_for('daily_input'))  # 再読み込み

    return render_template('daily_input.html')

# トップをdaily_inputにリダイレクト
@app.route('/')
def index():
    return redirect(url_for('daily_input'))

if __name__ == '__main__':
    app.run(debug=True)
