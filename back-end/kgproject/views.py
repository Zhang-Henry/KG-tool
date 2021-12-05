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


def save_entity(file_name, pk):
    neo4j = Neo4j()
    neo4j.connectDB()
    neo4j.saveEntity(file_name, pk)


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
            content = []
            for line in req.read().splitlines():
                content.append(line)
            # 打开特定的文件进行二进制的写操作
            destination = open(
                os.path.join(config.BASE_IMPORT_URL, req.name), 'wb+')
            for chunk in req.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()
            save_entity(req.name, "movie")
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

            # # 将上传的文件逐行读取保存到list中
            # file_info = {'date': '', 'name': '', 'uuid': '', 'path': ''}
            content = []
            for line in req.read().splitlines():
                content.append(line)

            # 打开特定的文件进行二进制的写操作
            destination = open(
                os.path.join(config.BASE_IMPORT_URL, req.name), 'wb+')
            for chunk in req.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()

            # # 生成当前文件生成UUID
            # file_info['uuid'] = uuid.uuid1()
            # # 上传文件的时间
            # time_stamp = time.time()
            # now = int(round(time_stamp * 1000))
            # file_info['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now / 1000))
            # # 文件名称
            # file_info['name'] = req.name
            # 返回状态信息
            response['msg'] = "Success"
            response['code'] = 200

    except Exception as e:
        response['msg'] = '服务器内部错误'
        response['code'] = 1
    return HttpResponse(json.dumps(response), content_type="application/json")
