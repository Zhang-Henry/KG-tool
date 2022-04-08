from kgproject import config
from py2neo import Graph,Node
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
    #   'properties' = {..},
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

    # 通过sql语句返回格式化的实体、关系数据
    # sql语句返回必须是 return n,m,r
    # n,m是节点，r是关系
    def format_relation(self, sql):
        data = []
        links = []
        all_entities, all_relations = self.query_labels_relations()
        results = self.graph.run(sql).to_data_frame() # 将py2neo的返回结果转换为data_frame的形式
        if results.size == 0:
            return []
        else:
            for r in results.itertuples():
                start, end = r[1], r[2]
                # 关系json
                links.append({
                    'target': end['name'],
                    'source': start['name'],
                    'name': r[3].__name__
                })
                # 给start node附属性
                n1, n2 = self.format_node(start), self.format_node(end)
                # 给end node附属性
                data.append(n1)
                data.append(n2)
            data = self.deleteDuplicate(data)  # 给实体去重
            info = {
                'data': data,
                'links': links,
                'entities': all_entities,
                'relations': all_relations
            }
            return info

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
        sql = "match (n)-[r:{}]-(m) return n,m,r limit 25".format(relation_name)
        info = self.format_relation(sql)
        return info

    # 去重
    def deleteDuplicate(self, li):
        temp_list = list(set([str(i) for i in li]))
        li = [eval(i) for i in temp_list]
        return li

    # 创建完图谱后返回第一个关系查询结果
    def random_relation(self):
        sql = "CALL db.relationshipTypes()"
        relations = self.graph.run(sql).data()
        relation_list = [r['relationshipType'] for r in relations]
        if len(relation_list) > 0:
            return self.query_relation(relation_list[0])

    # 通过name属性查询一个node，以及和它有关的所有关系
    def query_node(self, name):
        sql = 'match (n{{name:"{0}"}})-[r]-(m) return n,m,r'.format(name)
        info = self.format_relation(sql)
        return info

    # 查找单个节点
    def query_node_only(self, name, label):
        sql = 'match (n:{0}{{name:"{1}"}})-[r]-(m) return n,m,r'.format(label, name)
        info = self.format_relation(sql)
        return info

    # 查找单个关系
    def query_relation_only(self, source, target):
        sql = 'match (n{{name:"{0}"}})-[r]-(m{{name:"{1}"}}) return n,m,r'.format(
            source, target)
        info = self.format_relation(sql)
        return info

    # 删除单个节点，和他有关的关系
    def delete_node(self, name, label):
        sql1 = 'match (n:{0}{{name:"{1}"}})-[r]-() delete n,r'.format(label,name) #删除和节点有关的关系和节点本身
        sql2 = 'match (n:{0}{{name:"{1}"}}) delete n'.format(label,name) #删除没有关系的独立节点
        self.graph.run(sql1)
        self.graph.run(sql2)

    # 删除单个关系
    def delete_relation(self, source, target):
        sql = 'match (n{{name:"{0}"}})-[r]-(m{{name:"{1}"}}) delete r'.format(
            source, target)
        self.graph.run(sql)

    # 根据图谱名字，删除整个图谱
    def delete_graph(self, graph_name):
        sql1 = 'match (n{{graphName: "{0}"}})-[r{{graphName: "{0}"}}]-(m{{graphName: "{0}"}}) delete n,m,r'.format(graph_name)
        sql2 = 'match (n{{graphName:"{0}"}}) delete n'.format(graph_name)
        self.graph.run(sql1)
        self.graph.run(sql2)

    def select_graph(self, name):
        sql = 'match (n{{graphName: "{0}"}})-[r{{graphName: "{0}"}}]-(m{{graphName: "{0}"}}) return n,m,r limit 25'.format(name)
        info = self.format_relation(sql)
        return info