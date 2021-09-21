from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, flash, redirect, render_template, request, session
from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm, LogoutUserForm


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
def load_register_form(): #need to be more descriptive; register_user?
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
                    first_name=first_name, last_name=last_name) #move instance creation into classmethod register

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username
        flash(f"Welcome {first_name}!")
        return redirect(f'/users/{username}')

    else:
        # keep the validated data and show error msgs
        return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def show_login_form():#need to be more descriptive;
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

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect('/login')

    if username != session['username']:
        flash("You can not view other users' information")
        return redirect('/login') #instead of login, redirect to own users page

    user = User.query.get_or_404(username)
    return render_template('user-info.html', user=user, form=LogoutUserForm()) #maybe make form situation more consistent with other routes


@app.post('/logout')
def logout_user():
    """Logout user and clear session; redirect to '/'"""

    # could be more descriptive; include form_validate?
    session.pop("username", None)  
    flash('Logged Out')
    return redirect('/')
