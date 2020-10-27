from flask import Blueprint, render_template,request,redirect,url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .model_user import User
from . import database_user as db
from flask_login import login_user
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    pseudo = request.form.get('pseudo')
    password = request.form.get('password')

    user = User.query.filter_by(pseudo=pseudo).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Veuillez vérifier vos informations et réessayez.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    login_user(user)
    return redirect(url_for('main.chat'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    pseudo = request.form.get('pseudo')
    password = request.form.get('password')

    required = [email, pseudo, password]

    for i in range(len(required)):
        if required[i] == "" :
            flash('Missing information')
            return redirect(url_for('auth.signup'))

    user = User.query.filter_by(pseudo=pseudo).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Pseudo already exists. Go to login page ')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, pseudo = pseudo, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('main.chat'))


@auth.route('/logout')
def logout():
    return redirect(url_for('main.login'))
