import json
import pandas as pd
from kgproject import config
from py2neo import Graph, Node
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
        self.id_transname = {} # 建立关系名称中文和id的对应关系
        self.entity_list = {}  # key为实体id，value为实体列表
        self.relations = []  # 实体类别之间的关系列表
        self.relation_dict = {}
        self.disease_attr = []
        self.disease_infos = []
        # key为关系名称id，value为实体实例关系列表 - [[disease1, drug1],[disease1, drug1]]
        self.relation_list = {}

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
        print(graph_info)
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
            self.id_relation[relation['lineId']] = relation['trans_name']
            self.relation_list[relation['lineId']] = []
        # keys = self.all_attr(filename)

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

    def create_relationship(self, start_node, end_node, edges, rel_type, trans_name):
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
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, trans_name)
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
            trans_name = self.id_transname[k]
            self.create_relationship(
                start_name, end_name, v, rel_type, trans_name)

