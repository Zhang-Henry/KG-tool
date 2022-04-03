from django.urls import path

from . import views

urlpatterns = [
    path('save_graph/', views.save_graph, name='save_graph'),
    path('build_graph_name/', views.build_graph_name, name='build_graph_name'),
    path('all_graph_info/', views.all_graph_info, name='all_graph_info'),
    path('delete_graph/', views.delete_graph, name='delete_graph'),

]
