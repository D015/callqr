# -*- coding: utf-8 -*-

from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import login_required

from app import app

from db_access import (AdminAccess,
                       CorporationAccess,
                       RoleAccess,
                       role_validation_object_return_transform_slug_to_id)

from forms import (AdminForm,
                   EditAdminForm)

from utils.utils_routes import remove_object


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