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

file_name = "Act.csv"
entity1, entity2 = "Person", "Film"
df1_pk, df2_pk = "name", "movie"
relation = "relation"
command = """LOAD CSV WITH HEADERS FROM "file:///{0}" AS line
MATCH(entity1: {1}{{{3}: line.{1}}}), (entity2: {2}{{{4}: line.{2}}})
CREATE(entity1)-[:RELATION {{type: line.{5}}}] -> (entity2)""".format(file_name, entity1,entity2,df1_pk,df2_pk,relation)
print(command)