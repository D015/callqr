from flask import flash, redirect, url_for, request

from app import db


def add_commit(db_obj):
    db.session.add(db_obj)
    db.session.commit()


def sort_dict_value(my_dict):
    list_my_dict = list(my_dict.items())
    list_my_dict.sort(key=lambda i: i[1])
    return list_my_dict


def sort_dict_value_contr(my_dict, contr=False):
    contr = 1 if contr is False else -1
    list_my_dict = list(my_dict.items())
    list_my_dict.sort(key=lambda i: i[1] * contr)
    return list_my_dict


# def remove_object(obj):
#     next_page = request.args.get('next')
#     form = RemoveObjectForm(obj)
#     if request.method == 'POST':
#         if form.submit.data and form.validate_on_submit():
#             BaseAccess(_obj=obj).remove_object()
#             flash('Your changes have been saved.')
#             return redirect(url_for('index'))
#             if next_page:
#                 return redirect(next_page)
#         elif form.cancel.data:
#             if next_page:
#                 return redirect(next_page)
#         else:
#             redirect(url_for('profile'))
#
#     return render_template('remove_object.html', obj=obj, title='Remove Object',
#                            form=form)