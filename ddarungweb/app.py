from flask import Flask
from flask import render_template ,flash
from flask import request ,redirect , url_for

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_login import LoginManager , login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__)


# Config~~
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_PASSWORD_SALT'] = True
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '허은혜♡'

# Flask app binding
csrf = CSRFProtect(app)
admin = Admin(app, name='microblog', template_mode='bootstrap3')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    active = db.Column(db.Boolean())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)




# WTF From modeling
class LoginForm(FlaskForm):
    log_email = StringField('ID', validators=[DataRequired()])
    log_pw = PasswordField('PW', validators=[DataRequired()])

class ResgisterForm(FlaskForm):
    reg_name = StringField('NAME', validators=[DataRequired()])
    reg_email = StringField('ID', validators=[DataRequired()])
    reg_pw = PasswordField('PW', validators=[DataRequired()])

    # reg_pw2 = PasswordField(
    #     'Repeat Password', validators=[DataRequired(), EqualTo('reg_pw')])
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')






# Flask and Flask-SQLAlchemy initialization here


admin.add_view(ModelView(User, db.session))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# def form_action(app_func):
#     print(app_func)
#     def form_wraper():
#         login_f = LoginForm()
#         reg_f = ResgisterForm()
#
#         if request.method == "POST":
#             if login_f.validate():
#                 log_email = request.form['log_email']
#                 log_pw = request.form['log_pw']
#                 print(log_email, log_pw)
#             elif reg_f.validate():
#                 reg_name = request.form['reg_name']
#                 reg_email = request.form['reg_email']
#                 reg_pw = request.form['reg_pw']
#                 print(reg_name, reg_email, reg_pw)
#         return render_template(app_func(), login_f=login_f, reg_f=reg_f)
#     return form_wraper
#
#
#
# @app.route('/', methods=['GET','POST'])
# @form_action
# def main():
#     return "index.html"

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)



# login method
def login(rule):
    login_f = LoginForm()
    reg_f = ResgisterForm()
    if request.method == "POST":
        # Authenticated
        if current_user.is_authenticated:
            redirect(rule)

        # Login
        elif login_f.validate_on_submit():
            log_email = request.form['log_email']
            log_pw = request.form['log_pw']
            user = User.query.filter_by(email=log_email).first()
            if user is None or not user.check_password(log_pw):
                flash('Invalid username or password')
                redirect(rule)
            login_user(user)#, remember=form.remember_me.data)
            redirect(rule)

        # Register
        elif reg_f.validate():
            reg_name = request.form['reg_name']
            reg_email = request.form['reg_email']
            reg_pw = request.form['reg_pw']
            user = User()
            user.email =reg_email
            user.name = reg_name
            user.active = True
            user.set_password(reg_pw)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            login_user(user)
            redirect(rule)



    return login_f, reg_f



@app.route('/', methods=['GET','POST'])
def main():
    print(current_user.is_authenticated)
    login_f, reg_f = login('/')
    return render_template("index.html", login_f=login_f, reg_f=reg_f)


@app.route('/listing', methods=['GET','POST'])
def listing():
    login_f, reg_f = login('/listing')
    return render_template('listing.html', login_f=login_f, reg_f=reg_f)

@app.route('/dashboard/', methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/myprofile', methods=['GET','POST'])
@login_required
def myprofile():
    return render_template('dashboard-myprofile.html')

@app.route('/dashboard/changepw', methods=['GET','POST'])
@login_required
def changepw():
    return render_template('dashboard-password.html')


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/tList')
def textList():
    return render_template('textlist.html')



if __name__ == '__main__':
    app.run()