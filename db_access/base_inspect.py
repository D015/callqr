from sqlalchemy import inspect

from models import (Admin,
                    Client,
                    ClientPlace,
                    Company,
                    Corporation,
                    Employee,
                    GroupClientPlaces)


class BaseInspectAccess:
    def __init__(self, model_name=None, another_model_name=None):

        self.another_model_name = another_model_name
        self.model_name = model_name

    def backrefs_and_type_of_model_to_model(self):
        """ returns dictionary with keys:
        model_attr_another_model,
        another_model_attr_model,
        model_to_another_model_type.
        model_to_another_model_type is given in the format
        OneToMany, ManyToOne, ManyToMany"""

        relationship_model_to_another_model = {}

        model_mapper = inspect(globals()[self.model_name]).attrs

        for model_mapper_k, model_mapper_v in model_mapper.items():

            if type(model_mapper_v).__dict__['strategy_wildcard_key'] \
                    is 'relationship':

                model_mapper_v_dict = model_mapper_v.__dict__ \
                    if '__dict__' in dir(model_mapper_v) else None

                model_mapper_attr_entity = \
                    str(model_mapper_v_dict['entity']). \
                        replace('mapped class ', '').split('-')[0]

                if model_mapper_attr_entity == self.another_model_name:
                    another_model_attr_model = \
                        model_mapper_v_dict['back_populates']

                    model_attr_another_model = \
                        str(model_mapper_v_dict['_dependency_processor']). \
                            split('.')[1].replace(')', '')

                    model_to_model_type = \
                        str(model_mapper_v_dict['_dependency_processor']). \
                            split('DP(')[0]
                    relationship_model_to_another_model = {
                        'another_model_attr_model': another_model_attr_model,
                        'model_attr_another_model': model_attr_another_model,
                        'model_to_another_model_type': model_to_model_type
                    }


        return relationship_model_to_another_model