from flask import Flask, flash, request, redirect, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from flask_images import Images, resized_img_src

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)



# Login Manager
login = LoginManager(app)
login.login_view = 'index'

images = Images(app)



from app import routes, models, forms