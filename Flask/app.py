from flask import render_template ,flash
from flask import request ,redirect , url_for
from flask_security import login_required
from flask_login import  logout_user
from extension import (render_with_opt, get_category, app,
                       SearchForm)

from dbconfig import *



@app.route('/', methods=['GET','POST'])
def main():
    return redirect("/index/")


@app.route('/index/', methods=['GET','POST'])
def index():
    locsearch = SearchForm()
    if request.method == "POST":
        src = request.form["src"]
        dest = request.form["dest"]
        result_cat = "테이크아웃"
        category = get_category("Takeout")
        lists = category["items"]
        locsearch = SearchForm()
        print(src, dest)
        return render_with_opt('listing.html', '/listing/',
                               result_cat=result_cat,
                               lists=lists,
                               locsearch=locsearch,
                               src=src, dest=dest)

    return render_with_opt("index.html",'/index/',locsearch=locsearch)

@app.route('/home/', methods=['GET','POST'])
def home():
    category_list = [get_category("Takeout")]
    locsearch = SearchForm()
    return render_with_opt("home.html",'/home/',category_list=category_list,locsearch=locsearch)

@app.route('/listing/', methods=['GET','POST'])
def listing():
    src =""
    dest=""
    result_cat = "테이크아웃"
    category = get_category("Takeout")
    lists = category["items"]
    locsearch = SearchForm()
    return render_with_opt('listing.html', '/listing/',
                           result_cat=result_cat,
                           lists=lists,
                           locsearch=locsearch,
                           src=src, dest=dest)



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