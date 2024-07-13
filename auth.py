from flask import Blueprint
from flask import render_template, request, redirect, url_for, session, jsonify
from db.auth import show_user, show_user_with_email, create_user


auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    msg = ''
    if request.method == 'POST':
        email_address = request.form['email_address']
        password = request.form['password']
        account = show_user(email_address, password)
        if not account is None:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['email_address']
            return redirect(url_for('index'))
        else:
            msg = r'Неверный логин/пароль!'
    return render_template('login.html', msg=msg)

 
@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))

 
@auth.route('/register', methods =['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html', msg='')
    password = request.form['password']
    email = request.form['email']
    account = show_user_with_email(email)
    if account:
        return render_template('register.html', msg='Аккаунт с таким email-адресом уже существует!')
    
    create_user(email, request.form['fullName'], password)
    return render_template('login.html', msg='Вы успешно зарегистрированы!')
