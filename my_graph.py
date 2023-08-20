from lxml import etree
import psycopg2
import networkx as nx
import matplotlib.pyplot as plt
import sys

import app_config


def validate_xml_with_xsd(xml_path, xsd_path):
    try:
        # Load the XSD schema
        xsd_tree = etree.parse(xsd_path)
        xsd_schema = etree.XMLSchema(xsd_tree)

        # Load the XML file to validate
        xml_tree = etree.parse(xml_path)

        if xsd_schema.validate(xml_tree):
            print("XML is valid against the XSD schema.")
        else:
            print("XML is not valid against the XSD schema.")
            for error in xsd_schema.error_log:
                print(error)
            return False
    except Exception as e:
        print("An error occurred:", e)
        return False

    return True


def is_valid_graph(xml_data):
    try:
        parser = etree.XMLParser()
        tree = etree.parse(xml_data, parser)
        root = tree.getroot()

        # Ensure there's <id> and <name> for the <graph>
        if root.find("id") is None or root.find("name") is None:
            return False, "Graph must have <id> and <name>."

        nodes = root.find("nodes")
        edges = root.find("edges")

        # Ensure there's at least one <node>
        if not nodes or len(nodes.findall("node")) < 1:
            return False, "<nodes> group must contain at least one <node>."

        # Check all nodes have unique IDs
        node_ids = {node.find("id").text for node in nodes.findall("node")}
        if len(node_ids) != len(nodes.findall("node")):
            return False, "All <node> elements must have unique <id> tags."

        # For each <edge> validate <from>, <to>, and <cost>
        for edge in edges.findall("edge"):
            from_node = edge.find("from").text
            to_node = edge.find("to").text

            if from_node not in node_ids or to_node not in node_ids:
                return False, "Each <edge> must have <from> and <to> corresponding to previously defined nodes."

            cost = edge.find("cost")
            if cost is not None:
                try:
                    cost_value = float(cost.text)
                    if cost_value < 0:
                        return False, "<cost> should be a non-negative floating point."
                except ValueError:
                    return False, "<cost> should be a floating point or integer value."

        return True, "The graph XML is valid."

    except etree.XMLSyntaxError:
        return False, "Invalid XML syntax."

    except Exception as e:
        return False, str(e)


def load_into_database(xml_path, db_connection):
    try:
        tree = etree.parse(xml_path)
        root = tree.getroot()

        nodes = root.findall("./nodes/node")
        edges = root.findall("./edges/edge")

        conn = psycopg2.connect(**db_connection)
        cur = conn.cursor()

        for node_elem in nodes:
            node_id = node_elem.find('id').text
            node_name = node_elem.find('name').text
            cur.execute("SELECT * FROM nodes WHERE id = %s", (node_id,))
            existing_node = cur.fetchone()

            if existing_node:
                cur.execute("UPDATE nodes SET name = %s WHERE id = %s", (node_name, node_id))
                print(f"Node {node_id} updated in the database.")
            else:
                cur.execute("INSERT INTO nodes (id, name) VALUES (%s, %s)", (node_id, node_name))
                print(f"Node {node_id} added to the database.")

        for edge_elem in edges:
            edge_id = edge_elem.find('id').text
            from_node = edge_elem.find('from').text
            to_node = edge_elem.find('to').text
            cost = float(edge_elem.find('cost').text)

            cur.execute("SELECT * FROM edges WHERE id = %s", (edge_id,))
            existing_edge = cur.fetchone()

            if existing_edge:
                cur.execute("UPDATE edges SET from_node = %s, to_node = %s, cost = %s WHERE id = %s",
                            (from_node, to_node, cost, edge_id))
                print(f"Edge {edge_id} updated in the database.")
            else:
                cur.execute("INSERT INTO edges (id, from_node, to_node, cost) VALUES (%s, %s, %s, %s)",
                            (edge_id, from_node, to_node, cost))
                print(f"Edge {edge_id} added to the database.")

        conn.commit()
        print(f"Graph data from: {xml_path}, loaded into the database successfully.")

        cur.close()
        conn.close()
    except Exception as e:
        print("An error occurred:", e)


def find_cycles_and_save_visualization(db_connection, output_file):
    try:
        conn = psycopg2.connect(**db_connection)
        cur = conn.cursor()

        # Load nodes and edges from the database
        nodes_query = "SELECT id FROM nodes"
        edges_query = "SELECT from_node, to_node, cost FROM edges"
        cur.execute(nodes_query)
        nodes = [row[0] for row in cur.fetchall()]
        cur.execute(edges_query)
        edges = [(row[0], row[1], {'weight': row[2]}) for row in cur.fetchall()]

        cur.close()
        conn.close()

        # Create a directed graph using NetworkX
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)

        # Find cycles using NetworkX
        cycles = list(nx.simple_cycles(graph))
        print(cycles)
        # cycles = [['g'], ['d', 'e', 'a', 'b', 'c'], ['b', 'e', 'a'], ['h', 'j']]
        # flatten the list of lists
        flat_cycles = [item for sublist in cycles for item in sublist]

        # Color nodes based on cycles
        node_colors = ['red' if node in flat_cycles else 'skyblue' for node in graph.nodes()]

        # Visualize the graph using Matplotlib
        pos = nx.circular_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color=node_colors, font_weight='bold', node_size=500, font_size=10,
                width=1.0)

        # # Color the last edge of each cycle red
        for cycle in cycles:
            for i in range(len(cycle)):
                if i < len(cycle) - 1:
                    nx.draw_networkx_edges(graph, pos, edgelist=[(cycle[i], cycle[i + 1])], edge_color='blue',
                                           node_size=500, width=1.0)
                else:
                    nx.draw_networkx_edges(graph, pos, edgelist=[(cycle[-1], cycle[0])], edge_color='red',
                                           node_size=500, arrowsize=15)

        # draw weighted edges on the graph
        nx.draw_networkx_edge_labels(graph, pos,
                                     edge_labels={(u, v): d['weight'] for u, v, d in graph.edges(data=True)})

        # Save the plot as a PNG image
        plt.savefig(output_file)
        print("Graph visualization saved as", output_file)

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    xml_schema = app_config.xml_schema
    xml_document = app_config.xml_document
    db_connection = app_config.db_connection

    # 1) Validate the XML document against the XSD schema
    if not validate_xml_with_xsd(xml_document, xml_schema):
        sys.exit(1)

    # 1.1) 2nd way to validate xml file using python
    #if not is_valid_graph(xml_document):
    #    sys.exit(1)

    # 2) Load the XML document into the database
    load_into_database(xml_document, db_connection)

    # 3) Find cycles in the graph and render a visualization
    find_cycles_and_save_visualization(db_connection, app_config.png_image)
