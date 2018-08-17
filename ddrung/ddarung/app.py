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
            return True
        else:
            return False
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            return True
        else:
            return False

### Temporary lists




# Flask and Flask-SQLAlchemy initialization here
admin.add_view(ModelView(User, db.session))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


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
            else:
                login_user(user)#, remember=form.remember_me.data)
                redirect(rule)

        # Register
        elif reg_f.validate():
            reg_name = request.form['reg_name']
            reg_email = request.form['reg_email']
            reg_pw = request.form['reg_pw']
            if reg_f.validate_email(reg_email):
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
            else:
                print("E mail is not valid")


    return login_f, reg_f
def update_userdata():
    pass



def render_with_opt(html,rule, **option):
    categories = ["All", "음식", "문화", "놀이", "산책"]
    user_destinations = ["서울 은평구", "서울 동작구"]
    user_favorates = ["인천 서구", "서울 강남구"]
    if current_user.is_authenticated:
        return render_template(html,
                               categories=categories,
                               user_favorates=user_favorates,
                               user_destinations=user_destinations,
                               **option)
    else:
        login_f, reg_f = login(rule)
        return render_template(html,
                               categories=categories,
                               login_f=login_f,
                               reg_f=reg_f,  **option)




@app.route('/', methods=['GET','POST'])
def main():
    return redirect("/index/")


@app.route('/index/', methods=['GET','POST'])
def index():
    return render_with_opt("index.html",'/index/')

@app.route('/home/', methods=['GET','POST'])
def home():
    return render_with_opt("home.html",'/home/')

@app.route('/listing/', methods=['GET','POST'])
def listing():
    return render_with_opt('listing.html', '/listing/')


@app.route('/dashboard/', methods=['GET','POST'])
@login_required
def dashboard():
    return render_with_opt('dashboard.html', '/dashboard/')


@app.route('/dashboard/myprofile/', methods=['GET','POST'])
@login_required
def myprofile():
    return render_with_opt('dashboard-myprofile.html','/dashboard/myprofile/')


@app.route('/dashboard/changepw/', methods=['GET','POST'])
@login_required
def changepw():
    return render_with_opt('dashboard-password.html', '/dashboard/changepw/')



@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/tList')
def textList():
    return render_with_opt('listing_l4.html','/tList')


if __name__ == '__main__':
    app.run()