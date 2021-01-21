# -*- coding: utf-8 -*-
from datetime import datetime

from aiogram.utils.deep_linking import get_start_link, decode_payload
from flask import render_template, \
    flash, \
    redirect, \
    url_for, \
    request

from flask_login import current_user, \
    login_user, \
    logout_user, login_required
from flask_sqlalchemy import Model
from sqlalchemy import or_, inspect
from sqlalchemy.engine import Connectable

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
    role_validation_object_return_transform_slug_to_id, BaseAccess, \
    BaseCompanyAccess
from email_my import send_call_qr_email

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
    EmployeeForm, \
    CorporationForm, \
    AdminForm, EditCorporationForm, EditAdminForm, EditEmployeeForm, \
    RemoveObjectForm

from app import app, db

from models import User, Employee, GroupClientPlaces, ClientPlace

# Last time visits for user
from utils_routes import remove_object, groups_client_places_for_employee, \
    client_places_for_employee, employee_or_current_employee, \
    another_objs_for_obj


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
        # todo change query by UserAccess
        user = User.query.filter(or_(User.username == form.username.data,
                                     User.email == form.username.data)).first()
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


# User editor view
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


# User deleter view
@app.route('/remove_user', methods=['GET', 'POST'])
@login_required
def remove_user():
    obj = UserAccess().the_current_user_of_model()

    return remove_object(obj=obj)


# Create admin view
@app.route('/create_admin/<corporation_slug_to_id>',
           endpoint='create_admin_view',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=400)
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


# TODO check compliance conditions
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


@app.route('/admin/<admin_slug_to_id>',
           endpoint='admin',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(myself=True, id_diff=-100,
                                                    another_id_limit=400)
def admin(admin_slug_to_id, **kwargs):
    admin = kwargs['admin']

    corporation = CorporationAccess(id=admin.corporation_id).object_by_id()

    return render_template('admin.html', admin_id=admin_slug_to_id,
                           admin=admin, corporation=corporation)


# todo cancel
# Admin editor view
@app.route('/edit_admin/<admin_slug_to_id>',
           endpoint='edit_admin',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(myself=True, id_diff=-100,
                                                    another_id_limit=600)
def edit_admin(admin_slug_to_id, **kwargs):
    admin = kwargs['admin']

    roles_to_choose = [(admin.role_id, admin.role.name)]

    if kwargs.get('valid_myself') is not True:
        roles = RoleAccess(
            corporation_id=admin.corporation_id).roles_available_to_create_admin()

        roles_to_choose = [(i.id, i.name) for i in roles]

    form = EditAdminForm(roles_to_choose, admin, role=admin.role_id)
    if request.method == 'POST':
        if form.submit.data and form.validate_on_submit():
            AdminAccess(_obj=admin).edit_model_object(
                about=form.about.data.strip(),
                phone=None if form.phone.data.strip() == '' \
                    else form.phone.data.strip(),
                email=form.email.data.strip(),
                role_id=form.role.data.strip())

            flash('Your changes have been saved.')
            return redirect(url_for('admin', admin_slug_to_id=admin.slug))
    elif request.method == 'GET':
        form.about.data = admin.about
        form.phone.data = admin.phone
        form.email.data = admin.email
    return render_template('edit_admin.html',
                           title='Edit admin {}'.format(admin.id),
                           form=form, valid_myself=kwargs.get('valid_myself'))


# Admin deleter view
@app.route('/remove_admin/<admin_slug_to_id>',
           endpoint='remove_admin',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(myself=False, id_diff=-100,
                                                    another_id_limit=600)
def remove_admin(admin_slug_to_id, **kwargs):
    corporation_slug = CorporationAccess(
        id=kwargs['corporation_id']).slug_by_id()

    return remove_object(obj=kwargs['admin'],
                         func_name_for_redirected_url='corporation',
                         kwargs_for_redirected_url={
                             'corporation_slug_to_id': corporation_slug})


# Create employee view
@app.route('/create_employee/<company_slug_to_id>',
           endpoint='create_employee_view',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
def create_employee_view(company_slug_to_id, **kwargs):
    corporation_id = kwargs['corporation_id']
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


# TODO check compliance conditions
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


@app.route('/employee/<employee_slug_to_id>',
           endpoint='employee',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(myself=True, id_diff=-100,
                                                    another_id_limit=700)
def employee(employee_slug_to_id, **kwargs):
    company_id = kwargs['company_id']

    employee = kwargs['employee']

    company = CompanyAccess(id=company_id).object_by_id()

    # Groups client places
    gcp = another_objs_for_obj(company_id, obj=employee,
                               another_obj_class_name='GroupClientPlaces')

    # Client places
    cp = another_objs_for_obj(company_id, obj=employee,
                              another_obj_class_name='ClientPlace')

    return render_template('employee.html', the_employee_id=employee_slug_to_id,
                           the_employee_slug=employee.slug,
                           the_employee=employee, company=company,
                           groups_client_places_for_admin=gcp[
                               'other_objs_in_company'],
                           groups_client_places_with_this_employee=
                           gcp['other_objs_with_relationship_to_obj'],
                           groups_client_places_without=gcp[
                               'other_objs_without_relationship_to_obj'],
                           client_places_with_this_employee=cp[
                               'other_objs_with_relationship_to_obj'],
                           client_places_without=cp[
                               'other_objs_without_relationship_to_obj'],
                           client_places_for_admin=cp[
                               'other_objs_in_company'])

    # # Groups client places
    # gcp = groups_client_places_for_employee(company_id, employee=employee)
    #
    # # Client places
    # cp = client_places_for_employee(company_id, employee=employee)
    #
    # return render_template('employee.html', the_employee_id=employee_slug_to_id,
    #                        the_employee_slug=employee.slug,
    #                        the_employee=employee, company=company,
    #                        groups_client_places_for_admin=gcp[
    #                            'groups_client_places_for_admin'],
    #                        groups_client_places_with_this_employee=
    #                        gcp['groups_client_places_with_this_employee'],
    #                        groups_client_places_without=gcp[
    #                            'groups_client_places_without'],
    #                        client_places_with_this_employee=cp[
    #                            'client_places_with_this_employee'],
    #                        client_places_without=cp['client_places_without'],
    #                        client_places_for_admin=cp[
    #                            'client_places_for_admin'])


# todo cancel
# Employee editor view
@app.route('/edit_employee/<employee_slug_to_id>',
           endpoint='edit_employee',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(myself=True, id_diff=-100,
                                                    another_id_limit=600)
def edit_employee(employee_slug_to_id, **kwargs):
    employee = kwargs['employee']

    roles_to_choose = [(employee.role_id, employee.role.name)]

    if kwargs.get('valid_myself') is not True:
        roles = RoleAccess(corporation_id=employee.corporation_id). \
            roles_available_to_create_employee()

        roles_to_choose = [(i.id, i.name) for i in roles]

    form = EditEmployeeForm(roles_to_choose, employee, role=employee.role_id)
    if request.method == 'POST':

        if form.submit.data and form.validate_on_submit():
            EmployeeAccess(_obj=employee).edit_model_object(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                about=form.about.data.strip(),
                phone=None if form.phone.data.strip() == '' \
                    else form.phone.data.strip(),
                email=form.email.data.strip(),
                role_id=form.role.data.strip())

            flash('Your changes have been saved.')
            return redirect(url_for('employee',
                                    employee_slug_to_id=employee.slug))
    elif request.method == 'GET':
        form.first_name.data = employee.first_name
        form.last_name.data = employee.last_name
        form.about.data = employee.about
        form.phone.data = employee.phone
        form.email.data = employee.email
    return render_template('edit_employee.html',
                           title='Edit employee {}'.format(employee.id),
                           form=form, valid_myself=kwargs.get('valid_myself'))


# Employee deleter view
@app.route('/remove_employee/<employee_slug_to_id>',
           endpoint='remove_employee',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(myself=False, id_diff=-100,
                                                    another_id_limit=600)
def remove_employee(employee_slug_to_id, **kwargs):
    company_slug = CompanyAccess(
        id=kwargs['company_id']).slug_by_id()

    return remove_object(obj=kwargs['employee'],
                         func_name_for_redirected_url='company',
                         kwargs_for_redirected_url={
                             'company_slug_to_id': company_slug})


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


# todo - to Corporation for an employee(role>role_id Add his company or ...(?)
@app.route('/corporation/<corporation_slug_to_id>',
           endpoint='corporation',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=500, role_id_1=900)
def corporation(corporation_slug_to_id, **kwargs):
    companies = None
    if kwargs['valid_role_id']:
        companies = CompanyAccess(
            corporation_id=corporation_slug_to_id).companies_by_corporation_id()
    admins = AdminAccess(
        corporation_id=corporation_slug_to_id).admins_by_corporation_id()

    return render_template('corporation.html', companies=companies,
                           admins=admins, corporation=kwargs['corporation'])


# Corporation editor view
@app.route('/edit_corporation/<corporation_slug_to_id>',
           endpoint='edit_corporation',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=400)
def edit_corporation(corporation_slug_to_id, **kwargs):
    corporation = kwargs['corporation']

    form = EditCorporationForm(corporation.name)

    if request.method == 'POST' and form.validate_on_submit():
        CorporationAccess(_obj=corporation).edit_model_object(
            name=form.name.data.strip(),
            about=form.about.data.strip())
        flash('Your changes have been saved.')
        return redirect(url_for('corporation',
                                corporation_slug_to_id=corporation.slug))
    elif request.method == 'GET':
        form.name.data = corporation.name
        form.about.data = corporation.about
    return render_template('edit_corporation.html', title='Edit Corporation',
                           form=form)


# Corporation deleter view
@app.route('/remove_corporation/<corporation_slug_to_id>',
           endpoint='remove_corporation',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=100)
def remove_corporation(corporation_slug_to_id, **kwargs):
    return remove_object(obj=kwargs['corporation'],
                         func_name_for_redirected_url='profile')


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


@app.route('/company/<company_slug_to_id>',
           endpoint='company',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=700, role_id_1=800)
def company(company_slug_to_id, **kwargs):
    company_id = kwargs['company_id']

    employee_of_current_user = EmployeeAccess(
        company_id=company_id).employee_of_current_user_by_company_id()

    # Groups client places
    gcp = groups_client_places_for_employee(company_id,
                                            employee=employee_of_current_user)

    # Client places
    cp = client_places_for_employee(company_id,
                                    employee=employee_of_current_user)

    # Employee
    employees = EmployeeAccess(
        company_id=company_id).employees_by_company_id() \
        if kwargs['valid_role_id'] else None

    return render_template(
        'company.html', company=kwargs['company'], employees=employees,
        groups_client_places_for_admin=gcp['groups_client_places_for_admin'],
        groups_client_places_with_this_employee=
        gcp['groups_client_places_with_this_employee'],
        groups_client_places_without=gcp['groups_client_places_without'],
        client_places_with_this_employee=cp['client_places_with_this_employee'],
        client_places_without=cp['client_places_without'],
        client_places_for_admin=cp['client_places_for_admin'])


# todo cancel
# Company editor view
@app.route('/edit_company/<company_slug_to_id>',
           endpoint='edit_company',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=400)
def edit_company(company_slug_to_id, **kwargs):
    company = kwargs['company']
    form = EditCompanyForm(company.name, company.corporation_id)
    if request.method == 'POST' and form.validate_on_submit():
        CompanyAccess(_obj=company).edit_model_object(
            name=form.name.data.strip(),
            about=form.about.data.strip())
        flash('Your changes have been saved.')
        return redirect(url_for('company',
                                company_slug_to_id=company.slug))
    elif request.method == 'GET':
        form.name.data = company.name
        form.about.data = company.about
    return render_template('edit_company.html',
                           title='Edit company{}'.format(company.name),
                           form=form)


# Company deleter view
@app.route('/remove_company/<company_slug_to_id>',
           endpoint='remove_company',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=200)
def remove_company(company_slug_to_id, **kwargs):
    corporation_slug = CorporationAccess(
        id=kwargs['corporation_id']).slug_by_id()

    return remove_object(obj=kwargs['company'],
                         func_name_for_redirected_url='corporation',
                         kwargs_for_redirected_url={
                             'corporation_slug_to_id': corporation_slug})


# Create group client places view
@app.route(
    '/create_group_client_places/<company_slug_to_id>',
    endpoint='create_group_client_places_view',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
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


@app.route('/group_client_places/<group_client_places_slug_to_id>',
           endpoint='group_client_places',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def group_client_places(group_client_places_slug_to_id, **kwargs):
    group_client_places = kwargs['group_client_places']

    client_places = group_client_places.client_places

    employees = group_client_places.employees

    return render_template('group_client_places.html',
                           client_places=client_places, employees=employees,
                           group_client_places=group_client_places,
                           group_client_places_id= \
                               group_client_places_slug_to_id)


# Group Client places editor view
@app.route('/edit_group_client_places/<group_client_places_slug_to_id>',
           endpoint='edit_group_client_places',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
def edit_group_client_places(group_client_places_slug_to_id, **kwargs):
    group_client_places = kwargs['group_client_places']

    form = EditGroupClientPlacesForm(group_client_places.company_id,
                                     group_client_places.name,
                                     group_client_places.about)
    if request.method == 'POST':
        if form.submit.data and form.validate_on_submit():
            GroupClientPlacesAccess(_obj=group_client_places). \
                edit_model_object(
                name=form.name.data.strip(),
                about=form.about.data.strip())
        flash('Your changes have been saved.')
        return redirect(url_for(
            'group_client_places',
            group_client_places_slug_to_id=group_client_places.slug))
    elif request.method == 'GET':
        form.name.data = group_client_places.name
        form.about.data = group_client_places.about

    return render_template('edit_group_client_places.html',
                           title='Edit group client places {}'.format(
                               group_client_places.name),
                           form=form)


# Group client places deleter view
@app.route('/remove_group_client_places/<group_client_places_slug_to_id>',
           endpoint='remove_group_client_places',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
def remove_group_client_places(group_client_places_slug_to_id, **kwargs):
    company_slug = CompanyAccess(
        id=kwargs['company_id']).slug_by_id()

    return remove_object(obj=kwargs['group_client_places'],
                         func_name_for_redirected_url='company',
                         kwargs_for_redirected_url={
                             'company_slug_to_id': company_slug})


# Create client place view
@app.route('/create_client_place/<company_slug_to_id>',
           endpoint='create_client_place_view',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
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


@app.route('/client_place/<client_place_slug_to_id>',
           endpoint='client_place',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=900)
def client_place(client_place_slug_to_id, **kwargs):
    client_place = kwargs['client_place']

    group_client_places = client_place.groups_client_places

    employees = client_place.employees

    return render_template('client_place.html',
                           client_place=client_place, employees=employees,
                           client_place_id=client_place.id,
                           group_client_places=group_client_places)


# todo cancel
# Client place editor view
@app.route('/edit_client_place/<client_place_slug_to_id>',
           endpoint='edit_client_place',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
def edit_client_place(client_place_slug_to_id, **kwargs):
    client_place = kwargs['client_place']

    groups_client_places = GroupClientPlacesAccess(
        company_id=client_place.company_id).groups_client_places_by_company_id()

    choices_group_client_places = [(i.id, i.name) for i in groups_client_places]
    choices_group_client_places.insert(0, ('', 'group not selected'))

    form = EditClientPlaceForm(
        client_place.company_id, client_place.name, choices_group_client_places,
        group_client_places=client_place.group_client_places_id)
    if request.method == 'POST':
        if form.submit.data and form.validate_on_submit():
            ClientPlaceAccess(_obj=client_place).edit_model_object(
                name=form.name.data.strip(),
                group_client_places_id=form.group_client_places.data.strip())
            flash('Your changes have been saved.')
            return redirect(url_for('client_place',
                                    client_place_slug_to_id=client_place.slug))
    elif request.method == 'GET':
        form.name.data = client_place.name
    return render_template('edit_client_place.html',
                           title='Edit client place {}'.format(
                               client_place.name),
                           form=form)


# Client place deleter view
@app.route('/remove_client_place/<client_place_slug_to_id>',
           endpoint='remove_client_place',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=600)
def remove_client_place(client_place_slug_to_id, **kwargs):
    company_slug = CompanyAccess(
        id=kwargs['company_id']).slug_by_id()

    return remove_object(obj=kwargs['client_place'],
                         func_name_for_redirected_url='company',
                         kwargs_for_redirected_url={
                             'company_slug_to_id': company_slug})


# TODO check compliance conditions
# Create relationship employee to group client places
@app.route(
    '/create_relationship_emp_to_grp_cln_plcs/<group_client_places_slug_to_id>',
    endpoint='create_relationship_emp_to_grp_cln_plcs',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def create_relationship_emp_to_grp_cln_plcs(
        group_client_places_slug_to_id, **kwargs):
    next_page = request.args.get('next')

    employee = employee_or_current_employee(kwargs['company_id'])

    group_client_places = kwargs['group_client_places']

    result = BaseCompanyAccess(
        _obj=group_client_places, another_obj=employee). \
        create_relationship_in_company_obj_1_to_obj_2()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('group_client_places',
                group_client_places_slug_to_id=group_client_places.slug))


# TODO check compliance conditions
@app.route(
    '/remove_relationship_emp_to_grp_cln_plcs/<group_client_places_slug_to_id>',
    endpoint='remove_relationship_emp_to_grp_cln_plcs',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def remove_relationship_emp_to_grp_cln_plcs(
        group_client_places_slug_to_id, **kwargs):
    next_page = request.args.get('next')

    employee = employee_or_current_employee(kwargs['company_id'])

    group_client_places = kwargs['group_client_places']

    result = BaseCompanyAccess(
        _obj=group_client_places, another_obj=employee). \
        remove_relationship_obj_1_to_obj_2()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('group_client_places',
                group_client_places_slug_to_id=group_client_places.slug))


# TODO check compliance conditions
# Create relationship employee to client lace
@app.route('/create_relationship_emp_to_cln_plc/<client_place_slug_to_id>',
           endpoint='create_relationship_emp_to_cln_plc',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def create_relationship_emp_to_cln_plc(client_place_slug_to_id,
                                       **kwargs):
    next_page = request.args.get('next')

    employee = employee_or_current_employee(kwargs['company_id'])

    client_place = kwargs['client_place']

    result = BaseCompanyAccess(
        _obj=client_place, another_obj=employee). \
        create_relationship_in_company_obj_1_to_obj_2()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('client_place',
                client_place_slug_to_id=client_place.slug))


# TODO check compliance conditions
# Remove relationship employee to client place
@app.route(
    '/remove_relationship_emp_to_cln_plc/<client_place_slug_to_id>',
    endpoint='remove_relationship_emp_to_cln_plc',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def remove_relationship_emp_to_cln_plc(
        client_place_slug_to_id, **kwargs):
    next_page = request.args.get('next')

    employee = employee_or_current_employee(kwargs['company_id'])

    client_place = kwargs['client_place']

    result = BaseCompanyAccess(
        _obj=client_place, another_obj=employee). \
        remove_relationship_obj_1_to_obj_2()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('client_place',
                client_place_slug_to_id=client_place.slug))


# # TODO check compliance conditions
# # Create relationship employee to client lace
# @app.route('/create_relationship_emp_to_cln_plc/<client_place_slug_to_id>',
#            endpoint='create_relationship_emp_to_cln_plc',
#            methods=['GET', 'POST'])
# @login_required
# @role_validation_object_return_transform_slug_to_id(role_id=800)
# def create_relationship_emp_to_cln_plc(client_place_slug_to_id,
#                                        **kwargs):
#     next_page = request.args.get('next')
#
#     employee = employee_or_current_employee(kwargs['company_id'])
#
#     client_place = kwargs['client_place']
#
#     result = BaseCompanyAccess(
#         _obj=client_place, another_obj=employee). \
#         create_relationship_in_company_obj_1_to_obj_2()
#
#     flash(result[1])
#     if next_page:
#         return redirect(next_page)
#
#     return redirect(
#         url_for('client_place',
#                 client_place_slug_to_id=client_place.slug))


@app.route('/test_', methods=['GET', 'POST'])
# @login_required
def test():
    print(' --- TEST --- ')

    # cp1 = BaseAccess(
    #     slug='940a298729414b40b80dcfb8f8298a7e').object_from_entire_db_by_slug()
    # print(cp1)
    # cp1_gcp = cp1.groups_client_places
    # print('_from_obj' in cp1_gcp.__dict__)
    # cp1_e = cp1.employees
    # print(type(cp1_gcp))
    # print(type(cp1_e))
    #
    # print(cp1_gcp.__dict__)
    # print('')
    # for i in cp1_gcp.__dict__:
    #     print(i)
    # print('______________')
    # print(cp1_e.__dict__)
    # print('')
    #
    # for k, v in cp1_e.__dict__.items():
    #     print(k,' - ', v)
    # _____________________________
    # gcp1 = BaseAccess(
        # slug='ebd5349316574600b8963433679388dc').object_from_entire_db_by_slug()
    # print(gcp1)
    # gcp1_cp = gcp1.client_places
    # gcp1_e = gcp1.employees
    # print(dir(cp1_gcp))
    # print(dir(cp1_e))

    # print(gcp1_cp.all())
    # print(gcp1_cp.__dict__)
    # print('_from_obj' in gcp1_cp.__dict__)
    # print('')
    # for k, v in gcp1_cp.__dict__.items():
    #     print(k, ' - ', v)

    # print('______________')

    # print(gcp1_e.all())
    # print(gcp1_e.__dict__)
    # print('_from_obj' in gcp1_e.__dict__)
    # print('')
    # for k, v in gcp1_e.__dict__.items():
        # print(k,' - ', v)


    # ____________________
    model1_name = 'ClientPlace'
    model2_name = 'GroupClientPlaces' 
    model2_mapper = inspect(globals()[model2_name]).attrs

    for model2_mapper_k, model2_mapper_v in model2_mapper.items():

        if type(model2_mapper_v).__dict__['strategy_wildcard_key'] \
                is 'relationship':

            model2_mapper_v_dict = model2_mapper_v.__dict__ if '__dict__' in dir(model2_mapper_v) else None
            # if # todo END !!!!!!!!!!!!!!!!!!!!!
            print('entity', ' ----- ', str(model2_mapper_v_dict['entity']))
            print('back_populates', ' ----- ', str(model2_mapper_v_dict['back_populates']))
            print('_dependency_processor', ' ----- ', str(model2_mapper_v_dict['_dependency_processor']))
            print('--------------------------')

            # if model2_mapper_v_dict:
            #     for k_i, v_i in model2_mapper_v_dict.items():
            #
            #         print(k_i, ' - - - ', v_i)
            #     print('--------------------------')





        # if hasattr(i, '__dict__'):
        #     print(i.__dict__)
        # print(type(i))
        # print(dir(i))
        # print(' ')
    # print(dir(ClientPlace.groups_client_places.parent))
    # print(dir(ClientPlace.employees.parent))

    # print(dir(cmp.relationships.employees.__dict__))
    # print(dir(cmp.relationships.groups_client_places.__dict__))

    return render_template('test.html', test1='test1', test2='test2')
