import subprocess
import json


def run_script(input_str):
    result = subprocess.run(['python', 'query_my_graph.py'], input=input_str.encode('utf-8'), capture_output=True,
                            check=True)
    return result.stdout.decode('utf-8').strip()


def test_query_my_graph():
    input_str = '{"queries": [{"paths": {"start": "a", "end": "e"}}, {"cheapest": {"start": "a", "end": "e"}}]}'

    expected_output = """
    {
      "answers": [
        {
          "paths": {
            "from": "a",
            "to": "e",
            "paths": [
              ["a", "b", "c", "d", "e"],
              ["a", "b", "e" ]
            ]
          }
        },
        {
          "cheapest": {
            "from": "a",
            "to": "e",
            "path": ["a", "b", "c", "d", "e"]
          }
        }
      ]
    }
    """.strip()

    output = run_script(input_str)
    assert json.loads(output) == json.loads(expected_output)


def run_my_graph_script():
    result = subprocess.run(['python', 'my_graph.py'], capture_output=True, check=True)
    return result.stdout.decode('utf-8').strip()


def test_my_graph_output():
    output = run_my_graph_script()
    # check that output contains the expected sctring: "Graph data from"
    assert "Graph data from" in output
    assert "loaded into the database successfully" in output
