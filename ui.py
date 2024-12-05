import re
import zipfile
import io

from pathlib import Path
from flask import Flask, render_template, session, redirect, url_for, request, jsonify, abort, send_file
from db.db import check_user_pwd, get_message, get_user_mailboxes, retreive_message_attachments, delete_message

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

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

@app.route('/settings')
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<p>Settings</p>"

@app.route('/sent')
def sent():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<p>Sent</p>"

@app.route('/new')
def new():
    if 'username' not in session:
        return redirect(url_for('login'))
    return "<p>New</p>"

@app.route('/view/<id>')
def view(id=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if id != None:
        message = get_message(id)
        if not message:
            abort(404)
        
        mailboxes = get_user_mailboxes(session['username'])
        if not mailboxes:
            abort(404)

        found = False
        for box in mailboxes:
            if box["mailboxId"] == message["messageMailbox"]:
                found = True
                break
        
        if not found:
            abort(404)
        
        # split_msg = message["messageContent"].split("\r\n")
        subject = re.search(r"Subject: ([^\r\n]*)\r\n", message["messageContent"])
        if not subject:
            subject = ""
        
        payload_match = message["messageContent"].split("\r\n\r\n", 1)
        if len(payload_match) == 2:
            message_body = payload_match[1]
        else:
            message_body = message["messageContent"]
        
        attachments_set = False
        attachment_list = retreive_message_attachments(id)
        if attachment_list:
            attachments_set = True
    else:
        abort(404)
    return render_template('view.html', id=id, message=message, subject=subject.group(1), message_body=message_body, attachments=attachments_set)

@app.route('/attachments/<id>')
def attachments(id=None):
    if 'username' not in session:
        abort(403)
    
    if id == None:
        abort(404)
    
    message = get_message(id)
    if not message:
        abort(404)
    
    mailboxes = get_user_mailboxes(session['username'])
    if not mailboxes:
        abort(404)

    found = False
    for box in mailboxes:
        if box["mailboxId"] == message["messageMailbox"]:
            found = True
            break
    
    if not found:
        abort(404)
    
    attachment_list = retreive_message_attachments(id)
    if not attachment_list:
        abort(404)
    
    try:
        files_to_zip = [Path(file["attachmentLocation"]) for file in attachment_list]
        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, 'w') as zipf:
            for file in files_to_zip:
                if file.exists():
                    zipf.write(file, arcname=file.name)
                else:
                    abort(400)

        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='attachments.zip'
        )

    except Exception as e:
        abort(500)

@app.route('/delete/<id>')
def delete(id=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if id == None:
        abort(404)
    
    message = get_message(id)
    if not message:
        abort(404)
    
    mailboxes = get_user_mailboxes(session['username'])
    if not mailboxes:
        abort(404)

    found = False
    for box in mailboxes:
        if box["mailboxId"] == message["messageMailbox"]:
            found = True
            break
    
    if not found:
        abort(404)

    if not delete_message(id):
        abort(404)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()