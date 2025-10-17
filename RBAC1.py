from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, roles_required, hash_password
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
app.config['SECURITY_PASSWORD_SALT'] = 'somesalt'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

db = SQLAlchemy(app)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.route('/admin')
@roles_required('admin')
def admin_page():
    return "Welcome, Admin!"

@app.route('/editor')
@roles_required('editor')
def editor_page():
    return "Welcome, Editor!"

@app.route('/viewer')
@roles_required('viewer')
def viewer_page():
    return "Welcome, Viewer!"

def create_users():
    db.create_all()
    for role_name in ['admin', 'editor', 'viewer']:
        if not user_datastore.find_role(role_name):
            user_datastore.create_role(name=role_name)
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', password=hash_password('adminpass'), roles=['admin'])
    if not user_datastore.get_user('editor@example.com'):
        user_datastore.create_user(email='editor@example.com', password=hash_password('editorpass'), roles=['editor'])
    if not user_datastore.get_user('viewer@example.com'):
        user_datastore.create_user(email='viewer@example.com', password=hash_password('viewerpass'), roles=['viewer'])
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        create_users()
    app.run(host='0.0.0.0', port=5000, debug=True)
