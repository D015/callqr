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
