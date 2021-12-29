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
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uploadentity/', views.upload_entity, name='upload_entity'),
    path('uploadrelation/', views.upload_relation, name='upload_relation'),
    path('returnkg/', views.return_kg, name='return_kg'),
    path('uploadjson/', views.upload_json, name='upload_json'),
    path('attr/<str:filename>/', views.attr, name='attr'),
    path('creategraph/<str:filename>/', views.create_graph, name='create_graph'),
]
