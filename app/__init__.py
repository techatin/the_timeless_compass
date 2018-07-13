from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'admin.login'

from app.admin.views import admin_blueprint
from app.mainpage.views import main_blueprint

app.register_blueprint(admin_blueprint)
app.register_blueprint(main_blueprint)
