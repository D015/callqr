# -*- coding: utf-8 -*-

from flask import (render_template,
                   flash,
                   redirect,
                   url_for,
                   request)

from flask_login import (current_user,
                         login_user,
                         logout_user,
                         login_required)

from sqlalchemy import or_

from werkzeug.urls import url_parse

from app import app

@app.route('/test_', methods=['GET', 'POST'])
# @login_required
def test():
    print(' --- START TEST --- ')


    print(' --- END TEST --- ')

    return render_template('test.html', test1='test1', test2='test2')