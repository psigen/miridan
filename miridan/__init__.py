from flask import Flask
from flask.ext.mongoengine import MongoEngine

# Create the Flask application.
app = Flask(__name__)
app.config.from_pyfile('miridan.cfg')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Configure a database client.
app.config["MONGODB_SETTINGS"] = {"DB": "miridan",
                                  #"USERNAME": "my_user_name",
                                  #"PASSWORD": "my_secret_password",
                                  "HOST": "127.0.0.1", "PORT": 27017}
db = MongoEngine(app)


import miridan.views
import miridan.users
import miridan.world