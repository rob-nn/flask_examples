from flask import Flask
from flask.ext.script import Manager
import flask
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'Hard to guess string'
manager = Manager(app)

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

@app.route('/redirect')
def redirect():
    return flask.redirect('http://www.google.com')

@app.route('/abort')
def abort():
    flask.abort(404)
    return 'Never arrives here.'


if __name__ == '__main__':
    manager.run()
