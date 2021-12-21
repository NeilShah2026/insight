#!/usr/bin/python

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps
import time

from password import _mysql_password
from sqlhelpers import *
from forms import BuyForm, RegisterForm, SendMoneyForm

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = _mysql_password
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def is_loggin_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def log_in_user(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "email", "username", "password")

    if request.method == 'POST' and form.validate():
        username = form.username.data
        name = form.name.data
        email = form.email.data

        if isnewuser(username):
            password = sha256_crypt.encrypt(str(form.password.data))
            users.insert(name, email, username, password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)

@app.route('/transaction', methods=['GET', 'POST'])
@is_loggin_in
def transaction():
    form = SendMoneyForm(request.form)
    balance = get_balance(session.get('username'))

    if request.method == 'POST':
        try:
            send_money(session.get('username'), form.username.data, form.amount.data)
            flash("Money Send!", 'success')
        except Exception as e:
            flash("Error: %s" %e, 'danger')
        
        return redirect(url_for('transaction'))

    return render_template('transaction.html', form=form, balance=balance)

@app.route('/buy', methods=['GET', 'POST'])
@is_loggin_in
def buy():
    form = BuyForm(request.form)
    balance = get_balance(session.get('username'))

    if request.method == 'POST':
        try:
            send_money("BANK", session.get('username'), form.amount.data)
            flash("Money Send!", 'success')
        except Exception as e:
            flash("Error: %s" %e, 'danger')
        
        return redirect(url_for('dashboard'))

    return render_template('buy.html', form=form, balance=balance)

@app.route('/dashboard')
@is_loggin_in
def dashboard():
    blockchain = get_blockchain().chain
    balance = get_balance(session.get('username'))
    ct = time.strftime("%H:%M:%S")
    return render_template('dashboard.html', session=session, ct=ct, blockchain=blockchain, page='dashboard', balance=balance)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        candidate = request.form['password']

        users = Table("users", "name", "email", "username", "password")
        user = users.getone("username", username)
        accpass = user.get('password')

        if accpass is None:
            flash('Username does not exist', 'danger')
            return redirect(url_for('login'))
        else:
            if sha256_crypt.verify(candidate, accpass):
                log_in_user(username)
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Password is incorrect', 'danger')
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/mine/post/<user>')
def mine_update(user):
    try:
        send_money("BANK", user, 1)
    except:
        pass
    return "Success"
    
@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.secret_key = "2374sfjk10r3ifjwksdhf"
    app.run(host="0.0.0.0", port=5000, debug=True)


