import re
import zipfile
import io
import time
import base64
import random

from pathlib import Path
from flask import Flask, render_template, session, redirect, url_for, request, jsonify, abort, send_file
from db.db import delete_user, get_user_messages, createUser, get_user_id, create_mailbox, delete_mailbox, check_user_pwd, get_message, get_user_mailboxes, retreive_message_attachments, delete_message, send_message, msg_db_type, update_receiver, update_sent, get_user, get_all_users, get_all_user_mailboxes, update_user, get_user_mailboxes, update_send_receive
from server.client.client import NuMailRequest
from server.client.reader import init_numail, read_numail
from server.message.Attachment import Attachment
from config.config import server_config, server_settings
# from config.config import server_settings
from errors.nuerrors import NuMailError
from server.client.dns import resolve_dns, decode_txt

config_path = Path(__file__).parent / "config" / "ui.conf"
server_config(config_path)
# print(server_config)

# DEBUG
# server_settings = {
#     "visible_domain": "numail.local",
#     "attachment_expire": 3600,
#     "attachment_delete_on_expire": 1,
#     "domain": "mail.numail.local",
#     "public_ip": "127.0.0.1",
#     "ip": "127.0.0.1",
# }

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    messages = get_user_messages(user_name=session["username"])
    if not messages:
        messages = []

    # print(messages)
    return render_template('index.html', messages=messages, isSent=False)

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
    
    currentUser = get_user(session['username'])
    if not currentUser:
        abort(404)

    if currentUser["isAdmin"]:
        users = get_all_users()
        mailboxes = get_all_user_mailboxes()
        if not mailboxes:
            mailboxes = []
    else:
        users = []
        mailboxes = []
    
    current_user_mb = get_user_mailboxes(session['username'])
    if not current_user_mb:
        current_user_mb = []
    
    users_serializable = []
    for user in users:
        users_serializable.append({
            key: (value.decode('utf-8') if isinstance(value, bytes) else value)
            for key, value in user.items()
            if key != "password"
        })
    
    mailbox_serializable = []
    for box in mailboxes:
        mailbox_serializable.append({
            key: (value.decode('utf-8') if isinstance(value, bytes) else value)
            for key, value in box.items()
        })


    ids = []

    def getId(length = 10, current=False):
        if current:
            return ids
        randomVal = ""
        while randomVal == "" or randomVal in ids:
            randomVal = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') for _ in range(length))
        
        ids.append(randomVal)
        return randomVal


    return render_template('settings.html', domain=server_settings["visible_domain"], user=currentUser, users=users_serializable, mailboxes=mailbox_serializable, usermb=current_user_mb, getId=getId)

@app.route('/usersettings', methods=['POST'])
def usersettings():
    if 'username' not in session:
        abort(403)
    
    user_field = request.form.get('user')
    pwd_field = request.form.get('pwd')
    fname_field = request.form.get('fname')
    lname_field = request.form.get('lname')
    displayName_field = request.form.get('displayName')
    company_field = request.form.get('company')
    admin_field = request.form.get('isAdmin')
    uname_field = request.form.get('uname')

    if not user_field:
        return jsonify({
            "status": "error",
        })
    
    currentUser = get_user(session["username"])
    if not currentUser or (str(currentUser["userId"]) != str(user_field) and not currentUser["isAdmin"]):
        abort(403)
    
    update_user_info = get_user_id(user_field)
    if not update_user_info:
        abort(403)

    if update_user_info["userName"] != uname_field:
        if update_user_info["userName"] == "admin":
            return jsonify({
                "status": "error",
                "message": "Unable to change username"
            })

        if not re.search(r"^[0-9_a-zA-Z\-.]+$", uname_field.strip(), re.MULTILINE):
            return jsonify({
                "status": "error",
                "message": "Username invalid"
            })
        
        test_user = get_user(uname_field.strip())
        if test_user:
            return jsonify({
                "status": "error",
                "message": "Username taken"
            })
        if not update_user(user_field, "userName", uname_field.strip()):
            return jsonify({
                "status": "error",
                "message": "Username Error"
            })
        
        if str(currentUser["userId"]) == str(user_field):
            session["username"] = uname_field.strip()

    if fname_field != update_user_info["firstName"]:
        if not update_user(user_field, "firstName", fname_field):
            return jsonify({
                "status": "error",
                "message": "First Name Error"
            })
    
    if lname_field != update_user_info["lastName"]:
        if not update_user(user_field, "lastName", lname_field):
            return jsonify({
                "status": "error",
                "message": "Last Name Error"
            })

    if displayName_field != update_user_info["displayName"]:
        if not update_user(user_field, "displayName", displayName_field):
            return jsonify({
                "status": "error",
                "message": "Display Name Error"
            })
    
    if company_field != update_user_info["company"]:
        if not update_user(user_field, "company", company_field):
            return jsonify({
                "status": "error",
                "message": "Company Error"
            })
    
    if pwd_field:
        if not update_user(user_field, "password", pwd_field):
            return jsonify({
                "status": "error",
                "message": "Password Error"
            })

    if currentUser["isAdmin"] and not request.form.get('self'):
        if not update_user(user_field, "isAdmin", admin_field if admin_field else False):
            return jsonify({
                "status": "error",
                "message": "Admin Error"
            })

    return jsonify({
        "status": "success",
    })

@app.route('/mbsettings', methods=['POST'])
def mbsettings():
    if 'username' not in session:
        abort(403)
    
    currentUser = get_user(session["username"])
    mailboxes = get_user_mailboxes(session["username"])
    if not currentUser or not mailboxes:
        abort(404)

    mailbox_names = []
    for mb in mailboxes:
        mailbox_names.append(mb["mbName"])

    input_fields = dict(request.form)
    # print(input_fields)
    fields = []
    for key, value in input_fields.items():
        hidden = re.search(r"hidden_([a-zA-Z0-9]+)$", key, re.MULTILINE)
        if hidden:
            if value not in mailbox_names and not currentUser["isAdmin"]:
                abort(403)
            fields.append([hidden.group(1), value])
    
    for field in fields:
        if f"canReceive_{field[0]}" in input_fields:
            update_send_receive(field[1], False, True)
        else:
            update_send_receive(field[1], False, False)

        if f"canSend_{field[0]}" in input_fields:
            update_send_receive(field[1], True, True)
        else:
            update_send_receive(field[1], True, False)
        
        if currentUser["isAdmin"]:
            if f"delete_{field[0]}" in input_fields:
                delete_mailbox(field[1])

    return jsonify({
        "status": "success",
    })

@app.route('/deleteuser/<id>', methods=['POST'])
def deleteuser(id=None):
    if 'username' not in session:
        abort(403)
    
    currentUser = get_user(session["username"])
    if not currentUser:
        abort(404)
    
    user_to_delete = get_user_id(str(id))
    if not user_to_delete:
        return jsonify({
            "status": "error",
            "message": "User to delete does not exist"
        })
    
    if user_to_delete["userName"] == "admin":
        return jsonify({
            "status": "error",
            "message": "Unable to delete admin account"
        })

    if currentUser["isAdmin"]:
        if not delete_user(str(id)):
            return jsonify({
                "status": "error",
            })

    return jsonify({
        "status": "success",
    })

@app.route('/createmb', methods=['POST'])
def createmb():
    if 'username' not in session:
        abort(403)

    email_field = request.form.get("email")
    uname_field = request.form.get("uid")
    send_field = request.form.get("canSend")
    receive_field = request.form.get("canReceive")

    if not email_field:
        return jsonify({
            "status": "error",
            "message": "Invalid Email"
        })
    elif not re.search(r"^[a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+$", email_field, re.MULTILINE):
        return jsonify({
            "status": "error",
            "message": "Invalid Email"
        })
    
    if not uname_field:
        return jsonify({
            "status": "error",
        })
    
    currentUser = get_user(session["username"])
    uid = get_user_id(uname_field)
    if not currentUser or not uid:
        abort(404)

    try:
        create_mailbox(
            user_name=uid["userName"],
            mb_name=email_field,
            mb_send=True if send_field else False,
            mb_receive=True if receive_field else False,
            read_confirm=False
        )
    except:
        return jsonify({
            "status": "error",
        })

    return jsonify({
        "status": "success",
    })

@app.route('/createuser', methods=['POST'])
def createuser():
    if 'username' not in session:
        abort(403)

    currentUser = get_user(session["username"])
    if not currentUser:
        abort(404)
    
    if not currentUser["isAdmin"]:
        abort(403)

    pwd_field = request.form.get("pwd")
    uname_field = request.form.get("uname")
    fname_field = request.form.get("fname")
    lname_field = request.form.get("lname")
    displayName_field = request.form.get("displayName")
    company_field = request.form.get("company")
    isAdmin_field = request.form.get("isAdmin")

    if not pwd_field:
        return jsonify({
            "status": "error",
            "message": "Invalid Password"
        })
    
    if not uname_field:
        return jsonify({
            "status": "error",
            "message": "Invalid Username"
        })
    
    if not displayName_field:
        return jsonify({
            "status": "error",
            "message": "Invalid Display Name"
        })

    try:
        createUser(user_name=uname_field, display_name=displayName_field, password=pwd_field, isAdmin=True if isAdmin_field else False, first_name=fname_field, last_name=lname_field, company=company_field)
    except:
        return jsonify({
            "status": "error",
        })

    return jsonify({
        "status": "success",
    })

@app.route('/sent')
def sent():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    messages = get_user_messages(user_name=session["username"])
    if not messages:
        messages = []
        
    return render_template('index.html', messages=messages, isSent=True)

@app.route('/new')
def new():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('new.html', id="", message={}, subject="", message_body="", attachments=[])

@app.route('/send', methods=['POST'])
async def send():
    if 'username' not in session:
        abort(403)
    
    from_field = request.form.get('from')
    to_field = request.form.get('to')
    subject = request.form.get('subject')
    message = request.form.get('data')
    read_confirm = False

    if not from_field or not to_field or not subject or not message:
        return jsonify({
            "status": "error",
            "message": "Missing subject, from, to, or body"
        })
    
    from_email_re = re.search(r"([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)$", from_field.strip(), re.MULTILINE)
    if not from_email_re:
        return jsonify({
            "status": "error",
            "message": "Invalid from address"
        })
    from_email = from_field.strip()
    
    mailboxes = get_user_mailboxes(session['username'])
    if not mailboxes:
        abort(404)
    
    found = False
    for box in mailboxes:
        if box["mbName"] == from_email_re.group(1):
            found = True
            break
    
    if not found or from_email_re.group(2) != server_settings["visible_domain"]:
        return jsonify({
            "status": "error",
            "message": "Invalid from address"
        })
    
    to_email_re = re.search(r"([a-zA-Z0-9.!#$%&'*+\-/=?^_`{|}~]+)@([a-zA-Z0-9._\-]+)$", to_field.strip(), re.MULTILINE)
    if not to_email_re:
        return jsonify({
            "status": "error",
            "message": "Invalid to address"
        })
    to_email = to_field.strip()

    
    normalized_message = message.replace('\r\n', '\n').replace('\n', '\r\n')
    normalized_message = f"Subject: {subject}\r\n\r\n" + normalized_message
    
    attachments = []
    uploaded_files = request.files.getlist('files[]')
    for file in uploaded_files:
        the_data = file.read()
        if len(the_data) > 0 and file.filename:
            data = f"Content-Disposition: attachment; filename=\"{file.filename}\"\r\nContent-Type: application/octet-stream\r\nContent-Transfer-Encoding: base64\r\n\r\n" + base64.b64encode(the_data).decode("utf-8")
            attachments.append(Attachment(data=data, expire=int(time.time()) + int(server_settings["attachment_expire"]), expireOnRetrieve=(int(server_settings["attachment_delete_on_expire"]) != 0)))

    try:
        upload_status = send_message(
            from_addr = from_email,
            to_addr = to_email,
            msgt = 0,
            data = normalized_message,
            readConfirm = True if read_confirm else False,
            receiver_id = None,
            attachments = attachments
        )

        if not upload_status:
            # print(1)
            return jsonify({
                "status": "error",
                "message": "Unable to send. Error in transport."
            })
        else:
            to_mx = []
            try:
                to_dns_results = await resolve_dns(to_email.split('@')[1], ["MX"])
                to_mx = sorted(to_dns_results["MX"], key=lambda x: x["priority"])
            except:
                pass
            
            numail_dns_settings = {}
            try:
                to_dns_results_txt = await resolve_dns(f"_numail.{to_email.split('@')[1]}", ["TXT"])
                for record in to_dns_results_txt["TXT"]:
                    numail_dns_settings.update(decode_txt(record["text"]))
            except:
                pass
                
            if "port" in numail_dns_settings.keys() and numail_dns_settings["port"].isdigit():
                to_port = int(numail_dns_settings["port"])
            else:
                to_port = 25

            i = 1
            loop_range_size = len(to_mx)
            for domain in to_mx:
                server_request = NuMailRequest(domain["host"], to_port)
                try:
                    await server_request.connect()
                except NuMailError as e:
                    if i == loop_range_size:
                        # writer.write(MessageLine(f"550 Unable to connect to server", message_stack).bytes())
                        # await writer.drain()
                        # print(2)
                        return jsonify({
                            "status": "error",
                            "message": "Unable to send. Error in transport."
                        })
                        break
                    else:
                        i += 1
                        continue
                init = await init_numail(server_request, local_server_settings=server_settings) # bool

                if init:
                    try:
                        chck = await server_request.send(f"CHCK RECEIVE MAIL: <{to_email}>")
                        if read_numail(chck)[0] != "250":
                            return jsonify({
                                "status": "error",
                                "message": "Unable to send. To address cannot receive."
                            })
                            raise
                        
                        # print(11)
                        from_adr = await server_request.send(f"MAIL FROM: <{from_email}>")
                        # print(from_adr)
                        # print(from_email)
                        if read_numail(from_adr)[0] != "250":
                            return jsonify({
                                "status": "error",
                                "message": "Unable to send. Invalid from address."
                            })
                            raise

                        # print(12)
                        to_adr = await server_request.send(f"RCPT TO: {to_email}")
                        if read_numail(to_adr)[0] != "250":
                            return jsonify({
                                "status": "error",
                                "message": "Unable to send. Invalid to address."
                            })
                            raise

                        # print(13)
                        msgt = await server_request.send(f"MSGT MAIL")
                        if read_numail(msgt)[0] != "250":
                            raise

                        # print(14)
                        data = await server_request.send(f"DATA")
                        if read_numail(data)[0] != "354":
                            raise

                        # print(15)
                        message_split = normalized_message.split("\r\n")
                        i = 0
                        for line in message_split:
                            if line == "":
                                i += 1
                                continue
                            send_line = line
                            if len(send_line) > 0 and send_line[0] == ".":
                                send_line = f".{send_line}"
                            
                            if i+1 < len(message_split) and message_split[i+1] == "":
                                send_line = f"{send_line}\r\n"
                                # print("TRUE")
                            await server_request.push(send_line)
                            i += 1

                        payload = await server_request.send(".")
                        if read_numail(payload)[0] != "250":
                            raise

                        # print(16)
                        for attachment in attachments:
                            # Send attachment
                            atch = await server_request.send(f"ATCH FILE: {attachment.id} {from_email.split('@')[1]}")
                            if read_numail(atch)[0] != "250":
                                raise
                        
                        # print(17)
                        # if read_confirm:
                        #     readconfirm = await server_request.send("RDCF")
                        #     if read_numail(readconfirm)[0] != "250":
                        #         raise

                        # print(17)
                        dlvr = await server_request.send(f"DLVR")
                        dlvr_parts = read_numail(dlvr)
                        # print(dlvr_parts)
                        if dlvr_parts[0] != "250":
                            raise
                        
                        # print(18)
                        await server_request.send(f"QUIT")
                        update_receiver(upload_status["message"]["messageId"], dlvr_parts[2].split()[0])
                        update_sent(upload_status["message"]["messageId"])
                        # print(19)
                    except:
                        # print(3)
                        return jsonify({
                            "status": "error",
                            "message": "Unable to send. Error in transport."
                        })
                else:
                    # print(4)
                    return jsonify({
                        "status": "error",
                        "message": "Unable to send. Error in transport."
                    })

                await server_request.close()
                break
    except Exception as e:
        # print(5)
        return jsonify({
            "status": "error",
            "message": "Unable to send. Error in transport."
        })

    return jsonify({
        "status": "success",
        "message": "Success"
    })

@app.route('/view/<id>')
async def view(id=None):
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
        read_con = False
        for box in mailboxes:
            if box["mailboxId"] == message["messageMailbox"]:
                found = True
                if box["mbReadConf"]:
                    read_con = True
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
        


        # Figure out read confirmatons. In message_parse, this file, and db
        # Considering Taking it out




        # Send Read Confirmation
        # if read_con:
        #     to_mx = []
        #     try:
        #         to_dns_results = await resolve_dns(message["messageFrom"].split('@')[1], ["MX"])
        #         to_mx = sorted(to_dns_results["MX"], key=lambda x: x["priority"])
        #     except:
        #         pass
            
        #     numail_dns_settings = {}
        #     try:
        #         to_dns_results_txt = await resolve_dns(f"_numail.{message["messageFrom"].split('@')[1]}", ["TXT"])
        #         for record in to_dns_results_txt["TXT"]:
        #             numail_dns_settings.update(decode_txt(record["text"]))
        #     except:
        #         pass
                
        #     if "port" in numail_dns_settings.keys() and numail_dns_settings["port"].isdigit():
        #         to_port = int(numail_dns_settings["port"])
        #     else:
        #         to_port = 25

        #     i = 1
        #     loop_range_size = len(to_mx)
        #     for domain in to_mx:
        #         server_request = NuMailRequest(domain["host"], to_port)
        #         try:
        #             await server_request.connect()
        #         except NuMailError as e:
        #             if i == loop_range_size:
        #                 # writer.write(MessageLine(f"550 Unable to connect to server", message_stack).bytes())
        #                 # await writer.drain()
        #                 print(2)
        #                 return jsonify({
        #                     "status": "error",
        #                     "message": "Unable to send. Error in transport."
        #                 })
        #                 break
        #             else:
        #                 i += 1
        #                 continue
        #         init = await init_numail(server_request, local_server_settings=server_settings) # bool

        #         if init:
        #             try:
        #                 chck = await server_request.send(f"CHCK RECEIVE MAIL: <{to_email}>")
        #                 if read_numail(chck)[0] != "250":
        #                     print(10)
        #                     raise
                        
        #                 print(11)
        #                 from_adr = await server_request.send(f"MAIL FROM: <{from_email}>")
        #                 print(from_adr)
        #                 print(from_email)
        #                 if read_numail(from_adr)[0] != "250":
        #                     raise

        #                 print(12)
        #                 to_adr = await server_request.send(f"RCPT TO: {to_email}")
        #                 if read_numail(to_adr)[0] != "250":
        #                     raise

        #                 print(13)
        #                 msgt = await server_request.send(f"MSGT MAIL")
        #                 if read_numail(msgt)[0] != "250":
        #                     raise

        #                 print(14)
        #                 data = await server_request.send(f"DATA")
        #                 if read_numail(data)[0] != "354":
        #                     raise

        #                 print(15)
        #                 message_split = normalized_message.split("\r\n")
        #                 for line in message_split:
        #                     send_line = line
        #                     if len(send_line) > 0 and send_line[0] == ".":
        #                         send_line = f".{send_line}"
        #                     await server_request.push(send_line)

        #                 payload = await server_request.send(".")
        #                 if read_numail(payload)[0] != "250":
        #                     raise

        #                 print(16)
        #                 for attachment in attachments:
        #                     # Send attachment
        #                     atch = await server_request.send(f"ATCH FILE: {attachment.id} {from_email.split('@')[1]}")
        #                     if read_numail(atch)[0] != "250":
        #                         raise
                        
        #                 print(17)
        #                 if read_confirm:
        #                     readconfirm = await server_request.send("RDCF")
        #                     if read_numail(readconfirm)[0] != "250":
        #                         raise

        #                 print(19)
        #                 dlvr = await server_request.send(f"DLVR")
        #                 dlvr_parts = read_numail(dlvr)
        #                 if dlvr_parts[0] != "250":
        #                     raise

        #                 update_receiver(upload_status["message"]["messageId"], dlvr_parts[2].split()[0])
        #                 update_sent(upload_status["message"]["messageId"])
        #             except:
        #                 print(3)
        #                 return jsonify({
        #                     "status": "error",
        #                     "message": "Unable to send. Error in transport."
        #                 })
        #         else:
        #             print(4)
        #             return jsonify({
        #                 "status": "error",
        #                 "message": "Unable to send. Error in transport."
        #             })

        #         await server_request.close()
        #         break
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