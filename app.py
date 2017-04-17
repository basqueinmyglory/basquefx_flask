from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime as dt
import os
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

#Create App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://wfmnyfwdodwjvj:49cb5d80d43011be38a957cf42bc0340bb454552a0ad1274a988d99fc31f4170@ec2-54-225-119-223.compute-1.amazonaws.com:5432/d60uuffk20up1i'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['DEBUG'] = True


#Create database connection object
db = SQLAlchemy(app)

#Define Models for secutity
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


#Define Models for Content
class journal(db.Model):
    __tablename__ = 'journal'
    id = db.Column('id', db.Integer, primary_key=True)
    entry_date = db.Column('entry_date', db.Date)
    strong_cur = db.Column('strong_cur', db.String)
    weak_cur = db.Column('weak_cur', db.String)
    strong_reason = db.Column('strong_reason', db.String)
    weak_reason = db.Column('weak_reason', db.String)
    consider_reason = db.Column('consider_reason', db.String)

    def __init__(self, id, entry_date, strong_cur, weak_cur, strong_reason, weak_reason, consider_reason):
        self.id = id
        self.entry_date = entry_date
        self.strong_cur = strong_cur
        self.weak_cur = weak_cur
        self.strong_reason = strong_reason
        self.weak_reason = weak_reason
        self.consider_reason = consider_reason

class blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column('id', db.Integer, primary_key=True)
    entry_date = db.Column('entry_date', db.Date)
    author = db.Column('author', db.String)
    title = db.Column('title', db.String)
    content = db.Column('content', db.String)


    def __init__(self, id, entry_date, title, content):
        self.id = id
        self.entry_date = entry_date
        self.title = title
        self.content = content


@app.route('/')
def home():
    daily = journal.query.order_by('entry_date').limit(1)
    return render_template("home.html", daily = daily)
    #entry_date = dt.date.today()

@app.route('/login/')
@login_required
def login():
    return render_template("adminbase.html")

@app.route('/blog/')
def blog():
    return render_template("blog.html")

@app.route('/entry/', methods=['GET', 'POST'])
@login_required
def entry():
    return render_template('entry.html')

@app.route('/daily/', methods=['GET', 'POST'])
@login_required
def daily():
    return render_template('daily.html')



if __name__=="__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
