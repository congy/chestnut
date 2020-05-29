import sys, os
script_dir = os.path.dirname(__file__)
os.chdir(script_dir)
sys.path.append(os.path.abspath(os.path.join(script_dir, '..', '..')))

import json
from typing import *

from schema import *
from query import *
from pred import *
from plan_search import *
from ilp.ilp_manager import *
from ds_manager import *
from query_manager import *
from populate_database import *
from codegen.protogen import *
from codegen.codegen_test import *
import globalv

from .activities_create import *
from .activities_index import *
from .activities_show import *
from .admin_index import *
from .admin_toggle_admin import *
from .admin_update_user import *
from .attachment_create import *
from .attachment_index import *
from .channels_create import *
from .channels_index import *
from .channels_show import *
from .main_index import *
from .main_search import *
#from .ilp_solve import *

def run(workload_name: str = "kandan_lg", single_query: int = -1,
        membound_factor: float = 1.7,
        queries: str = "(q_ai_1,1)|(q_ai_2,1)|(q_ai_3,1)|(q_as_1,1)|(q_ti_1,1)|(q_ci_1,1)|(q_cs_1,1)|(q_ms_1,1)",
        gen_tsv: bool = False, gen_cpp: bool = False, load_sql: bool = False,
        run_test_read_overall: bool = True, output = sys.stdout):
    """
    Args:
        - run_ilp: If ILP should be run.
        - single_query: Choose a single read query to solve by index, or -1 to solve all queries.
        - gen_tsv: If tsv files should be generated.
        - gen_db: If db should be generated.
        - run_test_read_overall: Run test_read_overall.
        - quiet: If debug prints should be supressed.
    """

    set_db_name(workload_name)
    datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
    set_data_file_dir(datafile_dir)

    dr = os.path.dirname(__file__)
    set_cpp_file_path(os.path.join(dr, '..', '..'))

    tables = [user, channel, activity, attachment]
    associations = [channel_to_activitiy, channel_user, activity_user, attachment_user, attachment_channel]

    globalv.tables = tables
    globalv.associations = associations
    #generate_db_data_files(datafile_dir, tables, associations)
    #exit(0)

    #read_queries: [ReadQuery] = [
    #    q_ai_1,
    #    q_ai_2,
    #    q_ai_3, \
    #    q_as_1,
    #    # q_di_1,
    #    q_ti_1,
    #    q_ci_1,
    #    q_cs_1,
    #    # q_mi_1,
    #    q_ms_1
    #]
    
    # set queries from parameter
    queries = [(x[1:].split(',')[0], float(x[:-1].split(',')[1])) for x in queries.split('|')]

    read_queries = []
    weights = []
    for q,weight in queries:
      if q == 'q_ai_1' and weight > 0:
        read_queries.append(q_ai_1)
        weights.append(weight)
      elif q == 'q_ai_2' and weight > 0:
        read_queries.append(q_ai_2)
        weights.append(weight)
      elif q == 'q_ai_3' and weight > 0:
        read_queries.append(q_ai_3)
        weights.append(weight)
      elif q == 'q_as_1' and weight > 0:
        read_queries.append(q_as_1)
        weights.append(weight)
      elif q == 'q_di_1' and weight > 0:
        read_queries.append(q_di_1)
        weights.append(weight)
      elif q == 'q_ti_1' and weight > 0:
        read_queries.append(q_ti_1)
        weights.append(weight)
      elif q == 'q_ci_1' and weight > 0:
        read_queries.append(q_ci_1)
        weights.append(weight)
      elif q == 'q_cs_1' and weight > 0:
        read_queries.append(q_cs_1)
        weights.append(weight)
      elif q == 'q_mi_1' and weight > 0:
        read_queries.append(q_mi_1)
        weights.append(weight)
      elif q == 'q_ms_1' and weight > 0:
        read_queries.append(q_ms_1)
        weights.append(weight)
      else:
        print("Query not found: {}".format(q))
        
    print("Queries and weights: ", file=sys.stderr)
    for i,q in enumerate(read_queries):
      print("{}: weight = {}".format(q, weights[i]), file=sys.stderr)

    write_queries = [
        q_ac_w1, q_ac_w2, q_ac_w3,
        q_du_1,
        q_dt_1,
        q_tc_w1, q_tc_w2, q_tc_w3,
        q_cc_w1, q_cc_w2
    ]

    #test_schema(tables, association)
    #exit(0)

    #q_ai_1.assigned_param_values = {Parameter('channel_id'):'47', Parameter('oldest'):'183'}
    #q_ai_2.assigned_param_values = {Parameter('channel_id'):'47'}

    # q_ti_1.assigned_param_values = {Parameter('channel_id'):'3'}
    # q_tc_w2.assigned_param_values = {Parameter('channel_id'):'3', Parameter('attachment_id'):'14'}
    #[q_ti_1], [q_tc_w1, q_tc_w2]

    #q_ci_1.assigned_param_values = {Parameter('channel_id'):'47'}
    results_json: Dict
    if single_query >= 0:
        search_plans_for_one_query(read_queries[single_query])
        results = ilp_solve([ read_queries[single_query] ], write_queries=[], membound_factor=membound_factor, save_to_file=False, read_from_file=False, read_ilp=False, save_ilp=False)
        results_json = get_ilp_result_json([ read_queries[single_query] ], *results)
        #exit(0)
        #get_dsmeta(read_queries)

        # test_merge(q)
        #test_cost(read_queries[:1])
    else:
        # Begin here.
        # test_ilp(read_queries, membound_factor=membound_factor)
        # membound_factor: memory bound vs table size (2 means mem bound is 2x table size).
        # TODO: tunable membound_factor.
        results = ilp_solve(read_queries, write_queries=[], membound_factor=membound_factor, save_to_file=True, read_from_file=False, read_ilp=False, save_ilp=True)
        results_json = get_ilp_result_json(read_queries, *results)

    if run_test_read_overall:
        test_read_overall(tables, associations, read_queries, memfactor=membound_factor, read_from_file=True, read_ilp=True)

    data_dir = datafile_dir
    if gen_tsv:
        # TODO: race condition: write files, then read files
        generate_db_data_files(data_dir, tables, associations)
    results_json['data'] = read_db_data_files(data_dir)

    if gen_cpp:
        generate_proto_files(get_cpp_file_path(), tables, associations)
        populate_database(data_dir, tables, associations, False) # TODO should this be in load_sql?
        test_query(tables, associations, read_queries[5], 13) # TODO only one query??

    if load_sql:
        s = create_psql_tables_script(data_dir, tables, associations)
        f = open('load_postgres_tables.sql', 'w')
        f.write(s)
        f.close()

    print(json.dumps(results_json, indent = 2), file = output)

    #populate_database(data_dir, tables, associations, True)
    #test_query(tables, associations, read_queries[0], 13)

    # indexes = {user:[['id']],\
    # channel:[],\
    # activity:[['id'], ['channel_id', 'id'], ['user_id']],\
    # attachment:[['channel_id', 'created_at']]}
    # s = create_psql_tables_script(data_dir, tables, associations, indexes)
    # f = open('load_postgres_tables.sql', 'w')
    # f.write(s)
    # f.close()

    print('scale', scale)

if '__main__' == __name__:
    run()
