import inspect


def check_role_and_return_object_and_transform_slug_to_id(
        role_id=0, others=False):
    def decorator_role(func):
        def check_role(obj_slug_to_id, *args, **kwargs):

            slug_arg_name = inspect.getfullargspec(func).args[0]
            obj_name = slug_arg_name[:slug_arg_name.find('_slug')]
            obj_name_underscore_replaced_by_spaces = obj_name.replace('_', ' ')
            cls_name_with_spaces = \
                obj_name_underscore_replaced_by_spaces.title()
            cls_name = cls_name_with_spaces.replace(' ', '')
            cls_name_access = cls_name + 'Access'
            cls = globals()[cls_name_access]
            # another option is to get the class
            # import importlib
            # cls = getattr(importlib.import_module("db_access"), cls_name_access)
