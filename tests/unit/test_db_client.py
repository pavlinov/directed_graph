import pytest
from unittest.mock import Mock, patch
from db_client import DatabaseClient, Node, Edge

@pytest.fixture
def mock_session():
    return Mock()

@pytest.fixture
def mock_session_query(mock_session):
    return Mock()

@patch('db_client.create_engine', Mock())
def test_get_nodes(mock_session_query, mock_session):
    mock_session.query.return_value = mock_session_query
    mock_session_query.all.return_value = [
        Node(id='x', name='X name'),
        Node(id='y', name='Y name'),
        Node(id='z', name='Z name'),
    ]

    db_client = DatabaseClient(db_connection='dummy_dsn')
    db_client.session = mock_session

    nodes = db_client.get_nodes()

    assert len(nodes) == 3
    assert ['x', 'y', 'z'] == nodes


@patch('db_client.create_engine', Mock())
def test_get_edges(mock_session_query, mock_session):
    mock_session.query.return_value = mock_session_query
    mock_session_query.all.return_value = [
        Edge(id='e1', from_node='x', to_node='y', cost=5.0),
        Edge(id='e2', from_node='y', to_node='z', cost=0.8),
        Edge(id='e3', from_node='z', to_node='x', cost=0.42),
    ]

    db_client = DatabaseClient(db_connection='dummy_dsn')
    db_client.session = mock_session

    edges = db_client.get_edges()

    assert len(edges) == 3
    assert [('x', 'y', 5.0), ('y', 'z', 0.8), ('z', 'x', 0.42)] == edges
