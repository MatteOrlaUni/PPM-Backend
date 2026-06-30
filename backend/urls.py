from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='main'),
    
    path('catalogue/', views.CatalogListView.as_view(), name='catalog_list'),
    path('admin/song/create/', views.AdminSongCreateView.as_view(), name='admin_song_create'),
    path('admin/song/<int:id>/update/', views.AdminSongUpdateView.as_view(), name='admin_song_update'),
    path('admin/song/<int:id>/delete/', views.AdminSongDeleteView.as_view(), name='admin_song_delete'),
    
    path('playlists/<int:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    path('playlists/<int:pk>/edit_inline/', views.PlaylistEditInlineView.as_view(), name='playlist_edit_inline'),
    path('playlists/create/', views.PlaylistCreateView.as_view(), name='playlist_create'),
    path('playlists/<int:pk>/delete/', views.PlaylistDeleteView.as_view(), name='playlist_delete'),
    
    path('playlists/<int:playlist_id>/remove_song/<int:song_id>/', views.RemoveSongFromPlaylistView.as_view(), name='playlist_remove_song'),
    path('playlists/<int:playlist_id>/bulk_save/', views.PlaylistBulkSaveView.as_view(), name='playlist_bulk_save'),

    path('artist/<str:name>/', views.ArtistDetailView.as_view(), name='artist_detail'),
    path('artist/<str:name>/edit_inline/', views.ArtistEditInlineView.as_view(), name='artist_edit_inline'),
    path('admin/artist/create/', views.AdminArtistCreateView.as_view(), name='admin_artist_create'),
    path('admin/artist/<str:name>/delete/', views.AdminArtistDeleteView.as_view(), name='admin_artist_delete'),

    path('genre/<str:name>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('genre/<str:name>/edit_inline/', views.GenreEditInlineView.as_view(), name='genre_edit_inline'),
    path('admin/genre/create/', views.AdminGenreCreateView.as_view(), name='admin_genre_create'),
    path('admin/genre/<str:name>/delete/', views.AdminGenreDeleteView.as_view(), name='admin_genre_delete'),

    path('', include('users.urls')),
]
