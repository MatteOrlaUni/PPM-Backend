import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model, login, authenticate, logout
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

        if search_type == 'genre':
            queryset = Genre.objects.all().order_by('name')
            if q:
                queryset = queryset.filter(name__icontains=q)
        elif search_type == 'artist':
            queryset = Artist.objects.all().order_by('-created_at')
            if q:
                queryset = queryset.filter(Q(name__icontains=q) | Q(songs__genre__name__icontains=q)).distinct()
        elif search_type == 'user' and self.request.user.is_authenticated and self.request.user.is_curator():
            queryset = get_user_model().objects.all().order_by('username')
            if q:
                queryset = queryset.filter(username__icontains=q)
        else: # song
            queryset = Song.objects.all().order_by('-created_at')
            if q:
                queryset = queryset.filter(Q(title__icontains=q) | Q(artist__name__icontains=q) | Q(genre__name__icontains=q))
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_type'] = self.request.GET.get('type', 'song')
        context['q'] = self.request.GET.get('q', '')
        
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
            if self.request.user.is_curator():
                context['all_genres'] = Genre.objects.all().order_by('name')
                context['all_artists'] = Artist.objects.all().order_by('name')
                context['existing_artists_json'] = json.dumps(list(Artist.objects.values_list('name', flat=True)))
                context['existing_genres_json'] = json.dumps(list(Genre.objects.values_list('name', flat=True)))
                context['existing_songs_json'] = json.dumps([{"title": s.title, "artist_id": str(s.artist_id)} for s in Song.objects.all()])
            
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
        context['existing_names'] = json.dumps(list(Playlist.objects.filter(user=playlist.user).exclude(id=playlist.id).values_list('name', flat=True)))
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
            if new_title and new_title != playlist.name:
                if not Playlist.objects.filter(user=playlist.user, name=new_title).exists():
                    playlist.name = new_title
                    playlist.save()
        return redirect('playlist_detail', pk=pk)

class PlaylistCreateView(LoginRequiredMixin, View):
    def post(self, request):
        existing_names = set(Playlist.objects.filter(user=request.user).values_list('name', flat=True))
        prog = 0
        while f"Nuova Playlist [{prog}]" in existing_names:
            prog += 1
        name = f"Nuova Playlist [{prog}]"
        playlist = Playlist.objects.create(name=name, user=request.user)
        return redirect('playlist_detail', pk=playlist.id)

class PlaylistDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)
        if playlist.user == request.user or request.user.is_curator():
            playlist.delete()
            messages.success(request, "Playlist eliminata con successo.")
        else:
            messages.error(request, "Azione non consentita.")
        return redirect('main')

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

class AdminArtistDeleteView(LoginRequiredMixin, View):
    def post(self, request, name):
        if not request.user.is_curator():
            return redirect('main')
            
        artist = get_object_or_404(Artist, name=name)
        artist.delete()
        
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('catalog_list')


class GenreDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre_name = self.kwargs['name']
        genre = get_object_or_404(Genre, name=genre_name)
        songs = Song.objects.filter(genre=genre).order_by('-created_at')
        context['title'] = genre.name
        context['subtitle'] = f"{songs.count()} brani nel catalogo"
        context['cover_type'] = 'genre'
        context['type_label'] = 'Genere'
        context['items'] = songs
        context['item_type'] = 'song'
        context['can_edit'] = self.request.user.is_curator()
        context['can_remove_item'] = False
        context['edit_url'] = reverse('genre_edit_inline', args=[genre.name])
        return context

class GenreEditInlineView(LoginRequiredMixin, View):
    def post(self, request, name):
        genre = get_object_or_404(Genre, name=name)
        if request.user.is_curator():
            new_name = request.POST.get('new_title')
            if new_name and new_name != name:
                genre.name = new_name
                genre.save()
                return redirect('genre_detail', name=new_name)
        return redirect('genre_detail', name=name)


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
        context['list_title'] = "Playlist"
        return context

class UserEditInlineView(LoginRequiredMixin, View):
    def post(self, request, username):
        user = get_object_or_404(get_user_model(), username=username)
        if request.user.is_curator() or request.user == user:
            new_username = request.POST.get('new_title')
            new_password = request.POST.get('password')
            
            updated = False
            if new_username and new_username != username:
                if not get_user_model().objects.filter(username=new_username).exists():
                    user.username = new_username
                    updated = True
                else:
                    messages.error(request, "Username già in uso.")
            
            if new_password:
                user.set_password(new_password)
                updated = True
                # Keep user logged in if they changed their own password
                if request.user == user:
                    login(request, user)
                    
            if updated:
                user.save()
                return redirect('user_detail', username=user.username)

        return redirect('user_detail', username=username)

class UserDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        logout(request)
        user.delete()
        return redirect('main')

class AdminUserDeleteView(LoginRequiredMixin, View):
    def post(self, request, username):
        if not request.user.is_curator():
            return redirect('main')
            
        target_user = get_object_or_404(get_user_model(), username=username)
        # Prevent deleting yourself through this route just in case
        if target_user == request.user:
            return redirect('catalog_list')
            
        target_user.delete() # Playlists will be deleted on cascade
        
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('catalog_list')

class AdminGenreDeleteView(LoginRequiredMixin, View):
    def post(self, request, name):
        if not request.user.is_curator():
            return redirect('main')
            
        genre = get_object_or_404(Genre, name=name)
        genre.delete()
        
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('catalog_list')

class AdminSongDeleteView(LoginRequiredMixin, View):
    def post(self, request, id):
        if not request.user.is_curator():
            return redirect('main')
            
        song = get_object_or_404(Song, id=id)
        song.delete()
        
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('catalog_list')

class AdminArtistCreateView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.is_curator():
            name = request.POST.get('name')
            if name:
                Artist.objects.get_or_create(name=name)
        return redirect('/catalogue/?type=artist')

class AdminGenreCreateView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.is_curator():
            name = request.POST.get('name')
            if name:
                Genre.objects.get_or_create(name=name)
        return redirect('/catalogue/?type=genre')

class AdminSongCreateView(LoginRequiredMixin, View):
    def post(self, request):
        if request.user.is_curator():
            title = request.POST.get('title')
            artist_id = request.POST.get('artist')
            genre_id = request.POST.get('genre')
            if title and artist_id and genre_id:
                try:
                    artist = Artist.objects.get(id=artist_id)
                    genre = Genre.objects.get(id=genre_id)
                    if not Song.objects.filter(title__iexact=title, artist=artist).exists():
                        Song.objects.create(title=title, artist=artist, genre=genre)
                except (Artist.DoesNotExist, Genre.DoesNotExist, ValueError):
                    pass
        return redirect('/catalogue/?type=song')
