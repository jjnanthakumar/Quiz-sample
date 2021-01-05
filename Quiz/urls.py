from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quiz/', views.quiz, name='quiz'),
    path('question/', views.question, name='question'),
    path('result/', views.result, name='result')
]
