from miridan import app


@app.route('/')
def index():
    return 'Hello World!'


@app.route('/user')
def show_user():
    """
    Return profile of the currently logged-in user.
    """
    return 'User'  # TODO: fill this in once sessions are working.
