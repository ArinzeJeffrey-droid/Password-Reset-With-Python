import secrets
from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, DataRequired, Length
app = Flask(__name__)
app.config['SECRET_KEY'] = '0fc45789743e75a27d99a91957180b'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/encrypt"
db = SQLAlchemy(app)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15) ])
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(20))
    token = db.Column(db.String(50))

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,password=form.password.data ,token=secrets.token_hex(15))
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful','success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        print(email)
        user = User.query.filter_by(email=email).first()
        print(user)
        if user and user.password == form.password.data:
            flash("Login Successful","success")
            return redirect(url_for('success_page'))
        else:
            flash("Try Again")
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/', methods=['GET','POST'])
def success_page():
    return render_template('index.html')

@app.route('/forgot-password', methods=['GET','POST'])
def password_reset():
    if request.method == "POST":
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            print(user.token)
            return redirect(url_for('confirm_reset'))
    return render_template('password_reset.html')


@app.route('/reset-password/<int:id>', methods=['GET','POST'])
def confirm_reset(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        if request.form['token'] == user.token:
            user.password = request.form['password']
            db.session.commit()
            flash('Password Reset sucessfull, You can Now Log In', 'Success')
            return redirect(url_for('login'))
    return render_template('confirm_reset.html')





if __name__ == "__main__":
    app.run(debug=True)