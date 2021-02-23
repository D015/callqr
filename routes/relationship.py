# -*- coding: utf-8 -*-
from flask import (flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app

from db_access import (BaseCompanyAccess,
                       EmployeeAccess,
                       GroupClientPlacesAccess,
                       role_validation_object_return_transform_slug_to_id)


# TODO check compliance conditions
@app.route(
    '/create_relationship_emp_to_grp_cln_plcs/<group_client_places_slug_to_id>',
    endpoint='create_relationship_emp_to_grp_cln_plcs',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def create_relationship_emp_to_grp_cln_plcs(
        group_client_places_slug_to_id, **kwargs):
    next_page = request.args.get('next')

    employee_slug = request.args.get('employee_slug_to_id')

    employee = EmployeeAccess(slug=employee_slug).object_by_slug()

    group_client_places = kwargs['group_client_places']

    result = BaseCompanyAccess(
        _obj=group_client_places, another_obj=employee). \
        create_relationship_in_company_obj_to_another_obj()

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

    employee_slug = request.args.get('employee_slug_to_id')

    employee = EmployeeAccess(slug=employee_slug).object_by_slug()

    group_client_places = kwargs['group_client_places']

    result = BaseCompanyAccess(
        _obj=group_client_places, another_obj=employee). \
        remove_relationship_obj_to_another_obj()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('group_client_places',
                group_client_places_slug_to_id=group_client_places.slug))


# TODO check compliance conditions
@app.route('/create_relationship_emp_to_cln_plc/<client_place_slug_to_id>',
           endpoint='create_relationship_emp_to_cln_plc',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def create_relationship_emp_to_cln_plc(client_place_slug_to_id,
                                       **kwargs):
    next_page = request.args.get('next')

    employee_slug = request.args.get('employee_slug_to_id')

    employee = EmployeeAccess(slug=employee_slug).object_by_slug()

    client_place = kwargs['client_place']

    result = BaseCompanyAccess(
        _obj=client_place, another_obj=employee). \
        create_relationship_in_company_obj_to_another_obj()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('client_place',
                client_place_slug_to_id=client_place.slug))


# TODO check compliance conditions
@app.route(
    '/remove_relationship_emp_to_cln_plc/<client_place_slug_to_id>',
    endpoint='remove_relationship_emp_to_cln_plc',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def remove_relationship_emp_to_cln_plc(
        client_place_slug_to_id, **kwargs):
    next_page = request.args.get('next')

    employee_slug = request.args.get('employee_slug_to_id')

    employee = EmployeeAccess(slug=employee_slug).object_by_slug()

    client_place = kwargs['client_place']

    result = BaseCompanyAccess(
        _obj=client_place, another_obj=employee). \
        remove_relationship_obj_to_another_obj()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('client_place',
                client_place_slug_to_id=client_place.slug))


# TODO check compliance conditions
@app.route('/create_relationship_gcp_to_cln_plc/<client_place_slug_to_id>',
           endpoint='create_relationship_gcp_to_cln_plc',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def create_relationship_gcp_to_cln_plc(client_place_slug_to_id,
                                       **kwargs):
    next_page = request.args.get('next')

    group_client_places_slug = request.args.get(
        'group_client_places_slug_to_id')

    group_client_places = GroupClientPlacesAccess(
        slug=group_client_places_slug).object_by_slug()

    client_place = kwargs['client_place']

    result = BaseCompanyAccess(
        _obj=client_place, another_obj=group_client_places). \
        create_relationship_in_company_obj_to_another_obj()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('client_place',
                client_place_slug_to_id=client_place.slug))


# TODO check compliance conditions
@app.route(
    '/remove_relationship_gcp_to_cln_plc/<client_place_slug_to_id>',
    endpoint='remove_relationship_gcp_to_cln_plc',
    methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=800)
def remove_relationship_gcp_to_cln_plc(
        client_place_slug_to_id, **kwargs):
    next_page = request.args.get('next')

    group_client_places_slug = request.args.get(
        'group_client_places_slug_to_id')

    group_client_places = GroupClientPlacesAccess(
        slug=group_client_places_slug).object_by_slug()

    client_place = kwargs['client_place']

    result = BaseCompanyAccess(
        _obj=client_place, another_obj=group_client_places). \
        remove_relationship_obj_to_another_obj()

    flash(result[1])
    if next_page:
        return redirect(next_page)

    return redirect(
        url_for('client_place',
                client_place_slug_to_id=client_place.slug))


