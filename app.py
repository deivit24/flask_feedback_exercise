from flask import Flask, request, render_template, redirect, flash, session
import requests
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, DeleteForm
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError
 
app = Flask(__name__)
 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_exercise'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'isaacneterothe12thchairman'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)
 
connect_db(app)
db.create_all()

@app.route('/')
def home_page():
    if "user_id" in session:
        id = session['user_id']
        main_user = User.query.get_or_404(id)
        users = User.query.all()
        return render_template('index.html', main_user = main_user, users=users)
    users = User.query.all() 
    return render_template('index.html')


@app.route('/register', methods=["GET", "POST"])
def register_user():
    if "user_id" in session:
        id = session['user_id']
        user = User.query.get_or_404(id)
        flash("You are already registered in", "info")
        return redirect(f'/user/{user.username}')
    form = UserForm()
    
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = User.register(first_name, last_name, username, email, password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken. Please pick another")
            return render_template('register.html', form = form)
        session["user_id"] = user.id

        # on successful login, redirect to secret page
        flash(f"Welcome {user.username}! You have successfully Created Your Account", "success")
        return redirect(f"/user/{user.username}")

    else:
        return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if "user_id" in session:
        id = session['user_id']
        user = User.query.get_or_404(id)
        flash("You are already logged in", "info")
        return redirect(f'/user/{user.username}')
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f" Welcome back {user.username}", "primary")
            session['user_id'] = user.id
            return redirect(f'/user/{user.username}')
        else: 
            form.password.errors = ['Invalid username/password']
    return render_template('login.html', form=form)


@app.route('/user/<username>')
def secret_page(username):
    if "user_id" not in session:
        flash("Please Login First", "danger")
        return redirect('/')
    id = session['user_id']
    main_user = User.query.get_or_404(id)
    user = User.query.filter_by(username=username).first_or_404()
    form = DeleteForm()
    return render_template('user.html', user = user, main_user=main_user, form = form)


@app.route("/user/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user and redirect to login."""

    if "user_id" not in session:
        flash("Please Login First", "danger")
        return redirect('/')
    id = session['user_id']
    main_user = User.query.get_or_404(id)
    user = User.query.filter_by(username=username).first_or_404()
    if main_user.username != user.username:
        flash("You are not authorized", "danger")
        return redirect('/')
    db.session.delete(user)
    db.session.commit()
    session.pop("user_id")
    flash("Successfully Deleted", 'success')
    return redirect("/login")


@app.route("/user/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """Show add-feedback form and process it."""

    if "user_id" not in session:
        flash("You are not authorized", "danger")
        return redirect('/')
    id = session['user_id']
    main_user = User.query.get_or_404(id)
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/user/{feedback.username}")

    else:
        return render_template("new_feedback.html", form=form, main_user=main_user)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "user_id" not in session:
        flash("You are not authorized", "danger")
        return redirect('/')
    id = session['user_id']
    main_user = User.query.get_or_404(id)
    if main_user.username != feedback.username:
        flash("You are not authorized", "danger")
        return redirect('/')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/user/{feedback.username}")

    return render_template("/edit_feedback.html", form=form, feedback=feedback, main_user=main_user)

@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("user_id")
    flash("Goodbye!", "info")
    return redirect("/")

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "user_id" not in session:
        flash("You are not authorized", "danger")
        return redirect('/')
    id = session['user_id']
    main_user = User.query.get_or_404(id)
    if main_user.username != feedback.username:
        flash("You are not authorized", "danger")
        return redirect('/')

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/user/{feedback.username}")

@app.errorhandler(404)
def page_not_found(e):
    if 'user_id' in session:
        id = session['user_id']
        main_user = User.query.get_or_404(id)
    
        return render_template('404.html', main_user=main_user), 404
    else: 
        main_user = "/"
        return render_template('404.html', main_user=main_user), 404