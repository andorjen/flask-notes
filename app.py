from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, flash, redirect, render_template, request, session
from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm


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
def load_register_form():
    """Render register form"""

    form = RegisterUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username, password=password)
        user = User(username=username, password=new_user.password, email=email,
                    first_name=first_name, last_name=last_name)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username
        flash(f"Welcome {first_name}!")
        return redirect("/secret")

    else:
        # keep the validated data and show error msgs
        return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def show_login_form():
    """Render login form"""

    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            return redirect('/secret')

        else:
            form.username.errors = ["Invalid username or password"]

    return render_template('login.html', form=form)


@app.get('/secret')
def show_secret():
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect('/login')

    return "YOU MADE IT!!!"
