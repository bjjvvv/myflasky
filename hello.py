from datetime import datetime
from flask import Flask, render_template, session, url_for, redirect, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.script import Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Mail, Message
import os.path


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'bian jia jun'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# mail configuration
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] =\
    os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] =\
    os.environ.get('MAIL_PASSWORD')
app.config['FLASK_MAIL_SUBJECT_PREFIX'] = '[FLASKY]'
app.config['FLASK_MAIL_SENDER'] = '514739571@qq.com'
app.config['FLASK_ADMIN']='bjjvvv@163.com'


manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

manager.add_command('db', MigrateCommand)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASK_MAIL_SUBJECT_PREFIX'] + subject,
                             sender=app.config['FLASK_MAIL_SENDER'],
                             recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db. Model):
    __tablename__ = 'users'
    id = db.Column(db. Integer, primary_key=True)
    username = db.Column(db. String(64), unique=True, index=True)

    role_id = db.Column(db.Integer,
                        db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self. username


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell",
                    Shell(make_context=make_shell_context))


class NameForm(Form):
    name = StringField("Whit is your name?", validators=[Required()])
    submit = SubmitField("Submit")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASK_ADMIN']:
                send_email(
                    app.config['FLASK_ADMIN'], 'New User',
                    'mail/new_user', user=user
                )
                print(user.username)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form, name=session.get('name'),
                           known=session.get('known', False))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


if __name__ == '__main__':
    manager.run()
