import json
import sys

import networkx as nx
from app_config import dsn
from db_client import DatabaseClient


def create_graph_from_database(dsn):
    try:
        # Fetch nodes and edges from the database
        db_client = DatabaseClient(dsn)
        nodes = db_client.get_nodes()
        edges = db_client.get_edges()
        db_client.close()

        graph = nx.DiGraph()
        # Add nodes and edges to the graph
        graph.add_nodes_from(nodes)
        for edge in edges:
            from_node, to_node, cost = edge
            graph.add_edge(from_node, to_node, weight=cost)

        return graph
    except Exception as e:
        print("An error occurred:", e)

# Trace the Path in Depth-First Search (recursive)
def find_dfs_paths(graph, start, end):
    paths = []
    def dfs(current_node, path):
        if current_node == end:
            paths.append(path)
        else:
            for neighbor in graph.successors(current_node):
                if neighbor not in path:
                    dfs(neighbor, path + [neighbor])

    dfs(start, [start])
    return paths


# Trace the Path in Depth-First Search (Iterative)
def find_dfs_paths_iterative(graph, start, end):
    paths = []
    stack = [(start, [start])]

    while stack:
        current_node, path = stack.pop()

        if current_node == end:
            paths.append(path)
        else:
            for neighbor in graph.successors(current_node):
                if neighbor not in path:
                    stack.append((neighbor, path + [neighbor]))

    return paths

# Tracing the Path in Breadth-First Search
def find_bfs_paths(graph, start, end):
    paths = []
    queue = [(start, [start])]

    while queue:
        current_node, path = queue.pop(0)

        if current_node == end:
            paths.append(path)
        else:
            for neighbor in graph.neighbors(current_node):
                if neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

    return paths

def find_all_paths(graph, start, end):
    all_paths = list(nx.all_simple_paths(graph, source=start, target=end))
    return all_paths

def find_cheapest_path(graph, start, end):
    try:
        path = nx.dijkstra_path(graph, start, end)
        return path
    except nx.NetworkXNoPath:
        return None



def process_queries(queries, graph):
    try:
        answers = []

        for query in queries:
            if "paths" in query:
                start = query["paths"]["start"]
                end = query["paths"]["end"]
                paths = find_all_paths(graph, start, end)
                answers.append({"paths": {"from": start, "to": end, "paths": paths}})
            if "cheapest" in query:
                start = query["cheapest"]["start"]
                end = query["cheapest"]["end"]
                cheapest_path = find_cheapest_path(graph, start, end)
                answers.append({"cheapest": {"from": start, "to": end, "path": cheapest_path or False}})

        result = {"answers": answers}
        return result
    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":

    graph = create_graph_from_database(dsn)

    try:
        input_data = json.load(sys.stdin)
        queries = input_data.get("queries", [])
        result = process_queries(queries, graph)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError:
        print("Invalid JSON input.")
