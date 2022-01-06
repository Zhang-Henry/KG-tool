import json
from logging import error
from random import SystemRandom
import pandas as pd
from kgproject import config
from py2neo import Graph, Node, RelationshipMatcher
import os
import sys
sys.path.append("..")


class Neo4j():
    graph = None

    def __init__(self):
        print("Creating neo4j class ...")
        self.graph = Graph(
            config.neo4j_url, password=config.password)
        print("The neo4j database connected successfully")
        self.id_name = {}  # 建立实体name和id的对应关系
        self.id_relation = {}  # 建立relation和id的对应关系
        self.entity_list = {}  # key为实体id，value为实体列表
        self.relations = []  # 实体类别之间的关系列表
        self.relation_dict = {}
        self.disease_attr = []
        self.disease_infos = []
        # key为关系名称id，value为实体实例关系列表 - [[disease1, drug1],[disease1, drug1]]
        self.relation_list = {}

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

    def all_attr(self, filename):
        path = os.path.join(config.BASE_IMPORT_URL, filename) + ".json"
        keys = []
        for data in open(path, encoding="utf-8"):
            data_dict = json.loads(data)
            for key in data_dict.keys():
                if key not in keys:
                    keys.append(key)
        return keys

    def remove_duplicates(self):
        for k, v in self.entity_list.items():
            self.entity_list[k] = set(v)

    def read_node(self, graph_info, filename):
        # 初始化entity和relation的list
        for node in graph_info['nodeList']:
            self.id_name[node['id']] = node['name']
            if node['name'] == 'Disease':
                self.disease_attr = node['attribute']
                continue
            self.entity_list[node['id']] = []
        for relation in graph_info['lineList']:
            if relation == {}:
                continue
            self.relations.append(relation)
            self.relation_dict[relation['lineId']] = relation
            self.id_relation[relation['lineId']] = relation['label']
            self.relation_list[relation['lineId']] = []
        keys = self.all_attr(filename)

        # 读取json文件数据
        path = os.path.join(config.BASE_IMPORT_URL, filename) + ".json"
        cnt = 0
        for data in open(path, encoding="utf-8"):
            # 枚举每个实体
            disease_dict = {}  # 保存disease的属性
            data_dict = json.loads(data)
            cnt += 1
            print(cnt)
            disease = data_dict['name']  # 疾病名字
            for attr in self.disease_attr:
                if attr in data_dict:
                    disease_dict[attr] = data_dict[attr]
                else:
                    disease_dict[attr] = ""
            disease_dict['name'] = data_dict['name']
            self.disease_infos.append(disease_dict)
            for relation in self.relations:
                if relation['label'] in data_dict:
                    node_id = relation['to']  # 关系箭头的指向方为实体
                    # 将关系名称与实体名字对应,extend在原列表的基础上增加新的list内容
                    self.entity_list[node_id].extend(
                        data_dict[relation['label']])
                    for item in data_dict[relation['label']]:
                        pair = [disease, item]
                        self.relation_list[relation['lineId']].append(pair)
        # print(self.relation_list)
        # print(self.entity_list)

    '''建立节点'''

    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.graph.create(node)
            count += 1
            print("正在生成实体节点：", node_name, count, len(nodes))
        return

    '''创建实体关联边'''

    def create_relationship(self, start_node, end_node, edges, rel_type):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s]->(q)" % (
                start_node, end_node, p, q, rel_type)
            try:
                self.graph.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''创建知识图谱中心疾病的节点'''

    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'])
            disease_dict.pop('name')
            # print(disease_dict)
            node.update(disease_dict)
            self.graph.create(node)
            count += 1
            print("正在生成disease节点：", count)
        return

    def create_graphnodes(self):
        self.create_diseases_nodes(self.disease_infos)
        self.remove_duplicates()
        for k, v in self.entity_list.items():
            self.create_node(self.id_name[k], v)

    def create_graphrels(self):
        for k, v in self.relation_list.items():
            start_id = self.relation_dict[k]['from']
            start_name = self.id_name[start_id]
            end_id = self.relation_dict[k]['to']
            end_name = self.id_name[end_id]
            rel_type = self.id_relation[k]
            self.create_relationship(start_name, end_name, v, rel_type)


    def deleteDuplicate(self, li):
        temp_list = list(set([str(i) for i in li]))
        li = [eval(i) for i in temp_list]
        return li

    def query_labels_relations(self):
        # return the whole knowledge graph info
        sql1 = "CALL db.labels()"
        sql2 = "CALL db.relationshipTypes()"
        entitys = self.graph.run(sql1).data()
        relations = self.graph.run(sql2).data()
        # print(entitys, relations)
        entity_list = [e['label'] for e in entitys]
        relation_list = [r['relationshipType'] for r in relations]
        return entity_list, relation_list

    def query_entity(self, entity_name):
        info = {}
        entitys, relations = self.query_labels_relations()
        sql = "MATCH (n:{0}) RETURN n LIMIT 25".format(entity_name)
        entity = self.graph.run(sql).data()
        # print(entity)
        data = []
        for e in entity:
            instance = {}
            instance['name'] = e['n']['name']
            e['n'].pop('name')
            for k, v in e['n'].items():
                if isinstance(v, list):
                    e['n'][k] = "; ".join(v)
            instance['properties'] = e['n']
            instance['category'] = entity_name
            instance['symolSize'] = 80
            data.append(instance)
        info['data'] = data
        info['entitys'] = entitys
        info['relations'] = relations
        return info

    def query_relation(self, relation_name):
        info = {}
        data = []
        links = []
        all_entitys, all_relations = self.query_labels_relations()
        relations = self.graph.match(r_type=relation_name)
        for r in relations:
            start = r.nodes[0]
            end = r.nodes[1]

            #给start node附属性
            n1 = {}
            n1['name'] = start['name']
            n1['category'] = list(start.labels)[0]
            n1['symolSize'] = 80
            property_info = dict(start)
            property_info.pop('name')
            for k, v in property_info.items():
                if isinstance(v, list):
                    property_info[k] = "; ".join(v)
            n1['properties'] = property_info

            #给end node附属性
            n2 = {}
            n2['name'] = end['name']
            n2['category'] = list(end.labels)[0]
            n2['symolSize'] = 80
            property_info = dict(end)
            property_info.pop('name')
            for k, v in property_info.items():
                if isinstance(v, list):
                    property_info[k] = "; ".join(v)
            n2['properties'] = property_info
            data.append(n1)
            data.append(n2)

            #关系json
            link = {}
            link['target'] = end['name']
            link['source'] = start['name']
            link['name'] = relation_name
            links.append(link)

        info['data'] = data
        self.deleteDuplicate(data) #给实体去重
        info['links'] = links
        info['entitys'] = all_entitys
        info['relations'] = all_relations
        return info
