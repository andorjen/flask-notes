from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, flash, redirect, render_template, session
from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm, OnlyCsrfForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask-notes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


app.config['SECRET_KEY'] = 'MY_SECRET'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


db.create_all()


@app.get('/')
def root():
    """Redirect to /register"""

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user_form():
    """Render register form"""

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username,
                                 password=password,
                                 email=email,
                                 first_name=first_name,
                                 last_name=last_name)

        db.session.commit()

        session["username"] = new_user.username
        flash(f"Welcome {first_name}!")
        return redirect(f'/users/{username}')

    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user_form():
    """Render login form"""

    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            return redirect(f'/users/{username}')

        else:
            form.username.errors = ["Invalid username or password"]

    return render_template('login.html', form=form)


@app.get('/users/<username>')
def show_user_information(username):
    """Render page with user's information"""

    form = OnlyCsrfForm()

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect('/login')

    if username != session['username']:
        flash("You can not view other users' information")

        return redirect(f'/users/{session["username"]}')

    user = User.query.get_or_404(username)
    return render_template('user-info.html', user=user, form=form)


@app.post('/logout')
def logout_user():
    """Logout user and clear session; redirect to '/'"""

    form = OnlyCsrfForm()

    if form.validate_on_submit():
        session.pop("username", None)
        flash('Logged Out')
        return redirect('/')

    return redirect('/')  # is this still best return?
