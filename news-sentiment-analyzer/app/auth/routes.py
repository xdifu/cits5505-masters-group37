# filepath: /home/god/web-group-project/cits5505-masters-group37/news-sentiment-analyzer/app/auth/routes.py
# Defines authentication routes (login, logout, register).

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

# Create Blueprint for authentication routes
bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Redirect if already logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger') # Use category for styling
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # Redirect to the page the user was trying to access, or index
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required # Ensure user is logged in to log out
def logout():
    """Handles user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login')) # Redirect to login after registration
    return render_template('auth/register.html', title='Register', form=form)