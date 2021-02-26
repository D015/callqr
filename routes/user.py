# -*- coding: utf-8 -*-

from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import (current_user,
                         login_user,
                         logout_user,
                         login_required)

from werkzeug.urls import url_parse

from app import app

from db_access import (UserAccess,
                       AdminAccess,
                       EmployeeAccess,
                       ClientAccess)

from forms import (LoginForm,
                   RegistrationForm,
                   EditUserForm)

from utils.utils_routes import remove_object


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAccess(username=form.username_or_email.data,
                          email=form.username_or_email.data). \
            user_by_username_or_email()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = UserAccess(username=form.username.data.strip(),
                          email=form.email.data,
                          password=form.password.data).create_user()
        if user:
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        else:
            flash('Something went wrong!')
    return render_template('register.html', title='Register', form=form)


@app.route('/profile')
@login_required
def profile():
    the_user = UserAccess().the_current_user()
    admins = AdminAccess().admins_of_current_user()
    employees = EmployeeAccess().employees_of_current_user()
    clients = ClientAccess().clients_of_current_user()
    admins_pending = AdminAccess().admins_pending_of_current_user()
    employees_pending = EmployeeAccess().employees_pending_of_current_user()

    return render_template('profile.html', user=the_user, admins=admins,
                           employees=employees, clients=clients,
                           admins_pending=admins_pending,
                           employees_pending=employees_pending)


@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    user = UserAccess().the_current_user()
    form = EditUserForm(user)
    if request.method == 'POST' and form.validate_on_submit():
        UserAccess(_obj=user).edit_model_object(
            username=form.username.data.strip(),
            about=form.about.data.strip())
        flash('Your changes have been saved.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.about.data = user.about
    return render_template('edit_user.html', title='Edit User',
                           form=form)


@app.route('/remove_user', methods=['GET', 'POST'])
@login_required
def remove_user():
    obj = UserAccess().the_current_user_of_model()
    return remove_object(obj=obj)
