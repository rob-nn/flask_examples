from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.script import Shell
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.mail import Message
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.bootstrap import Bootstrap
import flask
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') 

from flask.ext.mail import Mail
mail = Mail(app)


def send_email(to, subject, template, **kwargs):
    msg = Message('[Flasky] ' + subject, sender='Flasky admin <flask@example.com>', recipients=['aguiarlima.roberto@gmail.com'])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.body = render_template(template + '.html', **kwargs)
    mail.send(msg)

@app.route('/')
def hello_world():
    return flask.render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return flask.render_template('user.html', name = name)

@app.route('/secret')
def secret():
    return 'Not authorized', 400

@app.route('/browser')
def get_browser():
    user_agent = flask.request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>'% user_agent

@app.route('/make_response')
def make_res():
    response = flask.make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/redirect_')
def redirect_():
    return flask.redirect('http://www.google.com')

@app.route('/abort')
def abort():
    flask.abort(404)
    return 'Never arrives here.'

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/myform', methods=['GET', 'POST'])
def myform():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return flask.redirect(url_for('myform'))
    return render_template('myform.html', form = form, name=session.get('name'))

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r' % self.username

@app.route('/mydb', methods=['GET', 'POST'])
def mydb():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            send_email('aguiarlima.roberto@icloud.com', 'New user', 'mail/template', user=user)
        else:
            session['known'] = True
        session['name'] = user.username
        form.name.data = ''
        return redirect(url_for('mydb'))
    return render_template('mydb.html', form = form, name = session.get('name'), known=session.get('known', False))

def make_shell_context():
    return dict(app = app, db=db, User=user, Role=Role)

if __name__ == '__main__':
    manager = Manager(app)
    manager.add_command('shell', Shell(make_context = make_shell_context))
    migrate = Migrate(app, db)
    manager.add_command('db', MigrateCommand)
    manager.run()
