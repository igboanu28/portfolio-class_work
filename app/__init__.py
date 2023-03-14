from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_migrate import Migrate
from flask_login import LoginManager



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:Uche_123@localhost/portfolio'
app.config['SECRET_KEY'] = 'you-will-never-guess'
db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'



from app import routes,models