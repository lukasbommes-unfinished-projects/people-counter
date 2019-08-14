from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_required, login_user, logout_user, current_user
from server import db
from server.auth import bp
from server.auth.forms import LoginForm, RegistrationForm
from server.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('Sucessfully logged in')
        return redirect(next_page)
    return render_template('auth/login.html', login_form=login_form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Sucessfully logged out')
    return redirect(url_for('auth.login'))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(username=register_form.username.data, email=register_form.email.data)
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sucessfully registered')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', register_form=register_form)
