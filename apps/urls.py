# from django.contrib import admin
# from django.urls import include, path
from django.urls import path

from .views import indexPage

urlpatterns = [
    path('', indexPage)
]
