from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, flash, redirect, render_template, request
from models import db, connect_db, User
from forms import RegisterUserForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///database_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

debug = DebugToolbarExtension(app)
app.config['SECRET_KEY'] = 'MY_SECRET'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


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

        new_user = User(username=username, password=password, email=email,
                        first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        db.session.commit()

        flash(f"Welcome {first_name}!")
        return redirect("/secret")

    else:
        # keep the validated data and show error msgs
        return render_template("new-user-form.html", form=form)
