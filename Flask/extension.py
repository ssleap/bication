from flask import Flask
from flask import render_template ,flash
from flask import request ,redirect , url_for
from flask_sqlalchemy import SQLAlchemy


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_login import LoginManager , login_user, current_user
from path_finder import playFinder
import station

from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__)

# Config~~
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Ddrung.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_PASSWORD_SALT'] = True
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'login.html'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '허은혜♡'
# Flask app binding
csrf = CSRFProtect(app)
admin = Admin(app, template_mode='bootstrap3', base_template='admin/index.html')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from dbconfig import User, Role, Bookmark, Nonmember, Rent



from flask_admin import BaseView, expose


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
        user = User.query.filter_by(username=username).first()
        if user is not None:
            return True
        else:
            return False
    def validate_email(self, email):
        user = User.query.filter_by(email=email).first()
        if user is None:
            return True
        else:
            return False

class SearchForm(FlaskForm):
    src = StringField('NAME', validators=[DataRequired()])
    dest = StringField('NAME', validators=[DataRequired()])
    src_val = ""
    dest_val = ""

# Flask and Flask-SQLAlchemy initialization here
admin.add_view(ModelView(User, db.session, url = '/admin/user'))
admin.add_view(ModelView(Role, db.session, url = '/admin/role'))
admin.add_view(ModelView(Bookmark, db.session))
admin.add_view(ModelView(Nonmember, db.session))
admin.add_view(ModelView(Rent, db.session))



class AnalyticsView1(BaseView):
    @expose("/")
    def analytics1(self):
        return self.render("admin/analysis.html")
admin.add_view(AnalyticsView1(name='Analytics1', endpoint='analytics1'))


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
                print("E-mail is not valid")


    return login_f, reg_f




def get_category(name="Takeout"):

    if name == "Takeout":
        categories = { "cat_name": "테이크아웃",
                   "pop_tags": "#다이어트포기 #칼로리보충 #2+1할인",
                   "items" : [{ "img" : "/static/listimg/takeout/1.jpg",
                              "mark_cnt" : 45,
                              "title" : "디어브레드",
                              "text" : "빵집,치아바타,치즈,냉장고를부탁해,이원일셰프,착한가격,건강빵,테이크아웃,간단한요기,런치",
                              "star_cnt": 2,
                              "rev_cnt": 7,
                              "addr": "서울특별시 성북구 안암동5가 101-66",
                              "call": "070-7661-4129",
                              "lon": 37.587691,
                              "lat": 127.029014
                             },
                            {"img": "/static/listimg/takeout/2.jpg",
                             "mark_cnt": 16,
                             "title": "영철버거",
                             "text": "버거,치즈,모던한분위기,오래된밥집,아늑한카페,혼자맛집,간식,힐링푸드,런치",
                             "star_cnt": 2,
                             "rev_cnt": 15,
                             "addr": "서울특별시 성북구 안암동5가 86-132",
                             "call": "02-922-1668",
                             "lon": 37.585717,
                             "lat": 127.030605
                             },
                            {"img": "/static/listimg/takeout/3.jpg",
                             "mark_cnt": 12,
                             "title": "프로마치",
                             "text": "샌드위치,샐러드,브런치,평화로운,가성비좋은,여유로운,홈메이드,다이어트맛집,테이크아웃,아침메뉴",
                             "star_cnt": 2,
                             "rev_cnt": 82,
                             "addr": "서울특별시 성북구 안암동5가 103-149",
                             "call": "050-4110-1371",
                             "lon": 37.585589,
                             "lat": 127.030184
                             },
                            {"img": "/static/listimg/takeout/4.jpg",
                             "mark_cnt": 5,
                             "title": "호만두",
                             "text": "졸업식,고급스럽고 격식있는,조용히 이야기하는,가족외식,기념일,저녁식사,점심식사",
                             "star_cnt": 1,
                             "rev_cnt": 16,
                             "addr": "서울특별시 성북구 안암동5가 104-34",
                             "call": "02-923-1555",
                             "lon": 37.583911,
                             "lat": 127.029734
                             },
                            {"img": "/static/listimg/takeout/5.jpg",
                             "mark_cnt": 4,
                             "title": "핸썸베이글",
                             "text": "베이글,연어베이글,크림치즈베이글,줄서서먹는,넓은공간,테이크아웃",
                             "star_cnt": 3,
                             "rev_cnt": 48,
                             "addr": "서울특별시 성북구 안암동5가 101-81",
                             "call": "02-6449-1505",
                             "lon": 37.587420,
                             "lat":127.028751
                             },
                            {"img": "/static/listimg/takeout/6.jpg",
                             "mark_cnt": 2,
                             "title": "본도시락",
                             "text": "불고기,도시락전문,도시락,고급스러운,여자들끼리,다양한메뉴",
                             "star_cnt": 2,
                             "rev_cnt": 23,
                             "addr": "서울특별시 성북구 안암동5가 134-70",
                             "call": "02-960-0209",
                             "lon": 37.582437,
                             "lat": 127.028591
                             }
                            ]
                 }

    else:
        categories = None
    return categories

def get_category_list():
    pass


def render_with_opt(html,rule, **option):
    categories = ["All", "테이크아웃", "문화", "놀이", "산책"]
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