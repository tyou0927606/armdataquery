======================
armdata: command line query package to query Arm Treasure Data database tables
======================

armdata is a package to demonstate how to build a command line utility to 
query Arm Treasure Data tables. It makes use of tdclient python client to
perform actual SQL queries. The CLI implementation makes use of wonderful click
 to provide parameter verification.
 
Some sample unit tests are provided, they are for demonstration purpose only, 
not meant to be exclusive.

---------------------------
How to install the package:

1. Set the environment variable "TD_API_KEY" to the assigned key

export TD_API_KEY=<api_key>

2. Run "pip install tox" to install "tox" first 

3. Then run "tox" in the folder where the downloaded source code is located 
to install the local package "armdata" along with the required packages to 
the python virtualenv specified in "tox.ini".

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ tox
GLOB sdist-make: /Users/Tim/Documents/arm_treasure_data/setup.py
py37 create: /Users/Tim/Documents/arm_treasure_data/.tox/py37
py37 installdeps: pytest
py37 inst: /Users/Tim/Documents/arm_treasure_data/.tox/.tmp/package/1/armdata-1.0.zip
py37 installed: armdata==1.0,attrs==19.3.0,Click==7.0,importlib-metadata==0.23,mock==3.0.5,more-itertools==7.2.0,msgpack==0.6.2,packaging==19.2,pluggy==0.13.1,py==1.8.0,pyparsing==2.4.5,pytest==5.3.0,python-dateutil==2.8.1,six==1.13.0,tabulate==0.8.6,td-client==1.1.0,urllib3==1.25.7,wcwidth==0.1.7,zipp==0.6.0
py37 run-test-pre: PYTHONHASHSEED='1122654074'
py37 run-test: commands[0] | pytest -v
============================== test session starts ==============================
platform darwin -- Python 3.7.4, pytest-5.3.0, py-1.8.0, pluggy-0.13.1 -- /Users/Tim/Documents/arm_treasure_data/.tox/py37/bin/python
cachedir: .tox/py37/.pytest_cache
rootdir: /Users/Tim/Documents/arm_treasure_data
collected 21 items                                                              

tests/unit/test_cli.py::test_cli_with_row_records PASSED                  [  4%]
tests/unit/test_cli.py::test_cli_with_db_name_non_existent PASSED         [  9%]
tests/unit/test_cli.py::test_cli_with_column_name_non_existent PASSED     [ 14%]
tests/unit/test_cli.py::test_cli_with_table_name_non_existent PASSED      [ 19%]
tests/unit/test_cli.py::test_cli_with_runtime_auth_exception PASSED       [ 23%]
tests/unit/test_cli.py::test_cli_with_runtime_forbidden_exception PASSED  [ 28%]
tests/unit/test_cli.py::test_cli_with_runtime_not_found_exception PASSED  [ 33%]
tests/unit/test_cli.py::test_cli_with_runtime_data_error PASSED           [ 38%]
tests/unit/test_cli.py::test_cli_with_runtime_operational_error PASSED    [ 42%]
tests/unit/test_cli.py::test_cli_with_runtime_integrity_error PASSED      [ 47%]
tests/unit/test_cli.py::test_cli_with_runtime_internal_error PASSED       [ 52%]
tests/unit/test_cli.py::test_cli_with_non_conforming_min_timestamp PASSED [ 57%]
tests/unit/test_cli.py::test_cli_with_non_conforming_max_timestamp PASSED [ 61%]
tests/unit/test_cli.py::test_cli_with_non_integer_max_timestamp PASSED    [ 66%]
tests/unit/test_cli.py::test_cli_with_inconsisten_min_max_timestamp PASSED [ 71%]
tests/unit/test_cli.py::test_cli_with_non_supported_output_format PASSED  [ 76%]
tests/unit/test_cli.py::test_cli_with_non_supported_engine_type PASSED    [ 80%]
tests/unit/test_query.py::test_check_db_and_table PASSED                  [ 85%]
tests/unit/test_query.py::test_check_db_and_table_exception PASSED        [ 90%]
tests/unit/test_query.py::test_check_db_and_table_class PASSED            [ 95%]
tests/unit/test_query.py::test_check_db_and_table_class_exception PASSED  [100%]

============================== 21 passed in 0.66s ===============================
____________________________________ summary ____________________________________
  py37: commands succeeded
  congratulations :)
 
------------------------
How to run the query command:

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query --help
Usage: query [OPTIONS] DB_NAME TABLE_NAME

Options:
  -f, --format [csv|tabular]  Output format
  -c, --column TEXT           Table column list, separated by comma
  -l, --limit INTEGER         Limit of records returned
  -m, --min INTEGER           Minimum timestamp
  -M, --max INTEGER           Maximum timestamp
  -e, --engine [hive|presto]  Database engine type
  --help                      Show this message and exit.

Examples:

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 10 -e presto -f tabular -c host,path,referer,code,size,method sample_datasets www_access
host             path                     referer                  code    size  method
---------------  -----------------------  ---------------------  ------  ------  --------
224.225.147.72   /category/books?from=10  /item/games/2018          200     135  GET
136.204.225.125  /category/health         /category/games           200     136  GET
32.57.104.68     /category/office         /category/computers       200     113  GET
144.138.86.216   /category/software       -                         200     135  GET
200.69.132.222   /item/software/1166      -                         200      47  GET
200.81.68.44     /category/cameras        /category/electronics     200      81  GET
44.90.70.114     /category/office         -                         200      68  GET
108.75.69.24     /category/electronics    -                         200      40  GET
216.177.45.198   /category/toys           /item/books/3472          200      62  GET
184.189.183.181  /category/cameras        /item/giftcards/3836      200     133  GET

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 3 -e presto -f tabular sample_datasets2 www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME

Error: Invalid value: Database name not found

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 3 -e presto -f tabular sample_datasets www_access2
Usage: query [OPTIONS] DB_NAME TABLE_NAME

Error: Invalid value: Table name not found

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 3 -e presto -f tabular -c host,path,referer,code,size,method2 sample_datasets www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME

Error: Invalid value: Column names not found in the table: ['method2']

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l -1 -e presto -f tabular sample_datasets www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME

Error: Invalid value for "--limit" / "-l": limit should be a positive integer

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 3e -e presto -f tabular sample_datasets www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME
Try "query --help" for help.

Error: Invalid value for "--limit" / "-l": 3e is not a valid integer

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 3 -e hiwe -f tabular sample_datasets www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME
Try "query --help" for help.

Error: Invalid value for "--engine" / "-e": invalid choice: hiwe. (choose from hive, presto)

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 3 -e presto -f tabuler sample_datasets www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME
Try "query --help" for help.

Error: Invalid value for "--format" / "-f": invalid choice: tabuler. (choose from csv, tabular)

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 10 -e presto -f csv -c host,path,referer,code,size,method sample_datasets www_access
host,path,referer,code,size,method
80.171.155.85,/category/music,-,200,85,GET
52.141.188.126,/category/cameras?from=20,/category/cameras,200,124,GET
168.198.44.173,/category/software,/item/health/1326,200,79,GET
208.72.203.122,/item/electronics/3989,/category/software,200,94,GET
196.66.55.38,/category/games,-,200,103,GET
68.99.200.136,/category/office,-,200,98,GET
204.36.47.69,/category/software,-,200,41,GET
120.165.87.31,/category/electronics,-,200,73,GET
48.114.174.177,/category/electronics,-,200,73,GET
152.150.61.167,/item/jewelry/675,/item/networking/3044,200,102,GET

(base) Tims-MacBook-Pro-2:arm_treasure_data Tim$ query -l 10 -e presto -f json -c host,path,referer,code,size,method sample_datasets www_access
Usage: query [OPTIONS] DB_NAME TABLE_NAME
Try "query --help" for help.

Error: Invalid value for "--format" / "-f": invalid choice: json. (choose from csv, tabular)



----------------------
How to run the unit tests

During installation of the package to the virtualenv, "tox" invokes the tests after installation.

To run the provided unit tests, run "pytest -v".  