### Welcome to [Chestnut](https://congyan.org/chestnut.pdf) project! ###

Chestnut is a data layout generator for
in-memory object-oriented database applications. 

- It takes a set of object queries and a memory bound 
as input and generates customized data layout.

- The nested data layout can be nested (to reduce serializaing from the tabular layout 
as used in database to the nested layout as used in the application) 
with fancy indexes (to preprocess the queries as much as possible).

- Chestnut formulates the search of optimal layout under a memory bound
into ILP problem which can achieve desired tradeoff between memory and query performance. 

While still under maintainance, you may check out some examples under `benchmarks/`. 

For instance, in `benchmarks/kandan/kandan.py`, you can run
```
generate_db_data_files(datafile_dir, tables, associations)
populate_database(datafile_dir, tables, associations, True)
```
which generates random data for the application and populates MySQL database with the random data. 
You can go to `kandan_schema.py` to change the `scale` in order to generate data with different sizes.
The generated data will be in a tsv file with fields separated by `|`, stored under `./data/#{workload_name}/`

Then you can run
```
search_plans_for_one_query(q_ci_1)
```
to see all the query plans and data structures enumerated by Chestnut for an individual query (currently printing out using Chestnut IR).

You can try
```
test_codegen_one_query(tables, associations, q_ci_1)
```
to see the best data structure generated for a single query, with the c++ code generated. 
When you go to the folder of generated code (`./#{workload_name}/`), 
you can compile the code and run it. This code will load data from MySQL 
to populate the data structure (the data loading may take a while), and runs the query
with a subset of the query result printed along with how long the query takes.

If you have [gurobi license](https://www.gurobi.com/) installed, you can try the ILP to see how query plans share data structures.
To enable ILP, go to `./ilp/ilp_manager.y` and uncomment line
```
from gurobipy import *
```
If you don't have the license installed, you are still able to run the non-ILP stuffs 
(like generating code for a single query), by uncommenting this line in `./ilp/ilp_manager.y`,
```
from ilp_fake import *
```
To run the ILP and see the data structures generated (including code), try the following:
```
ilp_solve(read_queries, write_queries=[], membound_factor=1.7, save_to_file=True, read_from_file=False, read_ilp=False, save_ilp=True)
test_read_overall(tables, associations, read_queries, memfactor=1.7, read_from_file=True, read_ilp=True)
```
Write queries are currently not supported. `membound_factor` is the ratio of the allowed memory bound 
to the size of the application data. Similarly, the generated code will be stored to `./#{workload_name}/`.

You can also test the serialization cost between the c++-returned query result to the ruby objects. 
To do so, you can change the following line in `globalv.py`
```
qr_type = 'struct'
```
to 
```
qr_type = 'proto'
```
The code-gen process will also generates a ruby test file which sends query parameter and receives query result
from the Chestnut-generated C++ code using [zmq](https://zeromq.org/). The ruby tes file is
under `./#{workload_name}/ruby`. To run the test, you may first compile and run the Chestnut-generated c++ code,
which will populate the data structures and wait for request, and then run the ruby file to run the queries.
