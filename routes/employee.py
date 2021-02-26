# -*- coding: utf-8 -*-
from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app

from db_access import (CompanyAccess,
                       EmployeeAccess,
                       RoleAccess,
                       role_validation_object_return_transform_slug_to_id)

from forms import (EmployeeForm,
                   EditEmployeeForm)

from utils.utils_routes import (remove_object,
                                another_objs_for_obj)


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

    valid_myself = kwargs.get('valid_myself')

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
                           valid_myself=valid_myself,
                           groups_client_places_for_admin=gcp[
                               'other_objs_in_company'],
                           groups_client_places_with_this_employee=gcp[
                               'other_objs_with_relationship_to_obj'],
                           groups_client_places_without=gcp[
                               'other_objs_without_relationship_to_obj'],
                           client_places_with_this_employee=cp[
                               'other_objs_with_relationship_to_obj'],
                           client_places_without=cp[
                               'other_objs_without_relationship_to_obj'],
                           client_places_for_admin=cp[
                               'other_objs_in_company'])


# todo cancel
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
                role_id=form.role.data.strip(),
                active=form.active.data,
                archived=form.archived.data)

            flash('Your changes have been saved.')
            return redirect(url_for('employee',
                                    employee_slug_to_id=employee.slug))
    elif request.method == 'GET':
        form.first_name.data = employee.first_name
        form.last_name.data = employee.last_name
        form.about.data = employee.about
        form.phone.data = employee.phone
        form.email.data = employee.email
        form.active.data = employee.active
        form.archived.data = employee.archived
    return render_template('edit_employee.html',
                           title='Edit employee {}'.format(employee.id),
                           form=form, valid_myself=kwargs.get('valid_myself'))



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
