import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from .models import Song, Genre, Playlist, Artist
from .forms import CustomUserCreationForm

def auth_view(request):
    if request.user.is_authenticated:
        return redirect('catalog_list')
        
    login_form = AuthenticationForm(request)
    signup_form = CustomUserCreationForm()
    active_tab = 'login'
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('catalog_list')
        elif action == 'signup':
            active_tab = 'signup'
            signup_form = CustomUserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('catalog_list')
                
    context = {
        'login_form': login_form,
        'signup_form': signup_form,
        'active_tab': active_tab,
    }
    return render(request, 'login.html', context)

class HomeView(TemplateView):
    template_name = 'main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_releases'] = Song.objects.all().order_by('-created_at')[:5]
        context['popular_artists'] = Artist.objects.all().order_by('name')[:8]
        return context

class CatalogListView(ListView):
    template_name = 'catalogue.html'
    context_object_name = 'items'

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', 'song')
        genre_id = self.request.GET.get('genre')

        if search_type == 'playlist':
            if self.request.user.is_authenticated:
                if self.request.user.is_curator():
                    queryset = Playlist.objects.all().order_by('-created_at')
                else:
                    queryset = Playlist.objects.filter(user=self.request.user).order_by('-created_at')
            else:
                queryset = Playlist.objects.none()
            if q:
                queryset = queryset.filter(name__icontains=q)
        elif search_type == 'artist':
            queryset = Artist.objects.all().order_by('-created_at')
            if q:
                queryset = queryset.filter(name__icontains=q)
            if genre_id:
                queryset = queryset.filter(songs__genre_id=genre_id).distinct()
        else: # song
            queryset = Song.objects.all().order_by('-created_at')
            if q:
                queryset = queryset.filter(Q(title__icontains=q) | Q(artist__name__icontains=q))
            if genre_id:
                queryset = queryset.filter(genre_id=genre_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['search_type'] = self.request.GET.get('type', 'song')
        context['q'] = self.request.GET.get('q', '')
        context['genre_id'] = self.request.GET.get('genre', '')
        
        playlist_id = self.request.GET.get('add_to_playlist')
        if playlist_id and self.request.user.is_authenticated:
            try:
                playlist = Playlist.objects.get(id=playlist_id, user=self.request.user)
                context['adding_to_playlist'] = playlist
                if context['search_type'] == 'song':
                    playlist_songs = set(playlist.songs.values_list('id', flat=True))
                    for song in context['items']:
                        song.in_playlist = song.id in playlist_songs
            except Playlist.DoesNotExist:
                pass

        if self.request.user.is_authenticated:
            context['user_playlists'] = Playlist.objects.filter(user=self.request.user)
            
        context['popular_artists'] = Artist.objects.all().order_by('name')
        
        return context

class PlaylistDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Playlist
    template_name = 'item.html'
    context_object_name = 'playlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.object
        context['title'] = playlist.name
        context['subtitle'] = f"Creata da {playlist.user.username} • {playlist.songs.count()} brani"
        context['cover_type'] = 'playlist'
        context['type_label'] = 'Playlist'
        context['items'] = playlist.songs.all()
        context['item_type'] = 'song'
        context['can_edit'] = playlist.user == self.request.user or self.request.user.is_curator()
        context['can_remove_item'] = playlist.user == self.request.user
        context['edit_url'] = reverse('playlist_edit_inline', args=[playlist.id])
        context['playlist_id'] = playlist.id
        return context

    def test_func(self):
        playlist = self.get_object()
        return playlist.user == self.request.user or self.request.user.is_curator()
        
    def handle_no_permission(self):
        messages.error(self.request, "Azione non consentita.")
        return redirect('catalog_list')

class PlaylistEditInlineView(LoginRequiredMixin, View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        if playlist.user == request.user or request.user.is_curator():
            new_title = request.POST.get('new_title')
            if new_title:
                playlist.name = new_title
                playlist.save()
        return redirect('playlist_detail', pk=pk)

class PlaylistCreateView(LoginRequiredMixin, View):
    def post(self, request):
        playlist = Playlist.objects.create(name="Nuova Playlist", user=request.user)
        return redirect('playlist_detail', pk=playlist.id)

class AddSongToPlaylistView(LoginRequiredMixin, View):
    def post(self, request, song_id):
        playlist_id = request.POST.get('playlist_id')
        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
            song = get_object_or_404(Song, id=song_id)
            playlist.songs.add(song)
            messages.success(request, f"'{song.title}' aggiunto a {playlist.name}")
        return redirect('catalog_list')

class RemoveSongFromPlaylistView(LoginRequiredMixin, View):
    def post(self, request, playlist_id, song_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        song = get_object_or_404(Song, id=song_id)
        playlist.songs.remove(song)
        return redirect('playlist_detail', pk=playlist_id)

class TogglePlaylistSongView(LoginRequiredMixin, View):
    def post(self, request, playlist_id, song_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        song = get_object_or_404(Song, id=song_id)
        
        try:
            data = json.loads(request.body)
            add = data.get('add', True)
        except:
            add = True

        if add:
            playlist.songs.add(song)
            status = 'added'
        else:
            playlist.songs.remove(song)
            status = 'removed'
            
        return JsonResponse({'status': status, 'song_id': song.id})

class PlaylistBulkSaveView(LoginRequiredMixin, View):
    def post(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        selected_song_ids = request.POST.getlist('song_ids')
        
        # Le canzoni nella playlist vengono tolte/aggiunte in base alle spunte
        playlist.songs.clear()
        if selected_song_ids:
            songs_to_add = Song.objects.filter(id__in=selected_song_ids)
            playlist.songs.add(*songs_to_add)
            
        messages.success(request, "Playlist aggiornata con successo.")
        return redirect('playlist_detail', pk=playlist_id)

class ArtistDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist_name = self.kwargs['name']
        artist = get_object_or_404(Artist, name=artist_name)
        songs = Song.objects.filter(artist=artist).order_by('-created_at')
        context['title'] = artist.name
        context['subtitle'] = f"{songs.count()} brani nel catalogo"
        context['cover_type'] = 'artist'
        context['type_label'] = 'Artista'
        context['items'] = songs
        context['item_type'] = 'song'
        context['can_edit'] = self.request.user.is_curator()
        context['can_remove_item'] = False
        context['edit_url'] = reverse('artist_edit_inline', args=[artist.name])
        return context

class ArtistEditInlineView(LoginRequiredMixin, View):
    def post(self, request, name):
        artist = get_object_or_404(Artist, name=name)
        if request.user.is_curator():
            new_name = request.POST.get('new_title')
            if new_name and new_name != name:
                artist.name = new_name
                artist.save()
                return redirect('artist_detail', name=new_name)
        return redirect('artist_detail', name=name)

class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs['username']
        user = get_object_or_404(get_user_model(), username=username)
        playlists = Playlist.objects.filter(user=user)
        context['title'] = user.username
        context['subtitle'] = f"{playlists.count()} playlist pubbliche"
        context['cover_type'] = 'user'
        context['type_label'] = f"Utente - {user.role.title()}"
        context['items'] = playlists
        context['item_type'] = 'playlist'
        context['can_edit'] = self.request.user.is_curator() or self.request.user == user
        context['can_remove_item'] = False
        context['edit_url'] = reverse('user_edit_inline', args=[user.username])
        return context

class UserEditInlineView(LoginRequiredMixin, View):
    def post(self, request, username):
        user = get_object_or_404(get_user_model(), username=username)
        if request.user.is_curator() or request.user == user:
            new_username = request.POST.get('new_title')
            if new_username and new_username != username:
                if not get_user_model().objects.filter(username=new_username).exists():
                    user.username = new_username
                    user.save()
                    return redirect('user_detail', username=new_username)
                else:
                    messages.error(request, "Username già in uso.")
        return redirect('user_detail', username=username)
