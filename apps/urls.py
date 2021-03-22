from django.urls import path

from .views import (
    indexPage, 
    signUpPage,
    signInPage,
    signOutPage,
    attendeeListPage,
    attendeeProfilePage,
    attendeeSpeakerUpdatePage,
    attendeeSpeakerViewPage,
    attendeeStatsPage,
    paperCreatePage,
    paperRetrievePage,
    paperUpdatePage,
    paperDeletePage,
    paperListPage,
    paperAcceptedPage,
    paperStatsPage,
    paperAcceptedListPage,
    reviewCreatePage,
    reviewUpdatePage,
    reviewRetrievePage,
    dashboardPage,
)

urlpatterns = [
    path('', indexPage, name='index'),
    path('signup/', signUpPage, name='sign_up'),
    path('signin/', signInPage, name='sign_in'),
    path('signout/', signOutPage, name='sign_out'),
    # attendees
    path('attendees/', attendeeListPage, name='attendee_list'),
    path('attendee/profile', attendeeProfilePage, name='attendee_update'),
    path('attendee/speaker/update', attendeeSpeakerUpdatePage, name='speaker_update'),
    path('attendee/speaker/<int:pk>', attendeeSpeakerViewPage, name='speaker_view'),
    path('attendee/stats', attendeeStatsPage, name='attendee_stats'),
    # papers
    path('paper/new', paperCreatePage, name='paper_create'),
    path('paper/<int:pk>/update', paperUpdatePage, name='paper_update'),
    path('paper/<int:pk>/delete', paperDeletePage, name='paper_delete'),
    path('paper/<int:pk>', paperRetrievePage, name='paper_retrieve'),
    path('papers/', paperListPage, name='paper_list'),
    path('paper/<int:pk>/accept', paperAcceptedPage, name='paper_accept'),
    path("paper/stats", paperStatsPage, name='paper_stats'),
    path('papers/accepted', paperAcceptedListPage, name='papers_accepted'),
    # reviews
    path('review/<int:pk>/new', reviewCreatePage, name='review_create'),
    path('review/<int:pk>/update', reviewUpdatePage, name='review_update'),
    path('review/<int:pk>', reviewRetrievePage, name='review_retrieve'),
    # dashboard
    path('dashboard/', dashboardPage, name='dashboard'),
]
