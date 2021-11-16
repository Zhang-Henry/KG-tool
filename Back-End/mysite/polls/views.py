from mysite.settings import MEDIA_ROOT
from django.shortcuts import render
import os
from django.http import HttpResponse

import sys
sys.path.append("..")
print(sys.path)
# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)


def test1(request, question_id):
    return HttpResponse("这是编号为%d的网页" % question_id)


def upload_data(request):
    if request.method == 'GET':
        return HttpResponse("Get method")
    elif request.method == 'POST':
        file = request.FILES['myfile']
        print("The upload file name is ", file.name)
        filename = os.path.join(MEDIA_ROOT, file.name)
        with open(filename, 'wb') as f:
            data = file.file.read()
            f.write(data)
        return HttpResponse("Received file success: ", file.name)
