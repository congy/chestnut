from kandan_schema import *

q_mi_1 = get_all_records(channel)
q_mi_1.finclude(f('activities'))
q_mi_1.get_include(f('activities')).finclude(f('user'))
q_mi_1.complete()



