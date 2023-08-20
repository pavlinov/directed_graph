from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    from_node = Column(Integer, ForeignKey('nodes.id'))
    to_node = Column(Integer, ForeignKey('nodes.id'))
    cost = Column(Float)

class DatabaseClient:
    def __init__(self, db_connection):
        self.engine = create_engine(db_connection)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_nodes(self, nodes):
        for node_data in nodes:
            node = Node(id=node_data[0], name=node_data[0])
            self.session.add(node)
        self.session.commit()

    def save_edges(self, edges):
        for edge_data in edges:
            edge = Edge(id=edge_data['id'], from_node=edge_data['from_node'], to_node=edge_data['to_node'], cost=edge_data['cost'])
            self.session.add(edge)
        self.session.commit()


    def get_nodes(self):
        results = self.session.query(Node).all()
        nodes = []
        for result in results:
            nodes.append(result.id)
        return nodes

    def get_edges(self):
        results = self.session.query(Edge).all()
        edges = []
        for result in results:
            edges.append((result.from_node, result.to_node, result.cost))
        return edges

    def close(self):
        self.session.close()
