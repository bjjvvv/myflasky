from flask.ext.mail import Message
from ..hello import mail, app

msg = Message('通知',
    sender='bjjvvv flask@example.com',
    recipients=['bjjvvv@163.com'])
msg.body = '明天睡觉'
msg.html = '<b>明天睡觉</b>'

def send():
    with app.app_context():
        mail.send(msg)
