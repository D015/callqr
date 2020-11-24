# -*- coding: utf-8 -*-
from datetime import datetime

from flask import render_template, \
    flash, \
    redirect, \
    url_for, \
    request

from flask_login import current_user, \
    login_user, \
    logout_user, login_required

from werkzeug.urls import url_parse

from db_access.client_place_access import create_client_place
from db_access.company_access import create_company
from db_access.employee_access import create_employee, \
    create_relationship_employee_to_user, \
    is_relationship_employee_to_client_place
from db_access.group_client_places_access import create_group_client_places, \
    groups_client_places_by_company_id
from db_access.user_access import create_user
from db_access.corporation_access import create_corporation
from db_access.role_access import roles_available_to_create_admin, \
    roles_available_to_create_employee
from db_access.admin_access import create_admin, \
    create_relationship_admin_to_user
from db_access.decorator_access import \
    check_role_and_transform_corporation_slug_to_id, \
    check_role_and_transform_all_slug_to_id

from forms import ClientPlaceForm, \
    RegistrationForm, \
    LoginForm, \
    CompanyForm, \
    EditProfileForm, \
    EditCompanyForm, \
    EditClientPlaceForm, \
    GroupClientPlacesForm, \
    ChoiceClientPlaceForm, \
    EditGroupClientPlacesForm, \
    PersonForm, \
    EmployeeForm, \
    CorporationForm, \
    AdminForm

from sqlalchemy import or_

from app import app, db

from models import User, Employee, ClientPlace
#     GroupClientPlaces, \
#     Client


from email_my import send_call_qr_email


# Last time visits for user
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    return render_template('index.html', title='Home')


# Users registration view
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        create_user(username=form.username.data.strip(),
                    email=form.email.data,
                    password=form.password.data)

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
        flash('Something went wrong!')
    return render_template('register.html', title='Register', form=form)


# Login view function logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# Logout view function
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Create corporation view
@app.route('/_create_corporation', methods=['GET', 'POST'])
@login_required
def create_corporation_view():
    form = CorporationForm()
    if request.method == 'POST':
        if form.submit_corporation.data:
            if form.validate_on_submit():
                create_corporation(
                    name_corporation=form.name_corporation.data.strip())
                flash('Your corporation is now live!')

    form.name_corporation.data = ''

    return render_template('_create_corporation.html', form=form)


# Create admin view
@app.route('/_create_admin/<corporation_slug_or_id>',
           endpoint='create_admin_view',
           methods=['GET', 'POST'])
@login_required
@check_role_and_transform_corporation_slug_to_id(role_id=401)
def create_admin_view(corporation_slug_or_id):
    roles = roles_available_to_create_admin(
        corporation_id=corporation_slug_or_id)

    roles_to_choose = [(i.id, i.name) for i in roles]

    form = AdminForm(roles_to_choose, corporation_slug_or_id)

    if request.method == 'POST':
        if form.submit_admin.data:
            if form.validate_on_submit():
                create_admin(
                    corporation_id=corporation_slug_or_id,
                    email=form.email_admin.data.strip(),
                    role_id=form.role_admin.data.strip())
                flash('Your admin is now live!')

    form.email_admin.data = ''
    form.role_admin.data = ''

    return render_template('_create_admin.html', form=form,
                           corporation_slug=corporation_slug_or_id)


# Create relationship admin to user view
@app.route('/_create_relationship_admin_to_user/<admin_slug>',
           methods=['GET', 'POST'])
@login_required
def create_relationship_admin_to_user_view(admin_slug):
    admin = create_relationship_admin_to_user(admin_slug)

    if admin:
        flash('The relationship admin to user is created')
    else:
        flash('Something went wrong!')

    return render_template('index.html', title='Home')


# User profile view
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    companys = Company.query.filter_by(creator_user_id=user.id).order_by(
        Company.timestamp.desc())

    form = CompanyForm()
    if request.method == 'POST':
        if form.submit.data:
            if form.validate_on_submit():
                company = Company(name=form.name.data.strip(),
                                  creator=current_user,
                                  about=form.about.data.strip())
                db.session.add(company)
                db.session.commit()
                flash('Your company is now live!')

    form.name.data = ''
    form.about.data = ''

    return render_template('user.html', user=user, companys=companys, form=form)


# Create company view
@app.route('/_create_company/<corporation_slug_or_id>',
           endpoint='create_company_view',
           methods=['GET', 'POST'])
@login_required
@check_role_and_transform_corporation_slug_to_id(role_id=401)
def create_company_view(corporation_slug_or_id):
    form = CompanyForm(corporation_slug_or_id)

    if request.method == 'POST':
        if form.submit_company.data:
            if form.validate_on_submit():
                create_company(
                    corporation_id=corporation_slug_or_id,
                    name_company=form.name_company.data.strip())
                flash('Your company is now live!')

    form.name_company.data = ''

    return render_template('_create_company.html', form=form,
                           corporation_slug=corporation_slug_or_id)


# Create employee view
@app.route('/_create_employee/<corporation_slug_or_id>/<company_slug_or_id>',
           endpoint='create_employee_view',
           methods=['GET', 'POST'])
@login_required
@check_role_and_transform_all_slug_to_id(role_id=999)
def create_employee_view(corporation_slug_or_id, company_slug_or_id):
    roles = roles_available_to_create_employee(
        corporation_id=corporation_slug_or_id, company_id=company_slug_or_id)

    roles_to_choose = [(i.id, i.name) for i in roles]

    form = EmployeeForm(roles_to_choose, corporation_slug_or_id)

    if request.method == 'POST':
        if form.submit_employee.data:
            if form.validate_on_submit():
                create_employee(
                    company_id=company_slug_or_id,
                    first_name=form.first_name_employee.data.strip(),
                    email=form.email_employee.data.strip(),
                    role_id=form.role_employee.data.strip(),
                    corporation_id=corporation_slug_or_id)
                flash('Your employee is now live!')

    form.first_name_employee.data = ''
    form.email_employee.data = ''
    form.role_employee.data = ''

    return render_template('_create_employee.html', form=form,
                           corporation_slug_or_id=corporation_slug_or_id,
                           company_slug_or_id=company_slug_or_id)


# Create relationship employee to user view
@app.route('/_create_relationship_employee_to_user/<employee_slug>',
           methods=['GET', 'POST'])
@login_required
def create_relationship_employee_to_user_view(employee_slug):
    employee = create_relationship_employee_to_user(employee_slug)

    if employee:
        flash('The relationship employee to user is created')
    else:
        flash('Something went wrong!')

    return render_template('index.html', title='Home')


# Create group client places view
@app.route(
    '/_create_group_client_places/<corporation_slug_or_id>/<company_slug_or_id>',
    endpoint='create_group_client_places_view',
    methods=['GET', 'POST'])
@login_required
@check_role_and_transform_all_slug_to_id(role_id=601)
def create_group_client_places_view(corporation_slug_or_id, company_slug_or_id):
    form = GroupClientPlacesForm(company_slug_or_id)

    if request.method == 'POST':
        if form.submit_group_client_places.data:
            if form.validate_on_submit():
                create_group_client_places(
                    company_slug_or_id,
                    form.name_group_client_places.data.strip())
                flash('Your group is now live!')

    form.name_group_client_places.data = ''

    return render_template('_create_group_client_places.html',
                           form_group_client_places=form,
                           corporation_slug_or_id=corporation_slug_or_id,
                           company_slug_or_id=company_slug_or_id)

# Create client place view
@app.route(
    '/_create_client_place/<corporation_slug_or_id>/<company_slug_or_id>',
    endpoint='create_client_place_view',
    methods=['GET', 'POST'])
@login_required
@check_role_and_transform_all_slug_to_id(role_id=601)
def create_client_place_view(corporation_slug_or_id, company_slug_or_id):

    groups_client_places = groups_client_places_by_company_id(
        company_slug_or_id)

    choices_group_client_places = [(i.id, i.name) for i in groups_client_places]
    choices_group_client_places.insert(0, (None, 'group not selected'))

    form = ClientPlaceForm(company_slug_or_id, choices_group_client_places)

    if request.method == 'POST':
        if form.submit_client_place.data:
            if form.validate_on_submit():
                create_client_place(
                    company_slug_or_id,
                    form.name_client_place.data.strip(),
                    form.group_client_places.data.strip()) \
                    if form.group_client_places.data else \
                    create_client_place(
                        company_slug_or_id,
                        form.name_client_place.data.strip())

                flash('Your client place is now live!')

    form.name_client_place.data = ''
    form.group_client_places.data = ''


    return render_template('_create_client_place.html',
                           form_client_place=form,
                           corporation_slug_or_id=corporation_slug_or_id,
                           company_slug_or_id=company_slug_or_id)


# _Old__routes______________________________________
# Company profile view
@app.route('/company/<slug>', methods=['GET', 'POST'])
@login_required
def company(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()

    client_places = ClientPlace.query. \
        filter(ClientPlace.company_id == company.id). \
        order_by(ClientPlace.name.asc())

    groups_client_places = GroupClientPlaces.query. \
        filter(GroupClientPlaces.company_id == company.id). \
        order_by(GroupClientPlaces.name.asc())

    choices_group_client_places = [(i.id, i.name) for i in groups_client_places]
    choices_group_client_places.insert(0, ('', 'group not selected'))

    form_group_client_places = GroupClientPlacesForm(company.id)
    form_client_place = ClientPlaceForm(company.id, choices_group_client_places)

    if form_group_client_places.submit_group_client_places.data \
            and form_group_client_places.validate_on_submit():
        group_client_places = GroupClientPlaces(
            name=form_group_client_places.name_group_client_places.data.strip(),
            company_group_client_places=company)
        db.session.add(group_client_places)
        db.session.commit()
        flash('Your group_client_places is now live!')
        return redirect(url_for('company', slug=slug))

    if form_client_place.submit_client_place.data and \
            form_client_place.validate_on_submit():
        client_place = ClientPlace(
            name=form_client_place.name_client_place.data.strip(),
            company_client_place=company,
            group_client_places_id=form_client_place.group_client_places.data) \
            if form_client_place.group_client_places.data else \
            ClientPlace(
                name=form_client_place.name_client_place.data.strip(),
                company_client_place=company)

        db.session.add(client_place)
        db.session.commit()
        flash('Your client_place is now live!')
        return redirect(url_for('company', slug=slug))

    return render_template('company.html',
                           company=company,
                           client_places=client_places,
                           groups_client_places=groups_client_places,
                           form_client_place=form_client_place,
                           form_group_client_places=form_group_client_places)


# Profile editor view
@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data.strip()
        current_user.about = form.about.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_user'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about.data = current_user.about
    return render_template('edit_user.html', title='Edit User',
                           form=form)


# Company editor view
@app.route('/edit_company/<slug>', methods=['GET', 'POST'])
@login_required
def edit_company(slug):
    company = Company.query.filter(Company.slug == slug).first_or_404()
    form = EditCompanyForm(company.name)
    if form.validate_on_submit():
        company.name = form.name.data.strip()
        company.about = form.about.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_company', slug=company.slug))
    elif request.method == 'GET':
        form.name.data = company.name
        form.about.data = company.about
    return render_template('edit_company.html',
                           title='Edit company{}'.format(company.name),
                           form=form)


# Client place editor view
@app.route('/edit_client_place/<slug>', methods=['GET', 'POST'])
@login_required
def edit_client_place(slug):
    client_place = ClientPlace.query.filter_by(slug=slug). \
        first_or_404()

    groups_client_places = GroupClientPlaces.query. \
        filter(GroupClientPlaces.company_id == client_place.company_id). \
        order_by(GroupClientPlaces.name.asc())

    choices_group_client_places = [(i.id, i.name) for i in groups_client_places]
    choices_group_client_places.insert(0, ('', 'group not selected'))

    form = EditClientPlaceForm(client_place.company_id,
                               client_place.name,
                               choices_group_client_places,
                               group_client_places=client_place.group_client_places_id)
    if form.validate_on_submit():
        client_place.name = form.name.data.strip()
        client_place.group_client_places_id = form.group_client_places.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_client_place', slug=client_place.slug))
    elif request.method == 'GET':
        form.name.data = client_place.name
    return render_template('edit_client_place.html',
                           title='Edit client place {}'.format(
                               client_place.name),
                           form=form)


# Call QR view
@app.route('/callqr/<slug>')
# @login_required
def call_qr(slug):
    client_place = ClientPlace.query.filter_by(
        slug_link=slug).first_or_404()
    users_emails = []
    for user in client_place.users:
        users_emails.append(user.email)
    send_call_qr_email(client_place.name, users_emails)
    flash('Call client_place N {}'.format(client_place.name))
    return redirect(url_for('index', title='Home'))


# My corporations view
# @app.route('/my_corporations/<user_slug>', methods=['GET', 'POST'])
# @login_required
# def my_corporations(user_slug):
#      form = CorporationForm()
#     if request.method == 'POST':
#         if form.submit.data:
#             if form.validate_on_submit():
#                 company = create_corporation(
#                     name_corporation=
#                     about_corporation=
#                     about_admin=
#                     email_admin=
#                     phone_admin=
#                 )
# #                 flash('Your company is now live!')
# #
# #     form.name.data = ''
# #     form.about.data = ''
# #
# #     return render_template('my_companies.html', user=user, companys=companys,
# #                            form=form)


# My Companies view
@app.route('/my_companies/<username>', methods=['GET', 'POST'])
@login_required
def my_companies(username):
    user = User.query.filter_by(username=username).first_or_404()

    companys = Company.query.filter_by(creator_user_id=user.id). \
        order_by(Company.timestamp.desc())

    form = CompanyForm()
    if request.method == 'POST':
        if form.submit.data:
            if form.validate_on_submit():
                company = Company(name=form.name.data.strip(),
                                  creator=current_user,
                                  about=form.about.data.strip())
                db.session.add(company)
                db.session.commit()
                flash('Your company is now live!')

    form.name.data = ''
    form.about.data = ''

    return render_template('my_companies.html', user=user, companys=companys,
                           form=form)


# Group Client Places profile view
@app.route('/group_client_places/<slug>', methods=['GET', 'POST'])
@login_required
def group_client_places(slug):
    group_client_places = GroupClientPlaces.query.filter_by(slug=slug). \
        first_or_404()

    client_places_in_group_client_places = ClientPlace.query. \
        filter(ClientPlace.group_client_places_id == group_client_places.id,
               ClientPlace.company_id == group_client_places.company_id). \
        order_by(ClientPlace.name.asc())

    def client_places_not_in_group_client_places():
        client_places_not_in_group_client_places = ClientPlace.query. \
            filter(ClientPlace.company_id == group_client_places.company_id). \
            filter(
            or_(ClientPlace.group_client_places_id != group_client_places.id,
                ClientPlace.group_client_places_id == None)). \
            order_by(ClientPlace.name.asc())
        return client_places_not_in_group_client_places

    form_choice_client_places = ChoiceClientPlaceForm()
    form_choice_client_places.choices.choices = \
        [(c.id, c.name) for c in client_places_not_in_group_client_places()]

    if request.method == 'POST' \
            and form_choice_client_places.submit_choice_client_places.data \
            and form_choice_client_places.validate_on_submit():

        for client_place in client_places_not_in_group_client_places():

            if client_place.id in \
                    form_choice_client_places.choices.data:
                client_place.group_client_places_id = group_client_places.id

                db.session.add(client_place)
                db.session.commit()

        return redirect(url_for('group_client_places',
                                slug=group_client_places.slug))

    return render_template('group_client_places.html',
                           group_client_places=group_client_places,
                           client_places=client_places_in_group_client_places,
                           form_choice_client_places=form_choice_client_places)


# Group Client places editor view
@app.route('/edit_group_client_places/<slug>', methods=['GET', 'POST'])
@login_required
def edit_group_client_places(slug):
    group_client_places = GroupClientPlaces.query.filter_by(slug=slug). \
        first_or_404()

    form = EditGroupClientPlacesForm(group_client_places.company_id,
                                     group_client_places.name,
                                     group_client_places.about)
    if form.validate_on_submit():
        group_client_places.name = form.name.data.strip()
        group_client_places.about = form.about.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_group_client_places',
                                slug=group_client_places.slug))
    elif request.method == 'GET':
        form.name.data = group_client_places.name
        form.about.data = group_client_places.about
    return render_template('edit_group_client_places.html',
                           title='Edit group client places {}'.format(
                               group_client_places.name),
                           form=form)


# Profile view
@app.route('/profile')
@login_required
def profile():
    user = current_user

    person = Person.query.filter_by(user_id=current_user.id).first()

    if person:
        first_name = person.first_name
        last_name = person.last_name
        about = person.about
    else:
        first_name = 'No first name'
        last_name = 'No last name'
        about = 'No about'

    employee = Employee.query.filter_by(person=user.person).first()

    if employee:
        about_employee = employee.about
        email_employee = employee.email
        phone_number_telegram_employee = employee.phone_number_telegram
    else:
        about_employee = 'No about'
        email_employee = 'No email'
        phone_number_telegram_employee = 'No phone number telegram'

    client = Client.query.filter_by(person=user.person).first()

    if client:
        about_client = client.about

    else:
        about_client = 'No about'

    return render_template('profile.html', user=user, first_name=first_name,
                           last_name=last_name, about=about,
                           about_employee=about_employee,
                           email_employee=email_employee,
                           phone_number_telegram_employee= \
                               phone_number_telegram_employee,
                           about_client=about_client)


# Person editor view
@app.route('/edit_person', methods=['GET', 'POST'])
@login_required
def edit_person():
    user = current_user

    person = Person.query.filter_by(user_id=user.id).first()

    if person:
        first_name = person.first_name
        last_name = person.last_name
        about = person.about
    else:
        first_name = '1'
        last_name = '1'
        about = '1'

    form = PersonForm(first_name, last_name, about)
    if form.validate_on_submit() and person:
        person.first_name = form.first_name.data.strip()
        person.last_name = form.last_name.data.strip()
        person.about = form.about.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_person'))
    elif form.validate_on_submit() and person is None:
        person = Person(first_name=form.first_name.data.strip(),
                        last_name=form.last_name.data.strip(),
                        about=form.about.data.strip(),
                        user_id=user.id)
        db.session.add(person)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_person'))
    elif request.method == 'GET':
        form.first_name.data = first_name
        form.last_name.data = last_name
        form.about.data = about
    return render_template('edit_person.html', user=user, first_name=first_name,
                           last_name=last_name, about=about, form=form)


# Employee editor view
@app.route('/edit_employee', methods=['GET', 'POST'])
@login_required
def edit_employee():
    employee = Employee.query.filter_by(person=current_user.person).first()

    if employee:
        about = employee.about
        email = employee.email
        phone_number_telegram = employee.phone_number_telegram
    else:
        about = '1'
        email = '1'
        phone_number_telegram = '1'

    form = EmployeeForm(about, email, phone_number_telegram)
    if form.validate_on_submit() and employee:
        employee.about = form.about.data.strip()
        employee.email = form.email.data.strip()
        employee.phone_number_telegram = form.phone_number_telegram.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_employee'))
    elif form.validate_on_submit() and employee is None:
        employee = Employee(about=form.about.data.strip(),
                            email=form.email.data.strip(),
                            phone_number_telegram= \
                                form.phone_number_telegram.data.strip(),
                            person=current_user.person)
        db.session.add(employee)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_employee'))
    elif request.method == 'GET':
        form.about.data = about
        form.email.data = email
        form.phone_number_telegram.data = phone_number_telegram
    return render_template('edit_employee.html', user=current_user, about=about,
                           email=email,
                           phone_number_telegram=phone_number_telegram,
                           form=form)


@app.route('/test', methods=['GET', 'POST'])
# @login_required
def test():
    # user_id = current_user.id
    # corporation, admin = create_corporation(user_id, 'name_corporation',
    #                                         'about_corporation',
    #                                         'about_admin', '15@admin.com',
    #                                         '15', user_id)
    # print(corporation)
    # print("___")
    # print(admin)
    # print(corporation.admins.all())
    # _________________________________
    # admin = create_admin(user_id, 'about_admin', '12@admin.com', '12', '4', '33')
    # print(admin)
    # print(admin.corporation.name)
    # admin = Employee.query.filter_by(
    #     slug='552ebd2ec8cf4a59aa0c5d7a152c3e97').first_or_404()
    # print(admin)
    # __________________________________
    # user_admin_corporation = current_user.admins.filter_by(
    #     corporation_id=37).first()
    # print(user_admin_corporation)
    # _________________________________
    # user_id = user_by_id(1)
    # not_user_id = user_by_id(2)
    # user_slag = user_by_slug('3a6b4f3b493b4f12a214709622888268')
    # not_user_slag = user_by_slug('a6b4f3b493b4f12a214709622888268')
    #
    # print(user_id)
    # print(not_user_id)
    # print(user_slag)
    # print(not_user_slag)
    # ________________________________
    # user_id = user_by_slug_or_404('a6b4f3b493b4f12a214709622888268')
    # not_user_id = user_by_id(2)
    # user_slag = user_by_slug('3a6b4f3b493b4f12a214709622888268')
    # not_user_slag = user_by_slug('a6b4f3b493b4f12a214709622888268')

    # print(user_id)
    # print(not_user_id)
    # print(user_slag)
    # print(not_user_slag)
    # ____________________________________
    # corporation_id = corporation_by_slug('ef65ef6686d04a25a357dd8065122c8b').id
    # print(corporation_id)
    # _________________________________________________
    # role_id_creator_admin = (current_user.admins.filter_by(
    #     corporation_id=corporation_by_slug(
    #         'ef65ef6686d04a25a357dd8065122c8b').id).first()).role_id
    # print(role_id_creator_admin)
    # __________________________________________________
    # roles = Role.query.filter(Role.code == 10).order_by(Role.id.asc()).all()
    #
    # print(roles)
    # _________________________________________
    # next_page = request.args.get('next')
    # print(request.args)
    # # return redirect(next_page)
    # _____________________________________
    # print(roles_available_to_create_admin(current_user,'ef65ef6686d04a25a357dd8065122c8b'))
    # ___________________________________________
    # @check_role_and_relationship_to_corporation()
    # def func_test(corporation_id, c, b):
    #     result = corporation_id + c + b
    #     return result
    # a = func_test(18, 101, 3)
    # print(a)
    # _______________________________________
    # admin = Admin.query.filter(
    #     Admin.slug == 'bac41c4ac8194b23b736ea5d7533a91e',
    #     Admin.archived == False).first()
    # print(admin)
    # _____________________________________________
    # employee = Employee.query.filter(
    # Employee.slug == '37f917f33e9949c299a4071f95ca1f82', Employee.archived == False).first()
    # print(employee.corporation_id)
    # ________________________________
    # employee = current_user.employees.filter(
    #     Employee.corporation_id == 18,
    #     Employee.active == True, Employee.archived == False,
    #     Employee.role_id < 701).first()
    # print(employee)
    # _________________________________________________
    # employee3 = Employee.query.filter_by(id=3).first()
    # print(employee3, employee3.client_places.all())
    #
    # employee2 = Employee.query.filter_by(id=2).first()
    # print(employee2, employee2.client_places.all())
    #
    # client_place1 = ClientPlace.query.filter_by(id=1).first()
    # print(client_place1, client_place1.employees.all())
    #
    # client_place2 = ClientPlace.query.filter_by(id=2).first()
    # print(client_place2, client_place2.employees.all())
    #
    # client_place3 = ClientPlace.query.filter_by(id=3).first()
    # print(client_place3, client_place3.employees.all())
    #
    # client_place4 = ClientPlace.query.filter_by(id=4).first()
    # print(client_place4, client_place4.employees.all())
    # ___________________________________________________
    # rce = is_relationship_employee_to_client_place(3, 1)
    # print(rce)
    # ___________________________________________________

    return render_template('index.html', title='Home')
