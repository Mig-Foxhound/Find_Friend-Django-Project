from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('search/', views.Search, name='search'),
]

urlpatterns += [
    path('users/', views.UserDetail, name='user-detail'),
    path('users/create/', views.CreateUser, name='user-create'),
    path('users/insert/', views.InsertUserForm, name='user-insert'),
    path('users/update/', views.UserUpdate, name='user-update'),
    path('users/update_form', views.UpdateUserForm, name='user-update-form'),
    path('users/delete/', views.UserDelete, name='user-delete'),
    path('users/deleted/', views.UserDeleted, name='user-deleted'),
    path('users/match/', views.UserMatch, name='user-match')
]

urlpatterns +=[
    path('match/user/', views.MatchUser, name='match-user'),
    path('match/place/', views.MatchPlace, name='match-place')
]
urlpatterns += [
    path('location/', views.UpdateLocation, name='location-update'),
    path('location/search_location', views.SearchLocation, name='location-search')
]

urlpatterns += [
    path('places/crawl/', views.CrawlPopularity, name='place_crawl')
]
