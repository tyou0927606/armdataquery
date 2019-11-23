import pytest
import tdclient
from mock import patch
from armdata import query_util
from armdata.query_util import ArmQuery

@patch.object(ArmQuery, 'checkDbAndTable')
def test_check_db_and_table(mock_checkDbAndTable):
    mock_checkDbAndTable.return_value = (False, "database")
    
    assert ArmQuery("10574/8fe2c7251368da13d33683b37fa382c87f8eb", 'https://api.treasuredata.com').checkDbAndTable('sample_datasets', "www_acc") == (False, "database")


@patch.object(ArmQuery, 'checkDbAndTable')
def test_check_db_and_table_exception(mock_checkDbAndTable):
    mock_checkDbAndTable.side_effect = ValueError("The specified query type is not supported")
    
    try:
        ArmQuery("10574/8fe2c7251368da13d33683b37fa382c87f8eb", 'https://api.treasuredata.com').checkDbAndTable('sample_datasets', "www_acc")
    except ValueError as e:
        assert str(e) == "The specified query type is not supported"
        

@patch('armdata.query_util.ArmQuery')
def test_check_db_and_table_class(mock_class):
    instance = mock_class.return_value
    instance.checkDbAndTable.return_value = (False, "database")
    
    assert query_util.ArmQuery("10574/8fe2c7251368da13d33683b37fa382c87f8eb", 'https://api.treasuredata.com').checkDbAndTable('sample_datasets', "www_acc") == (False, "database")
    
@patch('armdata.query_util.ArmQuery')
def test_check_db_and_table_class_exception(mock_class):
    instance = mock_class.return_value
    instance.checkDbAndTable.side_effect = tdclient.errors.AuthError('List databases failed: {"error":"Failed to Login"}')
    
    try:
        ArmQuery("10574/8fe2c7251368da13d33683b37fa382c87f8eb", 'https://api.treasuredata.com').checkDbAndTable('sample_datasets', "www_acc")
    except tdclient.errors.AuthError as e:
        assert str(e) == 'List databases failed: {"error":"Failed to Login"}'
