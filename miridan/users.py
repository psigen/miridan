
from flask.ext.login import login_required, login_user, logout_user
from flask.ext.login import current_user

from miridan import app
from miridan import db
from miridan import login_manager

from flask import flash, redirect, url_for, request, jsonify


class User(db.Document):
    """
    Model for user profile data.
    """
    userid = db.StringField(required=True, primary_key=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_administrator(self):
        return True

    def get_id(self):
        return self.userid


@login_manager.user_loader
def load_user(userid):
    return User.objects(userid=userid).first()


#TODO: hilariously insecure!
@app.route("/user/login/<userid>")
def login(userid=None):
    user = User.objects(userid=userid).first()
    if user is None:
        user = User(userid=userid)
        user.save()

    login_user(user)
    flash("Logged in successfully as '{0}'.".format(userid))
    return redirect(request.args.get("next") or url_for("index"))


@app.route("/user/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/user/profile')
@login_required
def show_user():
    """
    Return profile of the currently logged-in user.
    """
    return jsonify({"userid": current_user.get_id()})
