import django
from django.contrib.auth import get_user_model
from backend.models import Genre, Artist, Song, Playlist

User = get_user_model()

# Create clean state
User.objects.exclude(is_superuser=True).delete()
Genre.objects.all().delete()
Artist.objects.all().delete()
Song.objects.all().delete()

u1 = User.objects.create_user(username='utente1', password='password1', role='listener')
u2 = User.objects.create_user(username='utente2', password='password2', role='curator')

g_pop = Genre.objects.create(name='Pop')
g_rock = Genre.objects.create(name='Rock')
g_jazz = Genre.objects.create(name='Jazz')
g_rap = Genre.objects.create(name='Rap')

a1 = Artist.objects.create(name='Artista 1')
a2 = Artist.objects.create(name='Artista 2')
a3 = Artist.objects.create(name='Artista 3')
a4 = Artist.objects.create(name='Artista 4')
a5 = Artist.objects.create(name='Artista 5')

songs_data = [
    ('Titolo canzone 1', a1, g_pop),
    ('Titolo canzone 2', a1, g_rock),
    ('Titolo canzone 3', a2, g_jazz),
    ('Titolo canzone 4', a2, g_pop),
    ('Titolo canzone 5', a3, g_rap),
    ('Titolo canzone 6', a3, g_rock),
    ('Titolo canzone 7', a4, g_jazz),
    ('Titolo canzone 8', a4, g_rap),
    ('Titolo canzone 9', a5, g_pop),
    ('Titolo canzone 10', a5, g_rock),
]

for title, artist, genre in songs_data:
    Song.objects.create(title=title, artist=artist, genre=genre, duration="3:00")

print("Database populated successfully!")
