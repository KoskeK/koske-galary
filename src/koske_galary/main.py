from flask import Flask, render_template #pyright: ignore
from flask_sqlalchemy import SQLAlchemy #pyright: ignore
from koske_galary.config import Config

config = Config()
app = Flask(__name__)
for key in config.config:
    app.config[key] = config.config[key]
db = SQLAlchemy(app)