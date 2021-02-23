# -*- coding: utf-8 -*-
from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app

from db_access import (AdminAccess,
                       CompanyAccess,
                       CorporationAccess,
                       role_validation_object_return_transform_slug_to_id)

from forms import (CorporationForm,
                   EditCorporationForm)

from utils.utils_routes import remove_object


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


@app.route('/remove_corporation/<corporation_slug_to_id>',
           endpoint='remove_corporation',
           methods=['GET', 'POST'])
@login_required
@role_validation_object_return_transform_slug_to_id(role_id=100)
def remove_corporation(corporation_slug_to_id, **kwargs):
    return remove_object(obj=kwargs['corporation'],
                         func_name_for_redirected_url='profile')