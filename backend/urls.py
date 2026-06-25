from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    
    path('login/', views.auth_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='catalog_list'), name='logout'),
    
    path('catalogue/', views.CatalogListView.as_view(), name='catalog_list'),
    
    path('playlists/<int:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    path('playlists/<int:pk>/edit_inline/', views.PlaylistEditInlineView.as_view(), name='playlist_edit_inline'),
    path('playlists/create/', views.PlaylistCreateView.as_view(), name='playlist_create'),
    
    path('playlists/add_song/<int:song_id>/', views.AddSongToPlaylistView.as_view(), name='playlist_add_song'),
    path('playlists/<int:playlist_id>/remove_song/<int:song_id>/', views.RemoveSongFromPlaylistView.as_view(), name='playlist_remove_song'),
    path('playlists/<int:playlist_id>/toggle_song/<int:song_id>/', views.TogglePlaylistSongView.as_view(), name='playlist_toggle_song'),
    path('playlists/<int:playlist_id>/bulk_save/', views.PlaylistBulkSaveView.as_view(), name='playlist_bulk_save'),

    path('artist/<str:name>/', views.ArtistDetailView.as_view(), name='artist_detail'),
    path('artist/<str:name>/edit_inline/', views.ArtistEditInlineView.as_view(), name='artist_edit_inline'),

    path('user/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user/<str:username>/edit_inline/', views.UserEditInlineView.as_view(), name='user_edit_inline'),
]
