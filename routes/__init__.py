from .base import (before_request,
                   index)

from .admin import (create_admin_view,
                    create_relationship_admin_to_user_view,
                    admin,
                    edit_admin,
                    remove_admin)

from .client_place import (create_client_place_view,
                           client_place,
                           edit_client_place,
                           remove_client_place)

from .company import (create_company_view,
                      company,
                      edit_company,
                      remove_company)

from .corporation import (create_corporation_view,
                          corporation,
                          edit_corporation,
                          remove_corporation)

from .employee import (create_employee_view,
                       create_relationship_employee_to_user_view,
                       employee,
                       edit_employee,
                       remove_employee)

from .group_client_places import (create_group_client_places_view,
                                  group_client_places,
                                  edit_group_client_places,
                                  remove_group_client_places)

from .user import (register,
                   login,
                   logout,
                   profile,
                   edit_user,
                   remove_user)

from .relationship import (create_relationship_emp_to_grp_cln_plcs,
                           remove_relationship_emp_to_grp_cln_plcs,
                           create_relationship_emp_to_cln_plc,
                           remove_relationship_emp_to_cln_plc,
                           create_relationship_gcp_to_cln_plc,
                           remove_relationship_gcp_to_cln_plc)

from .telegram import telegram_webhook

from .test import test