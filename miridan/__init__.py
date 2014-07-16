from flask import Flask
app = Flask(__name__)
database = {}

import miridan.views
import miridan.logic
