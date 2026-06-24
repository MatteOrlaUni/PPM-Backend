import os
import django

# Imposta l'ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from music.models import Genre, Song, Playlist

User = get_user_model()

def populate():
    print("Iniziando il popolamento del database...")

    # 1. Creazione Utenti Demo
    if not User.objects.filter(username='admin_demo').exists():
        User.objects.create_superuser('admin_demo', 'admin@example.com', 'admin12345')
        print("Creato superuser: admin_demo")

    if not User.objects.filter(username='user_demo').exists():
        User.objects.create_user('user_demo', 'user@example.com', 'user12345', role='listener')
        print("Creato listener: user_demo")

    if not User.objects.filter(username='manager_demo').exists():
        User.objects.create_user('manager_demo', 'manager@example.com', 'manager12345', role='curator')
        print("Creato curator: manager_demo")

    listener = User.objects.get(username='user_demo')

    # 2. Creazione Generi
    genres_data = ['Rock', 'Pop', 'Jazz', 'Classical', 'Hip-Hop']
    for g_name in genres_data:
        Genre.objects.get_or_create(name=g_name)
    print("Creati generi musicali.")

    # 3. Creazione Canzoni
    rock = Genre.objects.get(name='Rock')
    pop = Genre.objects.get(name='Pop')
    
    songs_data = [
        {'title': 'Bohemian Rhapsody', 'artist': 'Queen', 'genre': rock, 'duration': '5:55'},
        {'title': 'Stairway to Heaven', 'artist': 'Led Zeppelin', 'genre': rock, 'duration': '8:02'},
        {'title': 'Thriller', 'artist': 'Michael Jackson', 'genre': pop, 'duration': '5:57'},
        {'title': 'Billie Jean', 'artist': 'Michael Jackson', 'genre': pop, 'duration': '4:54'},
    ]

    for s_data in songs_data:
        Song.objects.get_or_create(title=s_data['title'], defaults=s_data)
    print("Create canzoni.")

    # 4. Creazione Playlist Demo
    if not Playlist.objects.filter(name='My Favorite Pop').exists():
        playlist = Playlist.objects.create(name='My Favorite Pop', user=listener)
        for song in Song.objects.filter(genre=pop):
            playlist.songs.add(song)
        print("Creata playlist demo.")

    print("Popolamento completato con successo!")

if __name__ == '__main__':
    populate()
