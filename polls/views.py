from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from polls.models import *
from django.core.cache import cache
from kgproject.models.query_db import query_db

# Create your views here.
@csrf_exempt
def save_graph(request):
    if request.method == "POST":
        text = request.body.decode("utf-8")
        text = json.loads(text)
        name, labels, relations, date, type= text['name'],text['entities'],text['relations'], text['date'], text['type']
        q_set =  KG.objects.filter(name=name)
        if q_set.exists():
          return HttpResponse('The knowledge graph name has existed.', content_type="application/json")
        else:
          kg = KG.objects.create(name=name,type=type,date=date)
          kg.save()
          for label in labels:
            Label.objects.create(kg=kg, name=label)
          for relation in relations:
            Relation.objects.create(kg=kg, name=relation)
    return HttpResponse('success', content_type="application/json")


@csrf_exempt
def build_graph_name(request):  # 保存图谱时传入名字
    if request.method == "POST":
        data = json.loads(request.body)
        kg_name = data['name']
        # kg_name = request.POST.get('name')
        graph = KG.objects.filter(name=kg_name)
        if graph.exists():
          msg = "duplicate name"
        else:
          cache.set('current_graph', kg_name, None)
          msg = "success"
    return HttpResponse(msg)


@csrf_exempt
def all_graph_info(request):
    kgs = KG.objects.all()
    graphs = list()
    for kg in kgs:
      labels = Label.objects.filter(kg=kg)
      rels = Relation.objects.filter(kg=kg)
      graphs.append({
        'name':kg.name,
        'date':kg.date,
        'type':kg.type,
        'entities':[label.name for label in labels],
        'relations':[rel.name for rel in rels]
      })
    return HttpResponse(json.dumps(graphs), content_type="application/json")



@csrf_exempt
def delete_graph(request):
    if request.method == "POST":
        data = json.loads(request.body)
        kg_name = data['name']
        # kg_name = request.POST.get('name')
        kgs = KG.objects.filter(name=kg_name)
        if kgs.exists():
          query_db.delete_graph(kg_name)
          kgs.delete()
          msg = "success"
        else:
          msg = "Graph name does not exist."
    return HttpResponse(msg)


@csrf_exempt
def show_select_graph(request):
    if request.method == "POST":
        data = json.loads(request.body)
        kg_name = data['name']
        # kg_name = request.POST.get('name')
        cache.set('current_graph', kg_name, None)
        info = query_db.select_graph(kg_name)
    return HttpResponse(json.dumps(info), content_type="application/json")
