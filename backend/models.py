from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('listener', 'Listener'),
        ('curator', 'Curator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='listener')

    def is_curator(self):
        return self.role == 'curator' or self.is_superuser

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs', null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='songs')
    duration = models.CharField(max_length=10, help_text="e.g. 3:45", blank=True, null=True)
    external_link = models.URLField(blank=True, null=True, help_text="Link to external audio source (e.g. YouTube/Spotify)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playlists')
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"
