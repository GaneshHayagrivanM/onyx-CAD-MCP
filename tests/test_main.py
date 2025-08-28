import pytest
from src.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """Test the index route."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert rv.get_json() == {"message": "AutoCAD MCP Server is running."}

def test_connect_to_autocad(client):
    """Test the connect_to_autocad route."""
    rv = client.post('/connect_to_autocad', json={"instance_id": "acad-1"})
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["message"] == "Successfully connected to AutoCAD instance acad-1"
    assert json_data["instance_id"] == "acad-1"

def test_execute_lisp(client):
    """Test the execute_lisp route."""
    client.post('/connect_to_autocad', json={"instance_id": "acad-1"})
    rv = client.post('/execute_lisp', json={"instance_id": "acad-1", "lisp_code": "(command)"})
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["message"] == "LISP code executed successfully"
    assert json_data["executed_code"] == "(command)"

def test_create_wall(client):
    """Test the create_wall route."""
    client.post('/connect_to_autocad', json={"instance_id": "acad-1"})
    wall_data = {
        "instance_id": "acad-1",
        "start_point": [0, 0],
        "end_point": [10, 0],
        "thickness": 0.2
    }
    rv = client.post('/create_wall', json=wall_data)
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data["message"] == "Wall created successfully"
    assert 'lisp_code' in json_data
    assert json_data["lisp_code"] == '(command "_PLINE" "0,0" "W" "0.2" "0.2" "10,0" "")'
