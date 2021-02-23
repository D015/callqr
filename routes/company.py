# -*- coding: utf-8 -*-

from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app
from db_access import (CorporationAccess,
                       CompanyAccess,
                       EmployeeAccess,
                       role_validation_object_return_transform_slug_to_id)

from forms import (CompanyForm,
                   EditCompanyForm)

from utils.utils_routes import (another_objs_for_obj,
                                remove_object)


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
    if employee_of_current_user:
        employee_of_current_user_slug = employee_of_current_user.slug
    else:
        employee_of_current_user_slug = None

    # Groups client places
    gcp = another_objs_for_obj(company_id, obj=employee_of_current_user,
                               another_obj_class_name='GroupClientPlaces')

    # Client places
    cp = another_objs_for_obj(company_id, obj=employee_of_current_user,
                              another_obj_class_name='ClientPlace')

    # Employee
    employees = EmployeeAccess(
        company_id=company_id).employees_by_company_id() \
        if kwargs['valid_role_id'] else None

    return render_template(
        'company.html', company=kwargs['company'], employees=employees,
        the_employee_slug=employee_of_current_user_slug,
        groups_client_places_for_admin=gcp['other_objs_in_company'],
        groups_client_places_with_this_employee=gcp[
            'other_objs_with_relationship_to_obj'],
        groups_client_places_without=gcp[
            'other_objs_without_relationship_to_obj'],
        client_places_with_this_employee=cp[
            'other_objs_with_relationship_to_obj'],
        client_places_without=cp['other_objs_without_relationship_to_obj'],
        client_places_for_admin=cp['other_objs_in_company'])


# todo cancel
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