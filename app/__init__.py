from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, instance_relative_config=True)
app.config["SECRET_KEY"] = "fvym74x2o4gn7v15"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///sleevy.db'  
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  
db = SQLAlchemy(app)
 

from app import models
from app import views


app.config.from_object('config')    