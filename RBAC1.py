from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
     UserMixin, RoleMixin, roles_required
import uuid

# --- Flask setup ---
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
app.config['SECURITY_PASSWORD_SALT'] = 'somesalt'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# --- Database setup ---
db = SQLAlchemy(app)

# Association table
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

# --- Models ---
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

# --- Setup Flask-Security ---
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# --- Create users and roles (only first time) ---
@app.before_request
def create_users():
    db.create_all()
    if not user_datastore.find_role("admin"):
        user_datastore.create_role(name="admin", description="Administrator")
        user_datastore.create_role(name="editor", description="Content Editor")
        user_datastore.create_role(name="viewer", description="Viewer")
    if not user_datastore.find_user(email="admin@example.com"):
        user_datastore.create_user(email="admin@example.com", password="adminpass", roles=["admin"])
        user_datastore.create_user(email="editor@example.com", password="editorpass", roles=["editor"])
        user_datastore.create_user(email="viewer@example.com", password="viewerpass", roles=["viewer"])
    db.session.commit()

# --- Role-based routes ---
@app.route("/")
def index():
    return """
    <h2>RBAC Demo</h2>
    <ul>
        <li><a href='/login'>Login</a></li>
        <li><a href='/admin'>Admin Page</a></li>
        <li><a href='/editor'>Editor Page</a></li>
        <li><a href='/viewer'>Viewer Page</a></li>
    </ul>
    """

@app.route("/admin")
@roles_required("admin")
def admin_page():
    return "✅ Welcome, Admin!"

@app.route("/editor")
@roles_required("editor")
def editor_page():
    return "✏️ Welcome, Editor!"

@app.route("/viewer")
@roles_required("viewer")
def viewer_page():
    return "👀 Welcome, Viewer!"

# --- Run server ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
