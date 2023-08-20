import pytest
from query_my_graph import (
    process_queries,
    find_dfs_paths,
    find_bfs_paths,
    find_dfs_paths_iterative,
)
import networkx as nx

@pytest.fixture
def nodes():
    return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k','l','m','n']

@pytest.fixture
def edges():
    edges = [
        ('a', 'b', 0.5),
        ('b', 'c', 10.0),
        ('b', 'e', 42.0),
        ('c', 'd', 5.0),
        ('d', 'e', 0.8),
        ('e', 'a', 0.42),
        ('e', 'f', 1.0),
        ('e', 'h', 0.53),
        ('g', 'g', 0.5),
        ('h', 'j', 0.5),
        ('j', 'h', 0.5),
        ('a', 'k', 6),
        #('g', 'a', 13),
        ('k', 'l', 7),
        ('l', 'm', 8),
        ('m', 'n', 9),
    ]
    return edges

@pytest.fixture
def graph(nodes, edges):
    """
    Create a graph with 9 nodes and 11 edges
    :return:
    """

    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    for edge in edges:
        from_node, to_node, cost = edge
        graph.add_edge(from_node, to_node, weight=cost)
    return graph

# skip the test
@pytest.mark.skip
def test_save_graph(nodes, edges):
    from lxml import etree

    # Create the root element
    root = etree.Element("graph")

    # Add id and name to the root
    etree.SubElement(root, "id").text = "g0"
    etree.SubElement(root, "name").text = "The Graph Name"

    # Add nodes to the root
    nodes_element = etree.SubElement(root, "nodes")
    for node in nodes:
        node_element = etree.SubElement(nodes_element, "node")
        etree.SubElement(node_element, "id").text = node
        etree.SubElement(node_element,
                         "name").text = node.upper() + " name"  # Assuming the name is the uppercase version of the id

    # Add edges to the root
    edges_element = etree.SubElement(root, "edges")
    for idx, (start, end, cost) in enumerate(edges, 1):
        edge_element = etree.SubElement(edges_element, "edge")  # Note: changed from 'node' to 'edge' for clarity
        etree.SubElement(edge_element, "id").text = f"e{idx}"
        etree.SubElement(edge_element, "from").text = start
        etree.SubElement(edge_element, "to").text = end
        etree.SubElement(edge_element, "cost").text = str(cost)

    # Serialize the XML structure to a string
    xml_str = etree.tostring(root, pretty_print=True, encoding="utf-8").decode("utf-8")
    print(xml_str)

    #Save the XML to a file
    with open("graph.xml", "w") as file:
        file.write(xml_str)


def test_create_graph(graph):
    assert graph is not None
    assert len(graph) > 0

def test_process_queries_short_path(graph):
    input_data = {
        "queries": [
            {
                "paths": {
                    "start": "a",
                    "end": "e"
                }
            },
            {
                "cheapest": {
                    "start": "a",
                    "end": "e"
                }
            }
        ]
    }
    
    expected_output = {
        "answers": [
            {
                "paths": {
                    "from": "a",
                    "to": "e",
                    "paths": [['a', 'b', 'c', 'd', 'e'], ['a', 'b', 'e']],
                }
            },
            {
                "cheapest": {
                    "from": "a",
                    "to": "e",
                    "path": ['a', 'b', 'c', 'd', 'e']
                }
            }
        ]
    }
    
    actual_output = process_queries(input_data["queries"], graph)
    
    assert actual_output == expected_output

def test_process_queries_no_path(graph):
    input_data = {
        "queries": [
            {
                "paths": {
                    "start": "f",
                    "end": "g"
                }
            },
            {
                "cheapest": {
                    "start": "f",
                    "end": "g"
                }
            }
        ]
    }

    expected_output = {
        "answers": [
            {
                "paths": {
                    "from": "f",
                    "to": "g",
                    "paths": [],
                }
            },
            {
                "cheapest": {
                    "from": "f",
                    "to": "g",
                    "path": False
                }
            }
        ]
    }

    actual_output = process_queries(input_data["queries"], graph)

    assert actual_output == expected_output

def test_process_queries_non_direct_path(graph):
    input_data = {
        "queries": [
            {
                "paths": {
                    "start": "f",
                    "end": "j"
                }
            },
            {
                "cheapest": {
                    "start": "f",
                    "end": "j"
                }
            }
        ]
    }

    expected_output = {
        "answers": [
            {
                "paths": {
                    "from": "f",
                    "to": "j",
                    "paths": [],
                }
            },
            {
                "cheapest": {
                    "from": "f",
                    "to": "j",
                    "path": False
                }
            }
        ]
    }

    actual_output = process_queries(input_data["queries"], graph)

    assert actual_output == expected_output

def test_process_queries_multi_path(graph):
    input_data = {
        "queries": [
            {
                "paths": {
                    "start": "b",
                    "end": "a"
                }
            },
            {
                "paths": {
                    "start": "h",
                    "end": "a"
                }
            }
        ]
    }

    expected_output = {
        "answers": [
            {
                "paths": {
                    "from": "b",
                    "to": "a",
                    "paths": [['b', 'c', 'd', 'e', 'a'], ['b', 'e', 'a'] ],
                }
            },
            {
                "paths": {
                    "from": "h",
                    "to": "a",
                    "paths": []
                }
            }
        ]
    }

    actual_output = process_queries(input_data["queries"], graph)

    assert actual_output == expected_output

def test_process_queries_multi_cheapest_path(graph):
    input_data = {
        "queries": [
            {
                "cheapest": {
                    "start": "b",
                    "end": "a"
                }
            },
            {
                "cheapest": {
                    "start": "h",
                    "end": "a"
                }
            }
        ]
    }

    expected_output = {
        "answers": [
            {
                "cheapest": {
                    "from": "b",
                    "to": "a",
                    "path": ['b', 'c', 'd', 'e', 'a']
                }
            },
            {
                "cheapest": {
                    "from": "h",
                    "to": "a",
                    "path": False
                }
            }
        ]
    }

    actual_output = process_queries(input_data["queries"], graph)

    assert actual_output == expected_output

def test_find_dfs_paths(graph, start='a', end='e'):
    paths = find_dfs_paths(graph, start, end)
    assert paths == [['a', 'b', 'c', 'd', 'e'], ['a', 'b', 'e']]

def test_find_dfs_paths_iterative(graph, start='a', end='e'):
    paths = find_dfs_paths_iterative(graph, start, end)
    assert paths == [['a', 'b', 'e'], ['a', 'b', 'c', 'd', 'e']]

def test_find_bfs_paths(graph, start='a', end='e'):
    paths = find_bfs_paths(graph, start, end)
    assert paths == [['a', 'b', 'e'], ['a', 'b', 'c', 'd', 'e']]

def test_manual_dijkstra(nodes, edges, start='a', end='e'):
    graph = {node: [] for node in nodes}
    for u, v, w in edges:
        graph[u].append((v, w))

    def dijkstra(graph, start):
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        predecessors = {node: None for node in graph}
        priority_queue = [(0, start)]

        while priority_queue:
            current_distance, current_vertex = priority_queue.pop(0)

            if current_distance > distances[current_vertex]:
                continue

            for neighbor, weight in graph[current_vertex]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    predecessors[neighbor] = current_vertex

                    priority_queue.append((distance, neighbor))

        return distances, predecessors

    def restore_shortest_path(predecessors, start, end):
        path = [end]
        while path[-1] != start:
            path.append(predecessors[path[-1]])
        path.reverse()
        return path

    start_vertex = start
    distances, predecessors = dijkstra(graph, start_vertex)

    path = restore_shortest_path(predecessors, start_vertex, end)
    print(f"Shortest path from '{start}' to '{end}':", path)

    assert path == ['a', 'b', 'c', 'd', 'e']