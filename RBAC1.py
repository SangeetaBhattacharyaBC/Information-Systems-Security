pip install flask flask-login flask-sqlalchemy flask-security email-validator

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_security import Security, SQLAlchemyUserDatastore, RoleMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from flask_security import roles_required

@app.route('/admin')
@roles_required('admin')
def admin_page():
    return "Welcome Admin!"

@app.route('/editor')
@roles_required('editor')
def editor_page():
    return "Welcome Editor!"

@app.route('/viewer')
@roles_required('viewer')
def viewer_page():
    return "Welcome Viewer!"
    
@app.before_first_request
def create_user():
    db.create_all()
    if not user_datastore.find_role('admin'):
        user_datastore.create_role(name='admin')
        user_datastore.create_role(name='editor')
        user_datastore.create_role(name='viewer')
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', password='adminpass', roles=['admin'])
        user_datastore.create_user(email='editor@example.com', password='editorpass', roles=['editor'])
        user_datastore.create_user(email='viewer@example.com', password='viewerpass', roles=['viewer'])
    db.session.commit()

