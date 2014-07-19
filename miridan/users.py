
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from miridan import app
from miridan import db


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])

    @staticmethod
    def current():
        return current_user

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def create_default_users():
    user_datastore.create_user(email='psigen@gmail.com', password='moocow')
    user_datastore.create_user(email='jkl@example.com', password='jkljkl')
    user_datastore.find_or_create_role(name='admin',
                                       description='Administrator')
    user_datastore.add_role_to_user('psigen@gmail.com', 'admin')


@app.route('/user/profile')
@login_required
def show_user():
    """
    Return profile of the currently logged-in user.
    """
    return current_user.to_json()
