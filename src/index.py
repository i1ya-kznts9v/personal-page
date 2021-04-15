from flask import Flask
from flask import render_template

app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route("/")
def index():
    return render_template("index.html")


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
    app.run()