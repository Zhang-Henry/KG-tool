from django.http import HttpResponse,HttpResponseNotFound,Http404
from django.shortcuts import render #渲染模板
from django.shortcuts import redirect #重定向
from django.urls import reverse #反向解析
from django.views import View#视图类需要
from django.http import JsonResponse#相应json数据
from datetime import datetime
import json
import os
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def uploadFile(request):
    context = {}
    if request.method == "POST":    # 请求方法为POST时，进行处理
        myFile =request.FILES.get("myfile", None)    # 获取上传的文件，如果没有文件，则默认为None
        if not myFile:
            context['message'] = "文件上传失败"
        else:
            destination = open(os.path.join("./data",myFile.name),'wb+')    # 打开特定的文件进行二进制的写操作
            for chunk in myFile.chunks():      # 分块写入文件
                destination.write(chunk)
            destination.close()
            context['message'] = "文件上传成功"
    return render(request, "index.html",context)

def KGInfor(req):
    context = {}
    if req.method == "POST":
        e = req.POST.get("entity", None)
        r = req.POST.get("relation", None)

        entitys = e.split(" ")
        relations = r.split(" ")

        print(entitys, relations)
        context['message'] = "实体名称关系上传成功"
    return render(req, "index2.html", context)

def KGshow(req):




    data = [{'name': '中国科学院计算技术研究所', 'des': '中国科学院计算技术研究所', 'symbolSize': 80, 'category': 0, }, \
            {'name': '徐志伟', 'des': '徐志伟', 'symbolSize': 80, 'category': 1, }, \
            {'name': '文继荣', 'des': '文继荣', 'symbolSize': 80, 'category': 1, }, \
            {'name': '钮心忻', 'des': '钮心忻', 'symbolSize': 80, 'category': 1, }, ]
    links = [{'target': '中国科学院计算技术研究所', 'source': '徐志伟', 'name': '属于', 'des': '作者-作者单位'}, \
             {'target': '中国科学院计算技术研究所', 'source': '文继荣', 'name': '属于', 'des': '作者-作者单位'}, \
             {'target': '中国科学院计算技术研究所', 'source': '钮心忻', 'name': '属于', 'des': '作者-作者单位'}, ]

    return render(req,"index3.html", {'data': json.dumps(data), 'link': json.dumps(links)})



