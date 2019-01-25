from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.login_message = 'Для того, чтобы просматривать и проходить тесты, необходима регистрация.'
lm.init_app(app=app)
lm.login_view = 'login'