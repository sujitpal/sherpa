from django.urls import path

from .views import (
    indexPage, 
    signUpPage,
    signInPage,
    signOutPage,
    attendeeListPage,
    paperCreatePage,
    paperRetrievePage,
    paperUpdatePage,
    paperDeletePage,
    paperListPage
)

urlpatterns = [
    path('', indexPage, name='index'),
    path('signup/', signUpPage, name='sign_up'),
    path('signin/', signInPage, name='sign_in'),
    path('signout/', signOutPage, name='sign_out'),
    path('attendees/', attendeeListPage, name='attendee_list'),
    path('paper/new', paperCreatePage, name='paper_create'),
    path('paper/<int:pk>', paperRetrievePage, name='paper_retrieve'),
    path('paper/<int:pk>/update', paperUpdatePage, name='paper_update'),
    path('paper/<int:pk>/delete/', paperDeletePage, name='paper_delete'),
    path('papers/', paperListPage, name='paper_list'),
]
