from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render  # 渲染模板
from django.shortcuts import redirect  # 重定向
from django.urls import reverse  # 反向解析
from django.views import View  # 视图类需要
from django.http import JsonResponse  # 相应json数据
import json
import os
from django.views.decorators.csrf import csrf_exempt
import re
from . import config
from .models.neo_models import Neo4j
from .ner.ner import ner
from  .QA.chatbot_graph import ChatBotGraph

@csrf_exempt
def upload_entity(request):
    response = {}
    try:
        if request.method == 'POST':
            req = request.FILES.get('file')
            #  上传文件类型过滤
            file_type = re.match(r'.*\.(csv|xlsx|xls)', req.name)
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

            neo4j = Neo4j()
            neo4j.saveEntity(req.name)  # save entity to neo4j

            response['msg'] = "Success"
            response['code'] = 200
    except Exception as e:
        response['msg'] = '服务器内部错误'
        response['code'] = 1
    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
def upload_relation(request):
    response = {}
    try:
        if request.method == 'POST':
            req = request.FILES.get('file')

            #  上传文件类型过滤
            file_type = re.match(r'.*\.(csv|xlsx|xls)', req.name)
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
            neo4j = Neo4j()
            neo4j.saveRelation(req.name)  # save entity to neo4j
    except Exception as e:
        response['msg'] = '服务器内部错误'
        response['code'] = 1
    return HttpResponse(json.dumps(response), content_type="application/json")


@csrf_exempt
def return_kg(request):
    neo4j = Neo4j()
    kg_data = neo4j.query_all_nodes_relations_labels()  # save entity to neo4j
    return JsonResponse(kg_data, safe=False)

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


@csrf_exempt
def create_graph(request, filename):
    neo4j = Neo4j()
    if request.method == 'POST':
        # graph_info = request.POST.get("流程B")  # 获取前端创建的节点、关系信息
        graph_info = json.loads(request.body)
        print(graph_info)
        neo4j.read_node(graph_info, filename)
        neo4j.create_graphnodes()
        neo4j.create_graphrels()
        return HttpResponse("success")


@csrf_exempt
def after_creation(request):  # 创建图谱后自动返回一个任意关系的查询
    neo4j = Neo4j()
    data = neo4j.random_relation()
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def get_entity(request, entity_name):
    neo4j = Neo4j()
    info = neo4j.query_entity(entity_name)
    return HttpResponse(json.dumps(info, ensure_ascii=False), content_type="application/json")


@csrf_exempt
def get_relation(request, relation_name):
    neo4j = Neo4j()
    data = neo4j.query_relation(relation_name)
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
    if request.method == "POST":
        question = request.POST.get("question")
        handler = ChatBotGraph()
        answer = handler.chat_main(question)
        print('KG AI:', answer)
    return HttpResponse(answer, content_type="application/json")



