# import sys
# sys.path.append("..")
# from models.neo_models import Neo4j

# command = """LOAD CSV WITH HEADERS FROM "file:///Film.csv" AS line
# CREATE (p:Film{movie:line.movie,box_office:line.box_office,release_time:line.release_time,director:line.director})
# """
# neo4j = Neo4j()
# neo4j.connectDB()
# neo4j.graph.run(command)
# command2 = """CREATE CONSTRAINT ON (c:Film) ASSERT c.movie IS UNIQUE"""
# neo4j.graph.run(command2)

# cols = ['a','b','c','d']
# attributes = [col+':'+'line.'+col for col in cols]
# command = ",".join(attributes)
# print(command)

# file_name = "Act.csv"
# entity1, entity2 = "Person", "Film"
# df1_pk, df2_pk = "name", "movie"
# relation = "relation"
# command = """LOAD CSV WITH HEADERS FROM "file:///{0}" AS line
# MATCH(entity1: {1}{{{3}: line.{1}}}), (entity2: {2}{{{4}: line.{2}}})
# CREATE(entity1)-[:RELATION {{type: line.{5}}}] -> (entity2)""".format(file_name, entity1,entity2,df1_pk,df2_pk,relation)
# print(command)
# import json

# from py2neo.data import Entity

# json_str = [{
#     "value": {
#         "birthday": "1984年8月8日",
#         "profession": "演员",
#         "nationality": "中国",
#         "_type": "Person",
#         "name": "褚河",
#         "_id": 119,
#         "relation": [
#             {
#                 "releaseTime": "1966年6月2日",
#                 "movie": "哥谭精英",
#                 "director": "安纯",
#                 "_type": "Film",
#                 "_id": 100,
#                 "boxOffice": "37.78亿",
#                 "relation.type": "主演"
#             }
#         ]
#     }
# },
#     {
#     "value": {
#         "profession": "演员、歌手、舞者、商人、赛车手",
#         "birthday": "1984年2月9日（农历甲子年正月初八）",
#         "nationality": "中国",
#         "_type": "Person",
#         "name": "顾咏",
#         "_id": 124,
#         "relation": [
#             {
#                 "releaseTime": "1966年6月2日",
#                 "movie": "哥谭精英",
#                 "director": "安纯",
#                 "_type": "Film",
#                 "_id": 100,
#                 "boxOffice": "37.78亿",
#                 "relation.type": "主演"
#             },
#             {
#                 "releaseTime": "1986年1月22日",
#                 "movie": "红颜知己",
#                 "director": "严娣",
#                 "_type": "Film",
#                 "_id": 0,
#                 "boxOffice": "34.15亿",
#                 "relation.type": "主演"
#             }
#         ]
#     }
# }]

# entitys = []
# relations = []
# for item in json_str:
#   entity = item['value']

