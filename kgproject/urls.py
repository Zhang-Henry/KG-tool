"""kgproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
# from django.views.decorators.cache import cache_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uploadjson/', views.upload_json, name='upload_json'),
    path('attr/<str:filename>/', views.attr, name='attr'),
    path('creategraph/<str:filename>/', views.create_graph, name='create_graph'),
    path('get_entity/<str:entity_name>/',
         views.get_entity, name='get_entity'),
    path('get_relation/<str:relation_name>/',
         views.get_relation, name='get_relation'),
    path('after_creation/', views.after_creation, name='after_creation'),
    path('nerText/', views.nerText, name='nerText'),
    # path('get_answer/', cache_page(60 * 15)(views.get_answer), name='get_answer'),
    path('get_answer/', views.get_answer, name='get_answer'),
    path('search_item/', views.search_item, name='search_item'),
    path('show_node_only/', views.show_node_only, name='show_node_only'),
    path('show_relation_only/', views.show_relation_only,
         name='show_relation_only'),
    path('delete_node/', views.delete_node,
         name='delete_node'),
    path('delete_relation/', views.delete_relation,
         name='delete_relation'),
    path('relation_entity_extraction/', views.relation_entity_extraction,
         name='relation_entity_extraction'),
    path('get_progress/', views.get_progress, name='get_progress'),
    path('polls/', include('polls.urls')),
    path('dialogue/', include('dialogue.urls')),
]
