from django.shortcuts import render
from django.views.generic import TemplateView, ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Song, Genre

class HomeView(TemplateView):
    template_name = 'music/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_songs'] = Song.objects.order_by('-created_at')[:5]
        return context

class SongListView(ListView):
    model = Song
    template_name = 'music/song_list.html'
    context_object_name = 'songs'

class SongCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Song
    template_name = 'music/song_form.html'
    fields = ['title', 'artist', 'genre', 'duration', 'external_link']
    success_url = reverse_lazy('music:song_list')

    def test_func(self):
        # Solo i Curator (o superuser) possono creare brani
        return self.request.user.is_curator()

