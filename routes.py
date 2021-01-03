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

from db_access import \
    UserAccess, \
    AdminAccess, \
    EmployeeAccess, \
    RoleAccess, \
    CorporationAccess, \
    CompanyAccess, \
    GroupClientPlacesAccess, \
    ClientPlaceAccess, \
    ClientAccess, \
    check_role_and_return_corporation_and_transform_slug_to_id, \
    check_role_and_transform_all_slug_to_id, \
    check_role_and_return_admin_and_transform_slug_to_id, \
    check_role_and_return_company_transform_slug_to_id, \
    role_validation_object_return_transform_slug_to_id

from forms import ClientPlaceForm, \
    RegistrationForm, \
    LoginForm, \
    CompanyForm, \
    EditUserForm, \
    EditCompanyForm, \
    EditClientPlaceForm, \
    GroupClientPlacesForm, \
    ChoiceClientPlaceForm, \
    EditGroupClientPlacesForm, \
    PersonForm, \
    EmployeeForm, \
    CorporationForm, \
    AdminForm, EditCorporationForm

from app import app, db

from models import User


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


# Users registration view
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        UserAccess(username=form.username.data.strip(),
                   email=form.email.data,
                   password=form.password.data).create_user()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    flash('Something went wrong!')
    return render_template('register.html', title='Register', form=form)


# Profile editor view
@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    user = UserAccess().the_current_user()
    form = EditUserForm(user)
    if request.method == 'POST' and form.validate_on_submit():
        UserAccess(username=form.username.data.strip(),
                   about=form.about.data.strip(),
                   _obj=user).edit_model_object()
        flash('Your changes have been saved.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.about.data = user.about
    return render_template('edit_user.html', title='Edit User',
                           form=form)


# Create corporation view
@app.route('/create_corporation', methods=['GET', 'POST'])
@login_required
def create_corporation_view():
    form = CorporationForm()

    next_page = request.args.get('next')

    if request.method == 'POST':
        if form.submit_corporation.data and form.validate_on_submit():
            CorporationAccess(name=form.name_corporation.data.strip()). \
                create_corporation()
            flash('Your corporation is now live!')
            if next_page:
                return redirect(next_page)
            form.name_corporation.data = ''

        elif form.cancel_corporation.data:
            if next_page:
                return redirect(next_page)
            form.name_corporation.data = ''

    return render_template('create_corporation.html', form=form)


# Corporation editor view
@app.route('/edit_corporation<corporation_slug_to_id>',
           endpoint='edit_corporation',
           methods=['GET', 'POST'])
@login_required
@ role_validation_object_return_transform_slug_to_id(role_id=400)
def edit_corporation(corporation_slug_to_id, **kwargs):
    corporation = kwargs['corporation']
    form = EditCorporationForm(corporation.name)
    if request.method == 'POST' and form.validate_on_submit():
        CorporationAccess(name=form.name.data.strip(),
                          about=form.about.data.strip(),
                          _obj=corporation).edit_model_object()
        flash('Your changes have been saved.')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.name.data = corporation.name
        form.about.data = corporation.about
    return render_template('edit_corporation.html', title='Edit Corporation',
                           form=form)


# Create admin view
@app.route('/create_admin/<corporation_slug_to_id>',
           endpoint='create_admin_view',
           methods=['GET', 'POST'])
@login_required
@ role_validation_object_return_transform_slug_to_id(role_id=400)
def create_admin_view(corporation_slug_to_id, **kwargs):
    roles = RoleAccess(
        corporation_id=corporation_slug_to_id).roles_available_to_create_admin()

    roles_to_choose = [(i.id, i.name) for i in roles]

    form = AdminForm(roles_to_choose, corporation_slug_to_id)

    next_page = request.args.get('next')

    if request.method == 'POST':
        if form.submit_admin.data and form.validate_on_submit():
            AdminAccess(corporation_id=corporation_slug_to_id,
                        email=form.email_admin.data.strip(),
                        role_id=form.role_admin.data.strip()).create_admin()
            flash('Your admin is now live!')
            if next_page:
                return redirect(next_page)
            form.email_admin.data = ''
            form.role_admin.data = ''

        elif form.cancel_admin.data:
            if next_page:
                return redirect(next_page)
            form.email_admin.data = ''
            form.role_admin.data = ''

    return render_template('create_admin.html', form=form)


# Create relationship admin to user view
@app.route('/create_relationship_admin_to_user/<admin_pending_slug>',
           methods=['GET', 'POST'])
@login_required
def create_relationship_admin_to_user_view(admin_pending_slug):
    admin = AdminAccess(slug=admin_pending_slug). \
        create_relationship_admin_to_user()

    next_page = request.args.get('next')

    if admin:
        flash('The relationship admin to user is accepted')
    else:
        flash('Something went wrong!')

    if next_page:
        return redirect(next_page)
    return render_template('index.html')


# Create company view
@app.route('/create_company/<corporation_slug_to_id>',
           endpoint='create_company_view',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=400)
def create_company_view(corporation_slug_to_id, **kwargs):
    form = CompanyForm(corporation_slug_to_id)

    next_page = request.args.get('next')

    if request.method == 'POST':
        if form.submit_company.data and form.validate_on_submit():

            CompanyAccess(corporation_id=corporation_slug_to_id,
                          name=form.name_company.data.strip()). \
                create_company()
            flash('Your company is now live!')
            if next_page:
                return redirect(next_page)
            form.name_company.data = ''

        elif form.cancel_company.data:
            if next_page:
                return redirect(next_page)
            form.name_company.data = ''

    return render_template('create_company.html', form=form)


# Company editor view
# @app.route('/edit_company/<company_slug_to_id>', methods=['GET', 'POST'])
# @login_required
# def edit_company(company_slug_to_id, company):
#     form = EditCompanyForm(company.name)
#     if form.validate_on_submit():
#         company.name = form.name.data.strip()
#         company.about = form.about.data.strip()
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_company', slug=company.slug))
#     elif request.method == 'GET':
#         form.name.data = company.name
#         form.about.data = company.about
#     return render_template('test/old/edit_company.html',
#                            title='Edit company{}'.format(company.name),
#                            form=form)


# Create employee view
@app.route('/create_employee/<company_slug_to_id>',
           endpoint='create_employee_view',
           methods=['GET', 'POST'])
@login_required
@ role_validation_object_return_transform_slug_to_id(role_id=600)
def create_employee_view(company_slug_to_id, **kwargs):
    corporation_id = kwargs['company'].corporation_id
    roles = RoleAccess(corporation_id=corporation_id,
                       company_id=company_slug_to_id). \
        roles_available_to_create_employee()

    roles_to_choose = [(i.id, i.name) for i in roles]

    form = EmployeeForm(roles_to_choose, corporation_id)

    next_page = request.args.get('next')

    if request.method == 'POST':
        if form.submit_employee.data and form.validate_on_submit():
            EmployeeAccess(company_id=company_slug_to_id,
                           first_name=form.first_name_employee.data.strip(),
                           email=form.email_employee.data.strip(),
                           role_id=form.role_employee.data.strip(),
                           corporation_id=corporation_id). \
                create_employee()
            flash('Your employee is now live!')
            if next_page:
                return redirect(next_page)
            form.first_name_employee.data = ''
            form.email_employee.data = ''
            form.role_employee.data = ''

        elif form.cancel_employee.data:
            if next_page:
                return redirect(next_page)
            form.first_name_employee.data = ''
            form.email_employee.data = ''
            form.role_employee.data = ''

    return render_template('create_employee.html', form=form)


# Create relationship employee to user view
@app.route('/create_relationship_employee_to_user/<employee_pending_slug>',
           methods=['GET', 'POST'])
@login_required
def create_relationship_employee_to_user_view(employee_pending_slug):
    employee = EmployeeAccess(slug=employee_pending_slug). \
        create_relationship_employee_to_user()
    next_page = request.args.get('next')

    if employee:
        flash('The relationship employee to user is created')
    else:
        flash('Something went wrong!')

    if next_page:
        return redirect(next_page)

    return render_template('index.html', title='Home')


# Create group client places view
@app.route(
    '/create_group_client_places/<company_slug_to_id>',
    endpoint='create_group_client_places_view',
    methods=['GET', 'POST'])
@login_required
# @check_role_and_transform_all_slug_to_id(role_id=601)
@ role_validation_object_return_transform_slug_to_id(role_id=600)
def create_group_client_places_view(company_slug_to_id, **kwargs):
    form = GroupClientPlacesForm(company_slug_to_id)

    next_page = request.args.get('next')

    if request.method == 'POST':
        if form.submit_group_client_places.data and form.validate_on_submit():
            GroupClientPlacesAccess(
                name=form.name_group_client_places.data.strip(),
                company_id=company_slug_to_id).create_group_client_places()
            flash('Your group is now live!')
            if next_page:
                return redirect(next_page)
            form.name_group_client_places.data = ''

        elif form.cancel_group_client_places.data:
            if next_page:
                return redirect(next_page)
            form.name_group_client_places.data = ''

    return render_template('create_group_client_places.html',
                           form_group_client_places=form)


# Create client place view
@app.route(
    '/create_client_place/<company_slug_to_id>',
    endpoint='create_client_place_view',
    methods=['GET', 'POST'])
@login_required
# @check_role_and_transform_all_slug_to_id(role_id=601)
@ role_validation_object_return_transform_slug_to_id(role_id=600)
def create_client_place_view(company_slug_to_id, **kwargs):
    groups_client_places = GroupClientPlacesAccess(
        company_id=company_slug_to_id).groups_client_places_by_company_id()

    choices_group_client_places = [(i.id, i.name) for i in groups_client_places]

    choices_group_client_places.insert(0, ('', 'group not selected'))

    form = ClientPlaceForm(company_slug_to_id, choices_group_client_places)

    next_page = request.args.get('next')

    if request.method == 'POST':
        if form.submit_client_place.data and form.validate_on_submit():
            ClientPlaceAccess(company_id=company_slug_to_id,
                              name=form.name_client_place.data.strip(),
                              group_client_places_id=
                              form.group_client_places.data.strip()). \
                create_client_place()
            flash('Your client place is now live!')
            if next_page:
                return redirect(next_page)
            form.name_client_place.data = ''
            form.group_client_places.data = ''

        elif form.cancel_client_place.data:
            if next_page:
                return redirect(next_page)
            form.name_client_place.data = ''
            form.group_client_places.data = ''

    return render_template('create_client_place.html',
                           form_client_place=form)


# Create by yourself relationship to client lace
@app.route('/_yourself_to_client_place/<client_place_slug>',
           methods=['GET', 'POST'])
def create_by_yourself_relationship_to_client_place(client_place_slug):
    result = EmployeeAccess(client_place_slug=client_place_slug). \
        create_relationship_client_place_to_employee()

    flash(result[1])

    return render_template('index.html', title='Home')


# Create by yourself relationship to group client places
@app.route('/_yourself_to_group_client_places/<group_client_places_slug>',
           methods=['GET', 'POST'])
def create_by_yourself_relationship_to_group_client_places(
        group_client_places_slug):
    result = EmployeeAccess(
        group_client_places_slug=group_client_places_slug). \
        create_relationship_group_client_places_to_employee()

    flash(result[1])

    return render_template('index.html', title='Home')


# Profile view
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


@app.route('/corporation/<corporation_slug_to_id>',
           endpoint='corporation',
           methods=['GET', 'POST'])
@check_role_and_return_corporation_and_transform_slug_to_id(
    first_role_id=500, second_role_id=800)
@login_required
def corporation(corporation_slug_to_id, corporation, first_role):
    companies = None
    if first_role:
        companies = CompanyAccess(
            corporation_id=corporation_slug_to_id).companies_by_corporation_id()
    admins = AdminAccess(
        corporation_id=corporation_slug_to_id).admins_by_corporation_id()

    return render_template('corporation.html', companies=companies,
                           admins=admins, corporation=corporation)


@app.route('/company/<company_slug_to_id>',
           endpoint='company',
           methods=['GET', 'POST'])
@check_role_and_return_company_transform_slug_to_id(role_id=999)
@login_required
def company(company_slug_to_id, company):
    groups_client_places = GroupClientPlacesAccess(
        company_id=company_slug_to_id).groups_client_places_by_company_id()

    client_places = ClientPlaceAccess(
        company_id=company_slug_to_id).client_places_by_company_id()

    employees = EmployeeAccess(
        company_id=company_slug_to_id).employees_by_company_id()

    return render_template('company.html', company=company,
                           groups_client_places=groups_client_places,
                           client_places=client_places, employees=employees)


@app.route('/admin/<admin_slug_to_id>',
           endpoint='admin', methods=['GET', 'POST'])
@check_role_and_return_admin_and_transform_slug_to_id(others=True)
@login_required
def admin(admin_slug_to_id, admin):
    corporation = CorporationAccess(id=admin.corporation_id).object_by_id()

    return render_template('admin.html', admin_id=admin_slug_to_id,
                           admin=admin, corporation=corporation)


@app.route('/employee/<employee_slug_to_id>', methods=['GET', 'POST'])
@login_required
def employee(employee_slug_to_id):
    employee = EmployeeAccess(slug=employee_slug_to_id).object_by_slug()

    employee_id = employee.id

    company = CompanyAccess(id=employee.company_id).object_by_id()

    groups_client_places = employee.groups_client_places

    client_places = employee.client_places

    return render_template('employee.html', employee_id=employee_id,
                           employee=employee, company=company,
                           groups_client_places=groups_client_places,
                           client_places=client_places)


@app.route('/group_client_places/<group_client_places_slug_to_id>',
           methods=['GET', 'POST'])
@login_required
def group_client_places(group_client_places_slug_to_id):
    group_client_places = GroupClientPlacesAccess(
        slug=group_client_places_slug_to_id).object_by_slug()

    group_client_places_id = group_client_places.id

    client_places = group_client_places.client_places

    employees = group_client_places.employees

    return render_template('group_client_places.html',
                           client_places=client_places, employees=employees,
                           group_client_places=group_client_places,
                           group_client_places_id=group_client_places_id)


@app.route('/client_place/<client_place_slug_to_id>', methods=['GET', 'POST'])
@login_required
def client_place(client_place_slug_to_id):
    client_place = ClientPlaceAccess(
        slug=client_place_slug_to_id).object_by_slug()

    client_place_id = client_place.id

    group_client_places = client_place.group_client_places

    employees = client_place.employees

    return render_template('client_place.html',
                           client_place=client_place, employees=employees,
                           client_place_id=client_place_id,
                           group_client_places=group_client_places)



@app.route('/test', methods=['GET', 'POST'])
# @login_required
def test():
    print(' --- TEST --- ')
    print(current_user.__setattr__('admins'))
    return render_template('index.html', title='Home')