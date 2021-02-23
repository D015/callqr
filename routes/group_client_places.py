# -*- coding: utf-8 -*-
from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app

from db_access import (CompanyAccess,
                       GroupClientPlacesAccess,
                       role_validation_object_return_transform_slug_to_id)

from forms import (GroupClientPlacesForm,
                   EditGroupClientPlacesForm)

from utils.utils_routes import (another_objs_for_obj,
                                remove_object)


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
    company_id = kwargs['company_id']

    group_client_places = kwargs['group_client_places']

    # Client places
    cp = another_objs_for_obj(company_id, obj=group_client_places,
                              another_obj_class_name='ClientPlace')
    # Employees
    employees = another_objs_for_obj(company_id, obj=group_client_places,
                                     another_obj_class_name='Employee')

    return render_template('group_client_places.html',
                           group_client_places=group_client_places,
                           group_client_places_slug=group_client_places.slug,
                           group_client_places_id= \
                               group_client_places_slug_to_id,
                           client_places_with_this_gcp=cp[
                               'other_objs_with_relationship_to_obj'],
                           client_places_without=cp[
                               'other_objs_without_relationship_to_obj'],
                           client_places_for_company=cp[
                               'other_objs_in_company'],
                           employees_with_this_gcp=employees[
                               'other_objs_with_relationship_to_obj'],
                           employees_without=employees[
                               'other_objs_without_relationship_to_obj'],
                           employees_for_company=employees[
                               'other_objs_in_company'])


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