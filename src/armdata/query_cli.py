import os
import click
import re
from tabulate import tabulate
import tdclient
from armdata import query_util

class ArmQueryCLI:
    """It takes the following parameters to perform a query and return the 
    results in specified format:
    
    required: database name 'db_name'
    required: table name 'table_name'
    
    optional: comma separated list of columns 'col_list' as string (e.g.
        'column1,column2,column3’). If not specified, all columns are selected.
        
    optional: minimum timestamp 'min_time' in unix timestamp or 'NULL'
    optional: maximum timestamp 'max_time' in unix timestamp or 'NULL'.
        Obviously 'max_time' must be greater than 'min_time' or NULL.
        
    optional: query engine ‘engine’: 'hive' or 'presto'. Defaults to ‘presto’.
    
    optional: output format ‘format’: ‘csv’ or ‘tabular'. Defaults to ‘tabular’.
    
    optional: a query limit ‘limit’: ‘100’. If not specified, all records are selected.
        and it will run a query like:
        SELECT <col_list>
            FROM <table_name>
            WHERE TD_TIME_RANGE(time, <min_time>, <max_time>) LIMIT <limit>
    """
    
    DEFAULT_ENDPOINT = "https://api.treasuredata.com/"
    
    def __init__(self, db_name, table_name):
        self.db = db_name
        self.table = table_name
    
        if "TD_API_KEY" in os.environ:
            self._apikey = os.getenv("TD_API_KEY")
        else:
            raise ValueError("no API key given")
            
        if os.getenv("TD_API_SERVER"):
            self._endpoint = os.getenv("TD_API_SERVER")
        else:
            self._endpoint = self.DEFAULT_ENDPOINT
            
        self.arm_query = query_util.ArmQuery(self._apikey, self._endpoint)
        
    def verifyDbAndTable(self):
        """If verifies that the db name and table name exist
        Return: (True, "")  #table name found
        or (False, "table"|"database") # either database name or table name not found
        """
        try:
            status, cause = self.arm_query.checkDbAndTable(self.db, self.table)
            return (status, cause)
        except tdclient.errors.APIError as e:
            #assert str(e) == 'List databases failed: {"error":"Failed to Login"}'
            raise click.ClickException(str(e))
        except tdclient.errors.DatabaseError as e:
            raise click.ClickException(str(e))
    
    def verifyTableColumns(self, col_list):
        """If verifies that the db name and table name exist
        Args:
            col_list: list of column names
        Return: 
            (True, "")  #table name found
            or (False, "table"|"database") # either database name or table name not found
        """
        try:
            status, missing_columns = self.arm_query.checkTableColumns(self.db, self.table, col_list)
            return (status, missing_columns)
        except tdclient.errors.APIError as e:
            raise click.ClickException(str(e))
        except tdclient.errors.DatabaseError as e:
            raise click.ClickException(str(e))
    
    def query(self, col_list, min_time, max_time, limit, engine):
        """Query the table with the provided parameters
        Args:
            col_list: list of column names separated by comma
            min_time: min time stamp
            max_time: max time stamp
            limit: limit of records
            engine: engine type
        Return:
            tuple of column names and List of records that match the query criteria
        """
        try:
            columns, rows = self.arm_query.query(self.db, self.table, col_list, min_time, max_time, limit, engine)
            return (columns, rows)
        except tdclient.errors.APIError as e:
            raise click.ClickException(str(e))
        except tdclient.errors.DatabaseError as e:
            raise click.ClickException(str(e))
            
        except ValueError as e:
            raise click.ClickException(str(e))

def validate_limit(ctx, param, value):
    if value and value <=0:
        raise click.BadParameter('limit should be a positive integer')
    elif value == 0:
        raise click.BadParameter('limit should be a positive integer')
    return value

def validate_unix_timestamp(ctx, param, value):
    """Verify that the timestamp is unix timestamp: 1427347140
    
       Any positive integer is valid
    """
    if value and value<0:
        raise click.BadParameter('Timestamp should be of unix timestamp: '+str(value))
    return value

def validate_timestamp_range(min_time, max_time):
    """Verify that the min_time is less than max_time
    """
    if int(min_time) > int(max_time):
        raise click.BadParameter('Min time is greater than the max time')

def print_tabular(column_names, data):
    print(tabulate(data, headers=column_names))
    
def print_csv(column_names, data):
    def convertToStr(column):
        if not column:
            return ""
        else:
            return str(column)
        
    print(",".join(column_names))
    for row in data:
        formatted_row = [convertToStr(col) for col in row]
        print(",".join(formatted_row))
    
"""  
query -f csv -e hive -c 'my_col1,my_col2,my_col5' -m 1427347140 -M 1427350725 -l 100
my_db my_table
where:
● -f / --format is optional and specifies the output format: tabular by default
● -c / --column is optional and specifies the comma separated list of columns to restrict the
result to. Read all columns if not specified.
● -l / --limit is optional and specifies the limit of records returned. Read all records if not
specified.
● -m / --min is optional and specifies the minimum timestamp: NULL by default
● -M / --max is optional and specifies the maximum timestamp: NULL by default
● -e / --engine is optional and specifies the query engine: ‘presto’ by default
"""

@click.command()
@click.argument('db_name')
@click.argument('table_name')
@click.option(
    '--format', '-f',
    default='tabular',
    type=click.Choice(['csv', 'tabular']),
    help='Output format',
)
@click.option(
    '--column', '-c',
    help='Table column list, separated by comma'
)
@click.option(
    '--limit', '-l', type=int, callback=validate_limit,
    help='Limit of records returned'
)
@click.option('--min', '-m', type=int, callback=validate_unix_timestamp, 
              help='Minimum timestamp')
@click.option('--max', '-M', type=int, callback=validate_unix_timestamp,
              help='Maximum timestamp')
@click.option(
    '--engine', '-e',
    default='presto',
    type=click.Choice(['hive', 'presto']),
    help='Database engine type',
)
def main(db_name, table_name, format, column, limit, min, max, engine):
     
    if min and max:
        validate_timestamp_range(min, max)
        
    #Verify that the database name and table name exist
    #Print proper error messages if not so
    query_cli = ArmQueryCLI(db_name, table_name)
    status, cause = query_cli.verifyDbAndTable()
    if not status:
        if cause == "database":
            raise click.BadParameter('Database name not found')
        elif cause == "table":
            raise click.BadParameter('Table name not found')
            
    #Verify that the provided column list exist in the table
    if column:
        column_list = column.split(',')
        status, missing_columns = query_cli.verifyTableColumns(column_list)
        if not status:
            raise click.BadParameter('Column names not found in the table: %s' %str(missing_columns))
    
    columns, rows = query_cli.query(column, min, max, limit, engine)
    #print("columns: {0}".format(columns))
    
    #print the retrieved data to screen
    if format == "csv":
        print_csv(columns, rows)
    elif format == "tabular":
        print_tabular(columns, rows)
        

def start():
    main()
    
if __name__ == "__main__":
    start()