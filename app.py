from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, flash, redirect, render_template, session
from models import db, connect_db, User, Note
from forms import AddNoteForm, EditNoteForm, RegisterUserForm, LoginUserForm, OnlyCsrfForm


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
    """ Check if user is authorized to view user information, if not, redirect to login 
        or their own user information page

        Otherwise, render page with user's information
    """

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


@app.post('/users/<username>/delete')
def delete_user(username):
    """Check if user is authorized to delete user account, if not, redirect to login 
        or their own user information page

        Otherwise, delete user and all of the user's notes from database,
        and redirect to /.
    """
    if "username" not in session:
        flash("You must be logged in first")
        return redirect('/login')

    if username != session['username']:
        flash("You can not delete other users")
        return redirect(f'/users/{session["username"]}')

    form = OnlyCsrfForm()

    if form.validate_on_submit():
        user = User.query.get_or_404(username)

        for note in user.notes:
            db.session.delete(note)

        db.session.delete(user)
        db.session.commit()

        session.pop("username", None)
        flash('Deleted user account')
        return redirect('/')

# Notes Routes
###############################################################


@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_note_form(username):
    """Check if user is authorized to add note, if not, redirect to login 
        or their own user information page

        Otherwise add note and redirect to user's information page
    """

    if "username" not in session:
        flash("You must be logged in first")
        return redirect('/login')

    if username != session['username']:
        flash("You can not add note for other users")
        return redirect(f'/users/{session["username"]}')

    form = AddNoteForm()

    if form.validate_on_submit():
        user = User.query.get_or_404(username)
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner=user.username)

        db.session.add(note)
        db.session.commit()

        return redirect(f'/users/{username}')

    else:
        return render_template('add-note.html', form=form)


@app.route('/notes/<int:note_id>/update', methods=['GET', 'POST'])
def update_note(note_id):
    """Check if user is authorized to update note, if not, redirect to login 
        or their own user information page

        Otherwise update note and redirect to user's information page
    """

    note = Note.query.get_or_404(note_id)

    if "username" not in session:
        flash("You must be logged in first")
        return redirect('/login')

    if note.author.username != session['username']:
        flash("You can not edit note for other users")
        return redirect(f'/users/{session["username"]}')

    form = EditNoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        flash("Note has been updated")
        return redirect(f'/users/{note.author.username}')

    else:
        return render_template('edit-note.html', form=form)


@app.post('/notes/<int:note_id>/delete')
def delete_note(note_id):
    """Check if user is authorized to delete note, if not, redirect to login 
        or their own user information page

        Otherwise delete note and redirect to user's information page
    """

    note = Note.query.get_or_404(note_id)
#make global constant for username to prevent misspelling
    # app.beforerequest to potentially reduce repetition of checking user authorization
    if "username" not in session: 
        flash("You must be logged in first")
        return redirect('/login')

    if note.author.username != session['username']:
        flash("You can not delete a note for other users")
        return redirect(f'/users/{session["username"]}')

    form = OnlyCsrfForm()

    if form.validate_on_submit():

        db.session.delete(note)
        db.session.commit()

        flash('Deleted note')
        return redirect(f'/users/{note.author.username}')
