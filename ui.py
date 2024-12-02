from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from db.db import check_user_pwd

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    return "<p>Hello, World!</p>"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if "email" not in request.form or "pwd" not in request.form:
            return jsonify({
                "status": "error"
            })
        
        uname = request.form['email']
        pwd = request.form['pwd']
        if check_user_pwd(uname, pwd):
            session['username'] = request.form['email']
            return jsonify({
                "status": "success"
            })
        return jsonify({
            "status": "error"
        })
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()