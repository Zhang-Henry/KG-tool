from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render  # 渲染模板
from django.shortcuts import redirect  # 重定向
from django.urls import reverse  # 反向解析
from django.views import View  # 视图类需要
from django.http import JsonResponse  # 相应json数据
from datetime import datetime
import json
import os
from django.views.decorators.csrf import csrf_exempt
import time
import uuid
import re
from . import config
from .models.neo_models import Neo4j


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
            neo4j.saveEntity(req.name) # save entity to neo4j

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
    kg_data = neo4j.return_data()  # save entity to neo4j
    return JsonResponse(kg_data, safe=False)