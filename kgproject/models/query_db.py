from kgproject import config
from py2neo import Graph, Node
import sys
sys.path.append("..")


class Query_db():
    graph = None

    def __init__(self):
        print("Creating neo4j class ...")
        self.graph = Graph(
            config.neo4j_url, password=config.password)
        print("The neo4j database connected successfully")

    def query_labels_relations(self):
        # return the whole knowledge graph info
        sql1 = "CALL db.labels()"
        sql2 = "CALL db.relationshipTypes()"
        entities = self.graph.run(sql1).data()
        relations = self.graph.run(sql2).data()
        # print(entities, relations)
        entity_list = [e['label'] for e in entities]
        relation_list = [r['relationshipType'] for r in relations]
        return entity_list, relation_list

    # format each node to a certain form
    # input: py2neo format node
    # return:
    # node = {
    #   'name'= 'xx',
    #   'properties' = 'xx',
    #   'category' = 'xx',
    #   'symolSize' = 80
    # }
    def format_node(self, e):
        node = {}
        node['name'] = e['name']
        node['category'] = list(e.labels)[0]
        e.pop('name')
        for k, v in e.items():
            if isinstance(v, list):
                e[k] = "; ".join(v)
        node['properties'] = e
        node['symolSize'] = 80
        return node

    # 查找指定标签实体,返回25条数据
    def query_entity(self, entity_name):
        info = {}
        all_entities, all_relations = self.query_labels_relations()
        sql = "MATCH (n:{0}) RETURN n LIMIT 25".format(entity_name)
        entitys = self.graph.run(sql).data()
        # print(entity)
        data = []
        for e in entitys:
            node = self.format_node(e['n'])
            data.append(node)
        info['data'], info['entities'], info['relations'] = data, all_entities, all_relations
        return info

    # 查找指定关系，使用py2neo接口查询
    def query_relation(self, relation_name):
        info = {}
        data = []
        links = []
        all_entities, all_relations = self.query_labels_relations()
        relations = self.graph.match(r_type=relation_name).limit(25)
        # print(len(relations))
        for r in relations:
            start, end = r.nodes[0], r.nodes[1]
            # 关系json
            link = {}
            link['target'], link['source'], link['name'] = end['name'], start['name'], relation_name
            links.append(link)
            # 给start node附属性
            n1, n2 = self.format_node(start), self.format_node(end)
            # 给end node附属性
            data.append(n1)
            data.append(n2)
        data = self.deleteDuplicate(data)  # 给实体去重
        info['data'], info['links'], info['entities'], info['relations'] = data, links, all_entities, all_relations
        return info

    def deleteDuplicate(self, li):
        temp_list = list(set([str(i) for i in li]))
        li = [eval(i) for i in temp_list]
        return li

    # 通过name属性查询一个node，以及和它有关的所有关系
    def query_node(self, name):
        info = {}
        all_entities, all_relations = self.query_labels_relations()
        sql = 'match (n{{name:"{0}"}})-[r]-(m) return *'.format(name)
        nodes = self.graph.run(sql).data()
        print(nodes[0])
        return nodes[0]
        if len(node) == 0:
            return []
        else:
            data = []
            for e in node:
                instance = {}
                node = e['n']
                instance['name'] = node['name']
                instance['category'] = list(node.labels)[0]
                instance['symolSize'] = 80
                property_info = dict(node)
                property_info.pop('name')
                for k, v in property_info.items():
                    if isinstance(v, list):
                        property_info[k] = "; ".join(v)
                instance['properties'] = property_info
                data.append(instance)
            info['data'] = data
            info['entities'] = [instance['category']]
            info['relations'] = []
            # print(info)
            return info
