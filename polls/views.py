from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from polls.models import *

# Create your views here.
@csrf_exempt
def save_graph(request):
    if request.method == "POST":
        text = request.body.decode("utf-8")
        text = json.loads(text)
        name, labels, relations= text['name'],text['entities'],text['relations']
        q_set =  KG.objects.filter(kg_name=name)
        if q_set.exists():
          return HttpResponse('The knowledge graph name has existed.', content_type="application/json")
        else:
          kg = KG.objects.create(kg_name=name)
          kg.save()
          for label in labels:
            e = Label.objects.create(kg_name=kg, label_name=label)
            e.save()
          for relation in relations:
            r = Relation.objects.create(kg_name=kg, relation_name=relation)
            r.save()
    return HttpResponse('success', content_type="application/json")
