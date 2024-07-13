from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta

from config import *
from db.users import get_user_type, show_user_projects
from db.admin import show_users, show_projects

from auth import auth
from projects import projects


application = Flask(__name__, static_url_path='/projects', static_folder='static')
application.secret_key = SECRET_KEY

application.register_blueprint(auth)
application.register_blueprint(projects, url_prefix='/projects')


@application.before_request
def make_session_permanent():
    session.permanent = True
    application.permanent_session_lifetime = timedelta(hours=4)


@application.route('/')
@application.route('/index')
def index():
    if not 'loggedin' in session:
        return redirect(url_for('auth.login'))
    
    user_type = get_user_type(session['id'])
    if user_type == 'user':
        user_projects = show_user_projects(session['id'])
        return render_template('index_user.html', projects=user_projects)
    if user_type == 'admin':
        users = show_users()
        projects = show_projects()
        return render_template('index_admin.html', users=users, projects=projects)


if __name__ == '__main__':
    application.run('0.0.0.0')
