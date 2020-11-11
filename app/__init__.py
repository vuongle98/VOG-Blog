from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CsrfProtect


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)
login = LoginManager(app)
csrf = CsrfProtect(app)
login.login_view = 'login'

from app import routes, models, errors