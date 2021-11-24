from py2neo import Graph, Node, Relationship, cypher, Path
import neo4j


# def createNodeDemo(self):
#     a = Node('Person', name='Alice')
#     b = Node('Person', name='Bob')
#     r = Relationship(a, 'KNOWS', b)
#     a['age'] = 20
#     b['age'] = 21
#     r['time'] = '2017/08/31'
#     self.graph.create(a)
#     self.graph.create(b)
#     self.graph.create(r)

# def CQL(self):
#   data = this.graph.run('MATCH (p:Person) return p').data
#   print(data)

class Neo4j():
    graph = None

    def __init__(self):
        print("create neo4j class ...")

    def connectDB(self):
        self.graph = Graph("http://localhost:7474/db/data/", password="123456")
