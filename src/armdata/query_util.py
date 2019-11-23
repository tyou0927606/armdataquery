"""
Query the database
"""

import os
import tdclient


class ArmQuery:
    
    def __init__(self, apikey, endpoint='https://api.treasuredata.com'):
        self._apikey = apikey
        self._endpoint = endpoint
        
    def checkDbAndTable(self, database, table):
        """Check that the specified db and table exist
        Args:
            db: database name
            table: table name
            
        Return:
            (True, "table") # db and table exist
            (False, "database" | "table") # either db or table does not exist
        """
        
        msg = ""
        db_found = False
        table_found = False
        with tdclient.Client(apikey=self._apikey, endpoint=self._endpoint) as client:
            for db in client.databases():
                if db.name == database:
                    db_found = True
                    for tbl in db.tables():
                        if tbl.table_name == table:
                            table_found = True
                            msg = ""
                            return (True, msg)
        
                        
        #Either db or table is not found
        if not db_found:
            return (False, "database")
        else:
            return (False, "table")
    
    def checkTableColumns(self, db, table, col_list):
        """Check that the column list are indeed in the specified table
        Args:
            db: database name
            table: table name
            col_list: list of column names
            
        Return:
            (True, []) # The specified list of column names is in the table
            (False, list of column names missing in the table) #mismatching column names
        """
        query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE                TABLE_NAME='"+table+"';"
          
        with tdclient.Client(apikey=self._apikey, endpoint=self._endpoint) as client:
            job = client.query(db, query, type="presto")
            # sleep until job's finish
            job.wait()
            column_names = [column for row in job.result() for column in row]
            missing_columns = []
            for col in col_list:
                if col not in column_names:
                    missing_columns.append(col)
            if missing_columns:
                return (False, missing_columns)
            else:
                return (True, [])
            
    def _queryTableColumnNames(self, db, table):
        """Query column names in the specified table
        Args:
            db: database name
            table: table name
        Return:
            list of column names in the table
        """
        query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE                TABLE_NAME='"+table+"';"
          
        with tdclient.Client(apikey=self._apikey, endpoint=self._endpoint) as client:
            job = client.query(db, query, type="presto")
            # sleep until job's finish
            job.wait()
            column_names = [column for row in job.result() for column in row]
            return column_names
            
    def query(self, db, table, col_list, min_time, max_time, limit, engine):
        """Query the specified table
        Args:
            db: database name
            table: table name
            col_list: list of column names
            min_time: min time stamp
            max_time: max time stamp
            limit: limit of records
            engine: engine type
        Return:
            tuple of column names and List of records that match the query criteria
        """
        if not col_list:
            column_names = self._queryTableColumnNames(db, table)
        else:
            column_names = col_list.split(',')
            
        if not col_list:
            col_list = ",".join(column_names)
        if not min_time:
            min_time = "NULL"
        if not max_time:
            max_time = "NULL"
        if  not limit:
            limit_cause = ";"
        else:
            limit_cause = " LIMIT "+str(limit)+";"
        query = "SELECT "+col_list+" FROM "+table+" WHERE TD_TIME_RANGE(time, "+str(min_time)+", " +str(max_time)+")"+limit_cause
          
        with tdclient.Client(apikey=self._apikey, endpoint=self._endpoint) as client:
            job = client.query(db, query, type=engine)
            # sleep until job's finish
            job.wait()
            rows = [row for row in job.result()]
            return (column_names, rows)
        
        
if __name__ == "__main__":
    td = ArmQuery("10574/8fe2c7251368da13d3365a683b37fa382c87f8eb", 'https://api.treasuredata.com')
    
    """
    status, msg = td._checkDbAndTable("sample_datasets", "www_access")
    print("checkDbAndTable return: {0} and msg: {1}".format(status, msg))
    
    status, column_names = td.checkTableColumns("www_access", [])
    print("checkTableColumns return: {0} and msg: {1}".format(status, column_names))
    """
    
    col_list = None
    min_time = None
    max_time = None
    limit = 1
    engine = "hive"
    columns, rows = td.query("sample_datasets", "www_access", col_list, min_time, max_time, limit, engine)
    print(columns)
    print(rows)