# -*- coding: utf-8 -*-

from flask import (render_template)

from app import app

from utils.utils_routes import call_of_employees_from_client_place


@app.route('/call_qr/<client_place_slug_link>',
           methods=['GET', 'POST'])
def call_qr(client_place_slug_link):
    the_call_qr = call_of_employees_from_client_place(
        client_place_slug_link=client_place_slug_link, type_call_out_id=10)
    print(the_call_qr)
    if the_call_qr:
        return render_template('index.html')
    return render_template('404.html')