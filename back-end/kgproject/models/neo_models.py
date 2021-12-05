import sys
sys.path.append("..")
import os
from py2neo import Graph, Node, Relationship, cypher, Path
from kgproject import config
import pandas as pd

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
        self.graph = Graph(config.neo4j_url, password=config.password)

    def saveEntity(self, file_name, pk):
        # the name of the uploaded file is the entity name
        # pk stands for the primary key(unique, constraint)
        file_path = os.path.join(config.BASE_IMPORT_URL, file_name)
        df = pd.read_csv(file_path)
        cols = ["_".join(col.split(' ')) for col in df.columns] # handle strings with blank spaces
        attributes = [col+':'+'line.'+col for col in cols]
        entity_type = file_name.split('.')[0]
        command1 = 'LOAD CSV WITH HEADERS FROM "file:///' + file_name + \
            '" AS line\nCREATE (p:' + entity_type + "{" + ",".join(
                attributes) + "})\n"
        # LOAD CSV WITH HEADERS  FROM "file:///hudong_pedia.csv" AS line
        # CREATE(p: HudongItem{title: line.title, image: line.image, detail: line.detail, url: line.url, openTypeList: line.openTypeList, baseInfoKeyList: line.baseInfoKeyList, baseInfoValueList: line.baseInfoValueList})
        self.graph.run(command1)
        print(command1)
        command2 = "CREATE CONSTRAINT ON (c:" + \
            entity_type + ") " + "ASSERT c." + pk + " IS UNIQUE\n"
        print(command2)
        self.graph.run(command2)

