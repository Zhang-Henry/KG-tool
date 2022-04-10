from django.http import HttpResponse
import json
import os
from django.views.decorators.csrf import csrf_exempt
import re
from . import config
from .models.neo_models import Neo4j
from .ner.ner import ner
# from .QA.chatbot_graph import handler
from .models.query_db import Query_db
from .Relation_entity.inference import *
import time

# 上传json文件，内容包括实体和关系
@csrf_exempt
def upload_json(request):
    response = {}
    if request.method == 'POST':
        req = request.FILES.get('file')
    # 上传文件类型过滤
        file_type = re.match(r'.*\.(json)', req.name)
        if not file_type:
            response['code'] = 2
            response['msg'] = '文件类型不匹配, 请重新上传'
            return HttpResponse(json.dumps(response))
        # 打开特定的文件进行二进制的写操作
        destination = open(
            os.path.join(config.BASE_IMPORT_URL, req.name), 'wb+')
        for chunk in req.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()
        response['msg'] = "Success"
        response['code'] = 200
    return HttpResponse(json.dumps(response), content_type="application/json")

# 返回json实体中所有的属性


@csrf_exempt
def attr(request, filename):
    neo4j = Neo4j()
    data_json = dict()
    data_json["attri"] = neo4j.all_attr(filename)
    # print(data_json)
    return HttpResponse(json.dumps(data_json), content_type="application/json")


num_progress = 0


@csrf_exempt
def create_graph(request, filename):
    neo4j = Neo4j()
    global num_progress
    if request.method == 'POST':
        # graph_info = request.POST.get("流程B")  # 获取前端创建的节点、关系信息
        num_progress = 0
        graph_info = json.loads(request.body)
        print(graph_info)
        neo4j.read_node(graph_info, filename)
        num_progress = 1
        neo4j.create_graphnodes()
        num_progress = 2
        neo4j.create_graphrels()
        num_progress = 3
        time.sleep(3)
        return HttpResponse("success")


@csrf_exempt
def get_progress(request):
    global num_progress
    if request.method == 'GET':
        return HttpResponse(num_progress, "success")

@csrf_exempt
def after_creation(request):  # 创建图谱后自动返回一个任意关系的查询
    query_db = Query_db()
    data = query_db.random_relation()
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def get_entity(request, entity_name):
    query_db = Query_db()
    info = query_db.query_entity(entity_name)
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def get_relation(request, relation_name):
    query_db = Query_db()
    data = query_db.query_relation(relation_name)
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def nerText(request):
    if request.method == "POST":
        text = request.body.decode("utf-8")
        print(text)
        content = ner(text)
        print(content)
    return HttpResponse(json.dumps(content, ensure_ascii=False), content_type="application/json")



@csrf_exempt
def get_answer(request):
    # if request.method == "POST":
    #     question = request.POST.get("question")
    #     print(question)
    #     # handler = ChatBotGraph()
    #     answer = handler.chat_main(question)
    #     print('KG AI:', answer)
    # return HttpResponse(answer, content_type="application/json")
    return HttpResponse("pass")


# 通过name属性查询一个node，以及和它有关的所有关系
@csrf_exempt
def search_item(request):
    if request.method == "POST":
        # name = request.POST.get("name")
        data = json.loads(request.body)
        # print(data)
        name = data['item']
        query_db = Query_db()
        info = query_db.query_node(name)
        print(info)
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def show_node_only(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        # name = request.POST.get("name")
        # label = request.POST.get("category")
        name = data['name']
        label = data['category']
        query_db = Query_db()
        info = query_db.query_node_only(name, label)
        print(info)
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def show_relation_only(request):
    if request.method == "POST":
        data = json.loads(request.body)
        source = data['source']
        target = data['target']
        # source = request.POST.get("source")
        # target = request.POST.get("target")
        query_db = Query_db()
        info = query_db.query_relation_only(source, target)
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def delete_node(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data['name']
        label = data['category']
        # name = request.POST.get("name")
        # label = request.POST.get("category")
        query_db = Query_db()
        query_db.delete_node(name, label)
        info = query_db.random_relation()
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def delete_relation(request):
    if request.method == "POST":
        data = json.loads(request.body)
        source = data['source']
        target = data['target']
        # source = request.POST.get("source")
        # target = request.POST.get("target")
        query_db = Query_db()
        query_db.delete_relation(source, target)
        info = query_db.random_relation()
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def relation_entity_extraction(request):
    if request.method == "POST":
        # text = request.POST.get("text")
        data = json.loads(request.body)
        text = data['text']
        print(text)
        entity_list = prediction(text)
        print(entity_list)
        relation_list = template_relation(entity_list, text)
        print(relation_list)
        data_list = get_json_data(relation_list)
        print(data_list)
        info = {
            'entity_list': entity_list,
            'relation_list': relation_list,
            'data_list': data_list
        }
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")



