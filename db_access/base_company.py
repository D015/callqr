from flask import render_template

from db_access.base import BaseAccess
from db_access.base_inspect import BaseInspectAccess
from utils_add import add_commit

from models import (Admin,
                    Client,
                    ClientPlace,
                    Company,
                    Corporation,
                    Employee,
                    GroupClientPlaces)


class BaseCompanyAccess(BaseAccess):
    def __init__(self, company_id=None, _obj=None, another_obj=None,
                 _obj_class_name=None, another_obj_class_name=None):

        self.company_id = company_id
        self._obj = _obj
        self._obj_class_name = _obj_class_name
        self.another_obj = another_obj
        self.another_obj_class_name = another_obj_class_name

    def objs_of_class_name_by_company_id(self):
        obj_class = globals()[self._obj_class_name]
        objs = obj_class.query.filter_by(company_id=self.company_id).all()
        return objs

    def is_relationship_obj_to_another_obj(self):
        if self._obj is None or self.another_obj is None:
            return render_template('404.html')

        inspect_obj_to_another_obj = BaseInspectAccess(
            model_name=self._obj.__class__.__name__,
            another_model_name=self.another_obj.__class__.__name__). \
            backrefs_and_type_of_model_to_model()

        _obj_attr_another_obj = inspect_obj_to_another_obj[
            'model_attr_another_model']

        _obj_another_obj = getattr(self._obj, _obj_attr_another_obj)

        is_iter = not (inspect_obj_to_another_obj[
                           'model_to_another_model_type'] == \
                       'ManyToOne')
        if is_iter:
            is_relationship = self.another_obj in _obj_another_obj
        else:
            is_relationship = self.another_obj is _obj_another_obj

        relationship_info = {'is_relationship': is_relationship,
                             'is_iter': is_iter,
                             '_obj_attr_another_obj': _obj_attr_another_obj
                             }

        return relationship_info

    def create_relationship_in_company_obj_to_another_obj(self):

        relationship_info = self.is_relationship_obj_to_another_obj()

        is_relationship = relationship_info['is_relationship']

        is_iter = relationship_info['is_iter']

        _obj_attr_another_obj = relationship_info['_obj_attr_another_obj']

        if is_relationship is False:
            if is_iter:
                getattr(self._obj, _obj_attr_another_obj). \
                    append(self.another_obj)
            else:
                setattr(self._obj, _obj_attr_another_obj, self.another_obj)

            add_commit(self._obj)
            return True, 'The relationship successfully created'
        elif is_relationship:
            return False, 'The relationship already existed'
        else:
            return None, 'error'

    def remove_relationship_obj_to_another_obj(self):
        relationship_info = self.is_relationship_obj_to_another_obj()

        is_relationship = relationship_info['is_relationship']

        is_iter = relationship_info['is_iter']

        _obj_attr_another_obj = relationship_info['_obj_attr_another_obj']

        if is_relationship:
            if is_iter:
                getattr(self._obj, _obj_attr_another_obj). \
                    remove(self.another_obj)
            else:
                setattr(self._obj, _obj_attr_another_obj, None)

            add_commit(self._obj)
            return True, 'The relationship successfully removed'
        elif is_relationship:
            return False, 'There was no relationship before'
        else:
            return None, 'error'

    # todo combine 'with' and 'without'
    #  to use another backrefs_and_type_of_model_to_model once
    def other_objs_without_relationship_obj(self):
        another_obj_class = globals()[self.another_obj_class_name]

        relationship_info = BaseInspectAccess(
            model_name=self._obj.__class__.__name__,
            another_model_name=self.another_obj_class_name). \
            backrefs_and_type_of_model_to_model()

        another_obj_class_attr_obj_name = \
            relationship_info['another_model_attr_model']

        relationship_type = relationship_info['model_to_another_model_type']

        if relationship_type == 'OneToMany':
            other_objs = another_obj_class.query.filter(
                another_obj_class.company_id == self._obj.company_id,
                getattr(another_obj_class,
                        another_obj_class_attr_obj_name) != self._obj).all()

        # (SQLAlchemy==1.3.17)SAWarning: Got None for value of column
        # client_place.group_client_places_id; this is unsupported for
        # a relationship comparison and will not currently produce
        # an IS comparison (but may in a future release)
        elif relationship_type == 'ManyToOne' \
                and getattr(self._obj,
                            relationship_info[
                                'model_attr_another_model']) is None:

            other_objs = another_obj_class.query.filter(
                another_obj_class.company_id == self._obj.company_id).all()

        else:
            other_objs = another_obj_class.query.filter(
                another_obj_class.company_id == self._obj.company_id,
                ~getattr(another_obj_class,
                         another_obj_class_attr_obj_name). \
                contains(self._obj)).all()

        return other_objs

    def other_objs_with_relationship_obj(self):
        relationship_info = BaseInspectAccess(
            model_name=self._obj.__class__.__name__,
            another_model_name=self.another_obj_class_name). \
            backrefs_and_type_of_model_to_model()

        _obj_other_objs = getattr(
            self._obj, relationship_info['model_attr_another_model'])

        # if many to one
        if relationship_info['model_to_another_model_type'] == 'ManyToOne':
            other_objs = [] if _obj_other_objs is None else [_obj_other_objs]
        else:
            other_objs = _obj_other_objs.all()

        return other_objs
