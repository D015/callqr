# -*- coding: utf-8 -*-
from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app

from db_access import (ClientPlaceAccess,
                       CompanyAccess,
                       GroupClientPlacesAccess,
                       role_validation_object_return_transform_slug_to_id)

from forms import (ClientPlaceForm,
                   EditClientPlaceForm)

from utils.utils_routes import (another_objs_for_obj,
                                remove_object)


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
    company_id = kwargs['company_id']

    client_place = kwargs['client_place']

    gcp = another_objs_for_obj(company_id, obj=client_place,
                               another_obj_class_name='GroupClientPlaces')

    employees = another_objs_for_obj(company_id, obj=client_place,
                                     another_obj_class_name='Employee')

    return render_template('client_place.html',
                           client_place=client_place,
                           client_place_slug=client_place.slug,
                           client_place_id=client_place_slug_to_id,
                           groups_client_places_with_this_cp=gcp[
                               'other_objs_with_relationship_to_obj'],
                           groups_client_places_without=gcp[
                               'other_objs_without_relationship_to_obj'],
                           groups_client_places_for_company=gcp[
                               'other_objs_in_company'],
                           employees_with_this_cp=employees[
                               'other_objs_with_relationship_to_obj'],
                           employees_without=employees[
                               'other_objs_without_relationship_to_obj'],
                           employees_for_company=employees[
                               'other_objs_in_company'])


# todo cancel
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