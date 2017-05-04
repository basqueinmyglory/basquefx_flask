from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime as dt
import os
from sqlalchemy import desc
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
class Journal(db.Model):
    __tablename__ = 'journal'
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column('entry_date', db.Date)
    strong_cur = db.Column('strong_cur', db.String)
    weak_cur = db.Column('weak_cur', db.String)
    strong_reason = db.Column('strong_reason', db.String)
    weak_reason = db.Column('weak_reason', db.String)
    consider_reason = db.Column('consider_reason', db.String)

    def __init__(self, entry_date, strong_cur, weak_cur, strong_reason, weak_reason, consider_reason):
        self.entry_date = entry_date
        self.strong_cur = strong_cur
        self.weak_cur = weak_cur
        self.strong_reason = strong_reason
        self.weak_reason = weak_reason
        self.consider_reason = consider_reason

class Blog(db.Model):
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column('entry_date', db.Date)
    author = db.Column('author', db.String)
    subject = db.Column('subject', db.String)
    title = db.Column('title', db.String)
    content = db.Column('content', db.String)


    def __init__(self, entry_date, author, subject, title, content):
        self.entry_date = entry_date
        self.author = author
        self.subject = subject
        self.title = title
        self.content = content

class Bias(db.Model):
    __tablename__ = 'bias'
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column('entry_date', db.Date)
    usd = db.Column('usd', db.String)
    gbp = db.Column('gbp', db.String)
    jpy = db.Column('jpy', db.String)
    eur = db.Column('eur', db.String)
    cad = db.Column('cad', db.String)
    chf = db.Column('chf', db.String)
    aud = db.Column('aud', db.String)
    nzd = db.Column('nzd', db.String)


    def __init__(self, entry_date, usd, gbp, jpy, eur, cad, chf, aud, nzd):
        self.entry_date = entry_date
        self.usd = usd
        self.gbp = gbp
        self.jpy = jpy
        self.eur = eur
        self.cad = cad
        self.chf = chf
        self.aud = aud
        self.nzd = nzd

#Rounting of pages
@app.route('/')
def home():
    dailyget = Journal.query.order_by(desc('entry_date')).limit(1)
    biasget = Bias.query.order_by(desc('entry_date')).limit(1)
    return render_template("home.html", dailyget = dailyget, biasget = biasget)

@app.route('/login/')
@login_required
def login():
    return render_template("loggedin.html")

@app.route('/blog/')
def blog():
    blogget = Blog.query.order_by(desc('entry_date'))
    return render_template("blog.html", blogget = blogget)

@app.route('/tools/')
def tools():
    return render_template('forexcal.html')

@app.route('/entry/')
@login_required
def entry():
    return render_template('entry.html')

@app.route('/entry_add/', methods=['POST'])
@login_required
def entry_add():
    add_entry = Blog(request.form['date'], request.form['name'], request.form['subject'], request.form['title'], request.form['content'])
    db.session.add(add_entry)
    db.session.commit()
    return render_template('loggedin.html')

@app.route('/daily/')
@login_required
def daily():
    return render_template('daily.html')

@app.route('/daily_add/', methods=['POST'])
@login_required
def daily_add():
    add_daily = Journal(request.form['date'], request.form['strong_cur'], request.form['weak_cur'], request.form['strong_rea'], request.form['weak_rea'], request.form['consider_reason'])
    db.session.add(add_daily)
    db.session.commit()
    return render_template('loggedin.html')

@app.route('/bias/')
@login_required
def bias():
    return render_template('bias.html')

@app.route('/bias_add/', methods=['POST'])
@login_required
def bias_add():
    add_bias = Bias(request.form['date'], request.form['usd'], request.form['gbp'], request.form['eur'], request.form['jpy'], request.form['cad'], request.form['chf'], request.form['aud'], request.form['nzd'])
    db.session.add(add_bias)
    db.session.commit()
    return render_template('loggedin.html')


if __name__=="__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
