from flask import request, redirect, url_for, render_template, flash

from bot.email_bot import send_call_qr_email
from bot.telegram_bot import send_message_telegram
from db_access import BaseAccess, GroupClientPlacesAccess, EmployeeAccess, \
    ClientPlaceAccess, BaseCompanyAccess
from db_access.call import CallAccess
from forms import RemoveObjectForm


def remove_object(obj=None, func_name_for_redirected_url='index',
                  kwargs_for_redirected_url={}):
    next_page = request.args.get('next')
    form = RemoveObjectForm(obj)
    if request.method == 'POST':
        if form.submit.data and form.validate_on_submit():
            remote_obj_id = BaseAccess(_obj=obj).remove_object()
            if remote_obj_id:
                flash('Your changes have been saved.')
            else:
                flash('Something went wrong!')
            return redirect(url_for(func_name_for_redirected_url,
                                    **kwargs_for_redirected_url))
        elif form.cancel.data:
            if next_page:
                return redirect(next_page)
        else:
            redirect(url_for('profile'))

    return render_template('remove_object.html', obj=obj, title='Remove Object',
                           form=form)


def groups_client_places_for_employee(company_id, employee=None):
    # - for admin
    groups_client_places_for_admin = GroupClientPlacesAccess(
        company_id=company_id).groups_client_places_by_company_id() \
        if employee is None else []

    # - for employee
    groups_client_places_with_this_employee = []
    groups_client_places_without = []
    if employee:
        # - for employee with relationship
        groups_client_places_with_this_employee = EmployeeAccess(
            _obj=employee). \
            groups_client_places_with_relationship_the_employee()
        # for employee without relationship
        groups_client_places_without = EmployeeAccess(
            _obj=employee). \
            groups_client_places_without_relationship_the_employee()

    gcp = {
        'groups_client_places_for_admin': groups_client_places_for_admin,
        'groups_client_places_with_this_employee':
            groups_client_places_with_this_employee,
        'groups_client_places_without': groups_client_places_without
    }
    return gcp


def client_places_for_employee(company_id, employee=None):
    # - for admin
    client_places_for_admin = ClientPlaceAccess(
        company_id=company_id).client_places_by_company_id() \
        if employee is None else []

    # - for employee
    client_places_with_this_employee = []
    client_places_without = []
    if employee:
        # - for employee with relationship
        client_places_with_this_employee = EmployeeAccess(
            _obj=employee). \
            client_places_with_relationship_the_employee()
        # for employee without relationship
        client_places_without = EmployeeAccess(
            _obj=employee). \
            client_places_without_relationship_the_employee()

    cp = {
        'client_places_for_admin': client_places_for_admin,
        'client_places_with_this_employee':
            client_places_with_this_employee,
        'client_places_without': client_places_without
    }
    return cp


def another_objs_for_obj(company_id, obj=None, another_obj_class_name=None):
    # - for object doesn't exist
    other_objs_in_company = BaseCompanyAccess(
        company_id=company_id, _obj_class_name=another_obj_class_name). \
        objs_of_class_name_by_company_id() if obj is None else []

    # - for obj exists
    other_objs_with_relationship_to_obj = []
    other_objs_without_relationship_to_obj = []
    if obj:
        other_objs_with_relationship_to_obj = BaseCompanyAccess(
            _obj=obj, another_obj_class_name=another_obj_class_name). \
            other_objs_with_relationship_obj()

        other_objs_without_relationship_to_obj = BaseCompanyAccess(
            _obj=obj, another_obj_class_name=another_obj_class_name). \
            other_objs_without_relationship_obj()

    other_objs = {
        'other_objs_in_company': other_objs_in_company,
        'other_objs_with_relationship_to_obj':
            other_objs_with_relationship_to_obj,
        'other_objs_without_relationship_to_obj':
            other_objs_without_relationship_to_obj}

    return other_objs


def employee_or_current_employee(company_id):
    employee_slug = request.args.get('employee_slug_to_id')
    if employee_slug:
        employee = EmployeeAccess(slug=employee_slug).object_by_slug()
    else:
        employee = EmployeeAccess(company_id=company_id). \
            employee_of_current_user_by_company_id()
    return employee


def call_of_employees_from_client_place(client_id=None,
                                        client_place_slug_link=None,
                                        type_call_out_id=None):

    cln_plc_empls_contacts = ClientPlaceAccess(slug_link=client_place_slug_link). \
        selection_of_employee_contacts_to_call_from_client_place()
    print(cln_plc_empls_contacts)

    client_place_name = f'Call {cln_plc_empls_contacts["client_place"].name}'

    call_email_success = None
    if cln_plc_empls_contacts['employees_emails']:
        for employee_email in cln_plc_empls_contacts['employees_emails']:
            send_call_qr_email(employee_email[1], client_place_name)

            CallAccess(type_call_out_id=type_call_out_id,
                       type_call_in_id=10,
                       destination=employee_email[1],
                       client_id=client_id,
                       client_place_id= \
                           cln_plc_empls_contacts['client_place'].id,
                       group_client_places_id= \
                           cln_plc_empls_contacts['client_place']. \
                       group_client_places_id,
                       company_id= \
                           cln_plc_empls_contacts['client_place'].company_id,
                       corporation_id= \
                           cln_plc_empls_contacts['client_place']. \
                       company.corporation_id,
                       employee_id=employee_email[0]). \
                create_call_of_employees_from_client_place()

        call_email_success = True

    call_telegram_success = None
    if cln_plc_empls_contacts['employees_telegrams']:
        for employee_telegram in cln_plc_empls_contacts['employees_telegrams']:
            send_message_telegram(employee_telegram[1], client_place_name)

            CallAccess(type_call_out_id=type_call_out_id,
                       type_call_in_id=20,
                       destination=employee_telegram[1],
                       client_id=client_id,
                       client_place_id= \
                           cln_plc_empls_contacts['client_place'].id,
                       group_client_places_id= \
                           cln_plc_empls_contacts['client_place']. \
                       group_client_places_id,
                       company_id= \
                           cln_plc_empls_contacts['client_place'].company_id,
                       corporation_id= \
                           cln_plc_empls_contacts['client_place']. \
                       corporation_id,
                       employee_id=employee_email[0]). \
                create_call_of_employees_from_client_place()

        call_telegram_success = True

    if call_email_success or call_telegram_success:
        return True
    return False
