from flask import Flask, render_template,request,redirect,url_for, session
from flask_sqlalchemy import SQLAlchemy #to represent the user model and interface with our database
from flask_login import LoginManager 
import jinja2
from jinja2 import Environment
import bcrypt
import os


# init SQLAlchemy so we can use it later in our models
database_user = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'NJqf76'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_user.sqlite'

    app.jinja_env.add_extension('jinja2.ext.do')
    
    database_user.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .model_user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .authorization import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

