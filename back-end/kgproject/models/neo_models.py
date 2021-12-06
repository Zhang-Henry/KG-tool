import pandas as pd
from kgproject import config
from py2neo import Graph, GraphService
import os
import sys

from py2neo.data import Entity
sys.path.append("..")


class Neo4j():
    graph = None

    def __init__(self):
        print("Creating neo4j class ...")
        self.graph = Graph(config.neo4j_url, password=config.password)
        print("The neo4j database connected successfully")

    def saveEntity(self, file_name):
        # the name of the uploaded file is the entity name
        # pk stands for the primary key(unique, constraint)
        file_path = os.path.join(config.BASE_IMPORT_URL, file_name)
        df = pd.read_csv(file_path)
        # cols = ["_".join(col.split(' ')) for col in df.columns] # handle strings with blank spaces
        pk = df.columns[0]
        attributes = [col+':'+'line.'+col for col in df.columns]
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

    def saveRelation(self, file_name):
        file_path = os.path.join(config.BASE_IMPORT_URL, file_name)
        df = pd.read_csv(file_path)
        entity1, relation, entity2 = df.columns[0], df.columns[1], df.columns[2]
        entity1_filepath = os.path.join(config.BASE_IMPORT_URL, entity1+".csv")
        entity2_filepath = os.path.join(config.BASE_IMPORT_URL, entity2+".csv")
        df1 = pd.read_csv(entity1_filepath)
        df2 = pd.read_csv(entity2_filepath)
        df1_pk, df2_pk = df1.columns[0], df2.columns[0]
        command = """LOAD CSV WITH HEADERS FROM "file:///{0}" AS line
        MATCH(entity1: {1}{{{3}: line.{1}}}), (entity2: {2}{{{4}: line.{2}}})
        CREATE(entity1)-[:RELATION {{type: line.{5}}}] -> (entity2)""".format(file_name, entity1, entity2, df1_pk, df2_pk, relation)
        print(command)
        self.graph.run(command)

    def query_all_nodes_relations_labels(self):
        # command = """MATCH p=()-[r:RELATION]->()
        # WITH COLLECT(p) AS ps
        # CALL apoc.convert.toTree(ps) yield value
        # RETURN value"""
        # command2 = """CALL apoc.schema.nodes()
        # YIELD name, label, properties, status, type"""
        command1 = "CALL apoc.schema.nodes()"
        schema = self.graph.run(command1).data()
        all_info = {}
        entitys = []
        links = []
        pks = []
        labels = []
        for entity in schema:
            label = entity['label']
            pk = entity['properties'][0]
            pks.append(pk)
            command = """CALL apoc.search.nodeAll('{{{0}:"{1}"}}','contains','') YIELD node AS n RETURN n""".format(
                label, pk)
            data = self.graph.run(command).data()
            for p in data:
                entity_new = {}
                entity_new['name'] = p['n'][pk]
                properties = []
                for k, v in p['n'].items():
                    if k != pk:
                        properties.append(str(k) + ": " + str(v))
                des = ", ".join(properties)
                entity_new['des'] = des
                entity_new['category'] = label
                entitys.append(entity_new)
        all_info['data'] = entitys

        command2 = "MATCH (n)-[r]-(m) RETURN *;"
        relations = self.graph.run(command2).data()
        for relation in relations:
            relation_new = {}
            for k, v in relation['m'].items():
                if k in pks:
                    relation_new['source'] = v
            for k, v in relation['n'].items():
                if k in pks:
                    relation_new['target'] = v
            relation_new['name'] = relation['r']['type']
            links.append(relation_new)
        all_info['links'] = links

        command3 = "match (n) return distinct labels(n)"
        label_data = self.graph.run(command3).data()
        for data in label_data:
            labels.append(data['labels(n)'][0])
        all_info['labels'] = labels

        # with open("data.json",'w+') as f:
        #     f.write(str(all_info))
        return all_info
