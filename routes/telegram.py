# -*- coding: utf-8 -*-
from flask import request

from app import app

from bot.telegram_bot import send_message_telegram

from db_access import EmployeeAccess


@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        if '/start ' in request.json['message']['text']:
            text_slug = request.json['message']['text'].replace('/start ', '')
            employee = EmployeeAccess(slug=text_slug).object_by_slug()
            if employee:
                chat_id = request.json['message']['chat']['id']
                EmployeeAccess(
                    _obj=employee).edit_model_object(telegram_chat_id=chat_id)

        the_id = request.json['message']['chat']['id']
        the_text = request.json['message']['text']

        print(request.json)
        print('___________________________')
        for k, v in request.json.items():

            print(k, ' --- ', v)
            if k == 'message':
                print('_____________________________')
                print('___________message__________________')
                print('_____________________________')
                for m_k, m_v in v.items():
                    print(m_k, ' --- ', m_v)
        send_message_telegram(the_id, the_text)
    return {"ok": True}