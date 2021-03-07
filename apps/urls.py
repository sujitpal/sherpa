# from django.contrib import admin
# from django.urls import include, path
from django.urls import path

from .views import (
    indexPage, 
    registerPage,
    attendeeListPage,
    paperCreatePage,
    paperRetrievePage,
    paperUpdatePage,
    paperDeletePage,
    paperListPage
)

urlpatterns = [
    path('', indexPage, name='index'),
    path('register/', registerPage, name='register'),
    path('attendees/', attendeeListPage, name='attendee_list'),
    path('paper_create/', paperCreatePage, name='paper_create'),
    path('paper/', paperRetrievePage, name='paper'),
    path('paper_update/', paperUpdatePage, name='paper_update'),
    path('paper_delete/', paperDeletePage, name='paper_delete'),
    path('papers/', paperListPage, name='papers'),
]
