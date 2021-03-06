# from django.contrib import admin
# from django.urls import include, path
from django.urls import path

from .views import indexPage, registerPage

urlpatterns = [
    path('', indexPage, name='index'),
    path('register/', registerPage, name='register')
]
