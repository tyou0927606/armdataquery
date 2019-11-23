import pytest
import click
from click.testing import CliRunner
import tdclient
from mock import patch
from armdata import query_util
from armdata import query_cli
from armdata.query_util import ArmQuery
from armdata.query_cli import start, main

@patch('armdata.query_util.ArmQuery')
def test_cli_with_row_records(mock_class):
    """Query successfuly gets the records back and prints it 
    
       query_util.ArmQuery instance is mocked to return records.
       Both the exit code and all records are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (True, [])
    columns = ['user','path','host','method','time']
    data = [[None, '144.138.86.216', '/category/software','GET','1412377158'],
            [None, '209.69.132.222', '/google/software/1166', 'GET', '1412377148'],
            [None, '219.69.132.222', '/yahoo/software/1166', 'GET', '1412377138'],
            [None, '220.69.132.222', '/linkedin/software/1166', 'GET', '1412377128'],
            [None, '300.69.132.222', '/item/software/1166', 'GET', '1412377108'],
           ]
    instance.query.return_value = (columns, data)
    
    col_list = ','.join(columns)
    runner = CliRunner()
    options = ["-l 5", "-c {0}".format(col_list)]
    result = runner.invoke(main, ["sample_datasets", "www_access", *options])
    
    assert result.exit_code == 0
    #verify that every row of data is returned
    output_header_data = result.output.split('\n')
    for row in data:
        assert row[1] in result.output
        for output_row in output_header_data:
            if row[1] in output_row:
                for i in range(2, len(row)):
                    assert row[i] in output_row
    

@patch('armdata.query_util.ArmQuery')
def test_cli_with_db_name_non_existent(mock_class):
    """Query fails when the user provided database name does not exist 
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (False, "database")
    
    columns = ['user','path','host','method','time']
    col_list = ','.join(columns)
    db_name = "non_existent_db"
    runner = CliRunner()
    result = runner.invoke(main, [db_name, "www_access", "-l 5",  "-c "+col_list])
    
    assert result.exit_code == 2
    assert "Database name not found" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_column_name_non_existent(mock_class):
    """Query fails when the user provided table name does not exist 
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (False, ['method1','time1'])
    
    columns = ['user','path','host','method1','time1']
    col_list = ','.join(columns)
    table_name = "non_existent_tb"
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", table_name, "-l 5",  "-c "+col_list])
    
    assert result.exit_code == 2
    assert "Column names not found" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_table_name_non_existent(mock_class):
    """Query fails when the user provided non existent column names 
       in the column list option
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (False, "table")
    
    columns = ['user','path','host','method','time']
    col_list = ','.join(columns)
    table_name = "non_existent_tb"
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", table_name, "-l 5",  "-c "+col_list])
    
    assert result.exit_code == 2
    assert "Table name not found" in result.output

@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_auth_exception(mock_class):
    """Query fails when the user fails to authenticate
    
       Both the exit code and error message are verified.
    """
    error_msg = 'List databases failed: {"error":"Failed to Login"}'
    instance = mock_class.return_value
    instance.checkDbAndTable.side_effect = tdclient.errors.AuthError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_forbidden_exception(mock_class):
    """Query fails when the user tries to access forbidden stuff
    
       Both the exit code and error message are verified.
    """
    error_msg = 'List databases failed: {"error":"Forbidden to access"}'
    instance = mock_class.return_value
    instance.checkDbAndTable.side_effect = tdclient.errors.ForbiddenError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_not_found_exception(mock_class):
    """Query fails when the user tries to access non existent stuff
       This is unlikey to happen as the the implementation already checks 
       the existence of database name and table name
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (True, [])
    error_msg = 'List databases failed: {"error":"Not Found"}'
    
    instance.query.side_effect = tdclient.errors.NotFoundError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_data_error(mock_class):
    """Query fails when there is DataError
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (True, [])
    error_msg = 'Access databases failed: {"error":"Data error"}'
    
    instance.query.side_effect = tdclient.errors.DataError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_operational_error(mock_class):
    """Query fails when there is OperationalError
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (True, [])
    error_msg = 'Access databases failed: {"error":"Operational error"}'
    
    instance.query.side_effect = tdclient.errors.OperationalError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_integrity_error(mock_class):
    """Query fails when there is IntegrityError
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (True, [])
    error_msg = 'Access databases failed: {"error":"Integrity error"}'
    
    instance.query.side_effect = tdclient.errors.IntegrityError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_runtime_internal_error(mock_class):
    """Query fails when there is InternalError
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    instance.checkTableColumns.return_value = (True, [])
    error_msg = 'Access databases failed: {"error":"Internal error"}'
    
    instance.query.side_effect = tdclient.errors.InternalError(error_msg)
    
    runner = CliRunner()
    result = runner.invoke(main, ["sample_datasets", "www_access", "-l 1", "-c user,host,method,time"])
    
    assert result.exit_code == 1
    assert error_msg in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_non_conforming_min_timestamp(mock_class):
    """Query fails when the user provided min timestamp is not 
     unix timestamp
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    
    runner = CliRunner()
    result = runner.invoke(main, ["sampe_datasets", "www_access", "-l 5",  "-m -123456789"])
    
    assert result.exit_code == 2
    assert "Timestamp should be of unix timestamp" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_non_conforming_max_timestamp(mock_class):
    """Query fails when the user provided max timestamp is not 
     unix timestamp
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    
    runner = CliRunner()
    result = runner.invoke(main, ["sampe_datasets", "www_access", "-l 5",  "-M -123457608"])
    
    assert result.exit_code == 2
    assert "Timestamp should be of unix timestamp" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_non_integer_max_timestamp(mock_class):
    """Query fails when the user provided max timestamp is not 
     integer unix timestamp
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    
    runner = CliRunner()
    result = runner.invoke(main, ["sampe_datasets", "www_access", "-l 5",  "-M -1234576da"])
    
    assert result.exit_code == 2
    assert "not a valid integer" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_inconsisten_min_max_timestamp(mock_class):
    """Query fails when the user provided min timestamp is greater
        than the max timestamp 
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    
    runner = CliRunner()
    result = runner.invoke(main, ["sampe_datasets", "www_access", "-m 1412377106", 
                                  "-M 1412377100"])
    
    assert result.exit_code == 2
    assert "Min time is greater than the max time" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_non_supported_output_format(mock_class):
    """Query fails when the user provided non supported output format
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    
    runner = CliRunner()
    result = runner.invoke(main, ["sampe_datasets", "www_access", "-f json"])
    
    assert result.exit_code == 2
    assert "choose from csv, tabular" in result.output
    
@patch('armdata.query_util.ArmQuery')
def test_cli_with_non_supported_engine_type(mock_class):
    """Query fails when the user provided non supported engine type
    
       Both the exit code and error message are verified.
    """
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (True, "")
    
    runner = CliRunner()
    result = runner.invoke(main, ["sampe_datasets", "www_access", "-e what"])
    
    assert result.exit_code == 2
    assert "choose from hive, presto" in result.output
