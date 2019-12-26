from flask import (Flask, current_app, flash, redirect, render_template,
                   request, send_from_directory, url_for, g, url_for, session)

from flask_security import (RoleMixin, Security,
                            SQLAlchemySessionUserDatastore, UserMixin,
                            current_user, login_required)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename

from datetime import datetime


app = Flask(__name__)
application = app

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://std_868:AlkaTraz_098@std-mysql:3306/std_868'
db = SQLAlchemy(app)
# mysql+mysqlconnector://std_[твой номер]:[твой пароль]@std-mysql:3306/std_[твой номер]

app.secret_key = "super secret key"

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users_list.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class UsersList(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(UsersList, self).__init__(*args, **kwargs)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))

class Commits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024), nullable=False)
    author = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, text, author):
        self.text=text
        self.author=author

db.create_all()


user_datastore = SQLAlchemySessionUserDatastore(db.session, UsersList, Role)
security = Security(app, user_datastore)

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/plagiat')
def plagiat():
    return render_template ('plagiat.html')

@app.route('/post', methods=['GET'])
def post():
    authors = UsersList.query.all()
    posts = Commits.query.order_by(Commits.id.desc())
    return render_template ('post.html', posts=posts, authors=authors)

@app.route('/remove/<id>', methods=['GET'])
def remove(id):
    obj = Commits.query.filter_by(id=id).one()
    db.session.delete(obj)
    db.session.commit()

    return redirect(url_for('post'))

@app.route('/edite/<id>', methods=['GET', 'POST'])
def edite(id):
    commits = Commits.query.filter_by(id=id).one()

    if request.method == 'POST':
        text = request.form['text']
        Commits.query.filter_by(id=id).update(dict(text=text))
        db.session.commit()
        return redirect(url_for('post'))
    
    return render_template('edit_post.html', commits=commits)

@app.route('/new_post', methods=['GET'])
@login_required
def new_post():
    if not current_user.is_authenticated:
        return redirect(url_for('post'))
    return render_template('form_create_post.html')

@app.route('/commit', methods=['POST'])
@login_required
def add_message():
    text = request.form['text']
    author = current_user.id
    db.session.add(Commits(text, author))
    db.session.commit()
    return redirect(url_for('post'))


@app.route('/newuser', methods=['POST'])
def new_user():
    FirstName = request.form['FirstName']
    LastName = request.form['LastName']
    email = request.form['E-mail']
    password = request.form['pass']

    email_user = UsersList.query.filter(UsersList.email == email).first()
    if email_user:
        flash('Пользователь с таким e-mail уже существует!')
        return redirect(url_for('security.login'))

    Us = user_datastore.create_user(email=email, username=FirstName, lastname=LastName, password=password)
    user_datastore.add_role_to_user(Us, "user") # зарегаешься на user сменишь
    db.session.commit()

    return redirect(url_for('security.login'))