from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.restful import Api

# Create the Flask application.
app = Flask(__name__)
app.config.from_pyfile('miridan.cfg')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Configure a database client.
app.config["MONGODB_SETTINGS"] = {"DB": "miridan",
                                  #"USERNAME": "my_user_name",
                                  #"PASSWORD": "my_secret_password",
                                  "HOST": "127.0.0.1", "PORT": 27017}

# Initialize various extensions.
db = MongoEngine(app)
api = Api(app)

import miridan.views
import miridan.users
import miridan.world