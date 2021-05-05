from flask import Flask, session, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import requests
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '92ac19172d34deafe37d7e8d02aedc0bc3770bcda379742647fdd9f4a81f73d85c2c8fdde4fb2f80'

database = SQLAlchemy(app)


class Users(database.Model):
    name = database.Column(database.String(255), nullable=False)
    id = database.Column(database.Integer, primary_key=True)

    vk_id = database.Column(database.String(255), unique=True, nullable=True)
    vk_access_token = database.Column(database.String(255), nullable=True)

    registered = database.Column(database.DATETIME, default=datetime.utcnow)

    def __repr__(self):
        return f'User: {self.name}\n' \
               f'ID: {self.id}\n' \
               f'VK_ID: {self.vk_id}\n' \
               f'Registered in: {self.registered}\n'


# class Posts(database.Model):
#     author = database.Column(database.String(255), nullable=False)
#     id = database.Column(database.Integer, primary_key=True)
#
#     question = database.Column(database.String(1023), nullable=False)
#     asked = database.Column(database.DATETIME, default=datetime.utcnow)
#
#     answer = database.Column(database.String(1023), nullable=True)
#     answered = database.Column(database.DATETIME, nullable=True)
#
#     def __repr__(self):
#         return f'Author: {self.author}\n' \
#                f'ID: {self.id}\n' \
#                f'Question: {self.question}\n' \
#                f'Asked in: {self.asked}\n' \
#                f'Answer: {self.answer}\n' \
#                f'Answered in: {self.answered}\n'


# @app.route("/add_question", methods=["POST", "GET"])
# def add_question():
#     if not session.get('user_id'):
#         return redirect(url_for('index'))
#
#     if request.method == "POST":
#         if len(request.form['question']) > 2:
#             user_id = session.get('user_id')
#             user = Users.query.filter_by(id=user_id).first()
#
#             new_post = Posts(author=user.name, question=request.form['question'])
#
#             try:
#                 database.session.add(new_post)
#                 database.session.commit()
#             except SQLAlchemyError as err:
#                 database.session.rollback()
#                 error = str(err.__dict__['orig'])
#
#                 print(f"ERROR adding question to database: {error}")
#
#                 flash("Question have to contains no less then 2 characters")
#         else:
#             flash("Question have to contains no less then 2 characters")
#
#     return redirect(url_for('index'))


@app.route("/")
def index():
    user_id = session.get('user_id')

    if user_id is None:
        return render_template("index_login.html")

    # posts = Posts.query.all()
    # return render_template('index_logout.html', posts=posts)

    user = Users.query.filter_by(id=user_id).first()

    return render_template('index_logout.html', name=user.name)


@app.route("/vk_login")
def vk_login():
    code = request.args.get('code')

    if not code:
        return redirect(url_for('index'))

    response = requests.get(
        "https://oauth.vk.com/access_token?client_id=7811263&client_secret=hqmY7LJ3d7Ih7pQxhOt0&redirect_uri=http://127.0.0.1:5000/vk_login&code=" + code)
    vk_access_json = json.loads(response.text)

    if "error" in vk_access_json:
        print(vk_access_json)
        return redirect(url_for('index'))
    # print(vk_access_json)

    vk_id = vk_access_json['user_id']
    access_token = vk_access_json['access_token']

    response = requests.get('https://api.vk.com/method/users.get?user_ids=' + str(
        vk_id) + '&fields=bdate&access_token=' + access_token + '&v=5.130')
    vk_user_json = json.loads(response.text)
    # print(vk_user_json)

    user = Users.query.filter_by(vk_id=vk_id).first()

    if user is None:
        name = vk_user_json['response'][0]['first_name'] + " " + vk_user_json['response'][0]['last_name']
        new_user = Users(name=name, vk_id=vk_id, vk_access_token=access_token)

        try:
            database.session.add(new_user)
            database.session.commit()
        except SQLAlchemyError as err:
            database.session.rollback()
            error = str(err.__dict__['orig'])

            print(f"ERROR adding user to database: {error}")

            return redirect(url_for('index'))

        user = Users.query.filter_by(vk_id=vk_id).first()

    session['user_id'] = user.id

    return redirect(url_for('index'))


@app.route("/logout")
def logout():
    if not session.get('user_id'):
        return redirect(url_for('index'))

    session.pop('user_id', None)

    return redirect(url_for('index'))


@app.route("/navitas_framework.html")
def navitas_framework():
    return render_template("navitas_framework.html")


@app.route("/botanic_garden_assistant.html")
def botanic_garden_assistant():
    return render_template("botanic_garden_assistant.html")


@app.route("/csharpmini.html")
def csharpmini():
    return render_template("csharpmini.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
