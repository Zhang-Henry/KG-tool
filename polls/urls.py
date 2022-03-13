from django.urls import path

from . import views

urlpatterns = [
    path('save_graph/', views.save_graph, name='save_graph'),
]
