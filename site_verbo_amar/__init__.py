from flask import Flask,render_template,url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


lista_projetos = ["Projeto1", "Projeto2"]

app.config["SECRET_KEY"] = "123456"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

database = SQLAlchemy(app)

from site_verbo_amar import routes