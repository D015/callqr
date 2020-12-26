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
    check_role_and_transform_corporation_slug_to_id, \
    check_role_and_return_company_transform_slug_to_id

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
def edit_user_view():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data.strip()
        current_user.about = form.about.data.strip()
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_user_view'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about.data = current_user.about
    return render_template('edit_user.html', title='Edit User',
                           form=form)


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


# Create admin view
@app.route('/create_admin/<corporation_slug_to_id>',
           endpoint='create_admin_view',
           methods=['GET', 'POST'])
@login_required
@check_role_and_transform_corporation_slug_to_id(role_id=401)
def create_admin_view(corporation_slug_to_id):
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

    return render_template('create_admin.html', form=form,
                           corporation_slug=corporation_slug_to_id)


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
@check_role_and_transform_corporation_slug_to_id(role_id=401)
def create_company_view(corporation_slug_to_id):
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

    return render_template('create_company.html', form=form,
                           corporation_slug=corporation_slug_to_id)


# Create employee view
@app.route('/create_employee/<company_slug_to_id>',
           endpoint='create_employee_view',
           methods=['GET', 'POST'])
@login_required
@check_role_and_transform_all_slug_to_id(role_id=999)
def create_employee_view(company_slug_to_id, corporation_id, *args):
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
    employee = EmployeeAccess(slug=employee_pending_slug).\
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
@check_role_and_transform_all_slug_to_id(role_id=601)
def create_group_client_places_view(company_slug_to_id, *args):
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
                           form_group_client_places=form,
                           company_slug_or_id=company_slug_to_id)


# Create client place view
@app.route(
    '/create_client_place/<company_slug_to_id>',
    endpoint='create_client_place_view',
    methods=['GET', 'POST'])
@login_required
@check_role_and_transform_all_slug_to_id(role_id=601)
def create_client_place_view(company_slug_to_id, *args):
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

        elif form.cancel_client_place.data :
            if next_page:
                return redirect(next_page)
            form.name_client_place.data = ''
            form.group_client_places.data = ''

    return render_template('create_client_place.html',
                           form_client_place=form,
                           company_slug_or_id=company_slug_to_id)


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
    corporation = CorporationAccess(id=admin.corporation_id).corporation_by_id()

    return render_template('admin.html', admin_id=admin_slug_to_id,
                           admin=admin, corporation=corporation)


@app.route('/employee/<employee_slug_to_id>', methods=['GET', 'POST'])
@login_required
def employee(employee_slug_to_id):
    employee = EmployeeAccess(slug=employee_slug_to_id).employees_by_slug()

    employee_id = employee.id

    company = CompanyAccess(id=employee.company_id).company_by_id()

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
        slug=group_client_places_slug_to_id).group_client_places_by_slug()

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
        slug=client_place_slug_to_id).client_place_by_slug()

    client_place_id = client_place.id

    group_client_places = client_place.group_client_places

    employees = client_place.employees

    return render_template('client_place.html',
                           client_place=client_place, employees=employees,
                           client_place_id=client_place_id,
                           group_client_places=group_client_places)




# _Old__routes______________________________________

@app.route('/test', methods=['GET', 'POST'])
# @login_required
def test():
    # __________________________
    # arg1 = request.args.get('arg1')
    # arg2 = request.args.get('arg2')
    # _____________________________
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
    #         'ef65ef6686d04a25a357dd8065122c8b').id).first()).first_role_id
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
    #     Employee.first_role_id < 701).first()
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
    # print(employees_of_current_user())
    # print(admins_of_current_user())
    # print(clients_of_current_user())
    # print(the_current_user())
    # _____________________________________________________
    # print(CompanyAccess().companies_of_current_user_by_corporation_id())
    # return render_template('index.html', title='Home')
    # __________________________________________________________
    current_user_admin_corporation = current_user.admins.filter_by(
            corporation_id=1).first()
    print(current_user_admin_corporation, type(current_user_admin_corporation))
    return render_template('index.html', title='Home')