ダイエット記録・共有アプリ

このアプリは、ユーザーが自分の体重や歩数などの健康記録を保存・可視化し、他のユーザーと成果を共有できるWebアプリケーションです。FlaskとSQLiteをベースに構築されています。

---

------プログラムのファイル構成------

puroen/
├── app.py # Flaskのメインアプリケーション
├── models.py # データベースのモデル定義
├── create_db.py
├── templates/ # HTMLテンプレート
    ├── AccountInfoChangePage.html
    ├── AchievementConfirmPage.html
    ├── AchievementCreatePage.html
    ├── base.html
    ├── FriendApplyAcceptPage.html
    ├── FriendApplyConfirmPage.html
    ├── FriendApplyPage.html
    ├── FriendApplyReceptPage.html
    ├── HomePage.html
    ├── LoginOrSignupPage.html
    ├── LoginPage.html
    ├── MyAchievementsPage.html
    ├── Profile.html
    ├── SearchResultPage.html
    ├── SignupPage.html
    ├── StepCalendarPage.html
    ├── UserSearchPage.html
    └── WeightGraphPage.html
├── instance/
│ └── users.db # SQLite データベース
└── README.md # このファイル


------実行方法------

1.仮想環境の作成と起動（任意）
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windowsなら venv\Scripts\activate

2.データベースの初期化（初回のみ）
flask db init
flask db upgrade

3.アプリケーションの起動
py app.py

4.ブラウザでアクセス
http://127.0.0.1:5000



------アプリの操作方法------

〇ユーザ登録・ログイン
    ・初回は「ユーザ登録」からアカウントを作成
    ・ログイン後に各機能を利用可能
〇一日の成果入力（体重・歩数）
    ・ホーム画面から「成果入力」ページへ移動
    ・日付、体重、歩数を記録
    ・記録は「自分の成果一覧」から確認可能
〇歩数カレンダー表示
    ・カレンダー形式で毎日の歩数を表示
    ・歩数は5000歩ごとで塗りつぶされる色が変わる
    ・月を切り替えて過去の記録も閲覧可能
〇体重推移グラフ
    ・折れ線グラフで体重の変化を可視化
〇友達機能
    ・ユーザ機能から友達申請を送信
    ・承認後、友達のプロフィールや目標体重を閲覧可能
    