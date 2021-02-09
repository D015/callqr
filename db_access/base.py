from app import db
from utils_add import add_commit


class BaseAccess:

    def __init__(self, id=None, slug=None, _obj=None, model=None):
        self.id = id
        self.slug = slug
        self._obj = _obj
        self.model = model

    def object_is_exist(self):
        is_exist = self._obj.__class__.query.get(self._obj.id)
        return True if is_exist else False

    def remove_object(self):
        if self._obj:
            obj_id = self._obj.id
            db.session.delete(self._obj)
            db.session.commit()
            return obj_id
        return None

    def edit_model_object(self, **kwargs):
        for key, value in kwargs.items():
            if value:
                setattr(self._obj, key, value)
            else:
                setattr(self._obj, key, None)
        add_commit(self._obj)
        return self._obj

    def object_by_slug(self):
        obj = self.model.query.filter_by(slug=self.slug).first()
        return obj

    def object_by_slug_or_404(self):
        obj = self.model.query.filter_by(slug=self.slug).first_or_404()
        return obj

    def object_id_by_slug(self):
        return self.object_by_slug().id

    def object_by_id(self):
        obj = self.model.query.get(self.id)
        return obj

    def object_by_id_or_404(self):
        obj = self.model.query.filter_by(id=self.id).first_or_404()
        return obj

    def slug_by_id(self):
        slug = self.model.query.get(self.id).slug
        return slug

    def object_from_entire_db_by_slug(self):
        for model_i in db.Model._decl_class_registry.values():
            if hasattr(model_i, 'slug'):
                obj_i = model_i.query.filter_by(slug=self.slug).first()
                if obj_i:
                    return obj_i
