from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/topscorers', views.topscorers, name='topscorers'),
    path('home/topscorersha',  views.topscorersha, name='topscorersha'),
    path('home/ultimateplayers', views.ultimateplayers, name='ultimateplayers'),
    path('home/ultimateplayersha', views.ultimateplayersha, name='ultimateplayersha'),
    path('home/ultimateplayersoa', views.ultimateplayersoa, name='ultimateplayersoa'),
    path('home/ultimateplayersoaha', views.ultimateplayersoaha, name='ultimateplayersoaha'),
    path('home/math', views.math, name='math')
]