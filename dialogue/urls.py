from django.urls import path

from . import views

urlpatterns = [
    path('upload_dialogue/', views.upload_dialogue,
         name='upload_dialogue'),
    path('speech_asr/', views.speech_asr,
         name='speech_asr'),
    path('speech_mie/', views.speech_MIE,
         name='speech_MIE'),
]
