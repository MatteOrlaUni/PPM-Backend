from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('songs/', views.SongListView.as_view(), name='song_list'),
    path('songs/add/', views.SongCreateView.as_view(), name='song_add'),
]
