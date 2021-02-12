from flask_mail import Message
from flask import render_template
from threading import Thread

from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_call_qr_email(name_place, users_emails):
    print(app.config['ADMINS'][0])
    send_email('Call client_place N {}'.format(name_place),
               sender=app.config['ADMINS'][0],
               recipients=users_emails,
               text_body='text body',
               html_body='<h1>HTML body</h1>')

# l1 =  ['7281015@gmail.com', '7281015@mail.ru']
# print(send_call_qr_email('123', l1))
