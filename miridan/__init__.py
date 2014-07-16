from flask import Flask
app = Flask(__name__)
database = {"banana": {}}

import miridan.views
import miridan.logic
