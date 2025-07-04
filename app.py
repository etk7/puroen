@app.route('/group_post', methods=['GET', 'POST'])
def group_post():
    if request.method == 'POST':
        input_date = request.form['date']
        group_name = request.form['group_name']
        content = request.form['content']
        # ← ここでDBに保存する処理を書く
        return redirect(url_for('group_post'))

    return render_template('ActivityReportCreate.html')
