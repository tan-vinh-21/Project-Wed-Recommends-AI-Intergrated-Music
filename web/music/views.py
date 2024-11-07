from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views import View
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Playlist, Album, Song
from .forms import PlaylistForm, SignUpForm
from itertools import groupby
from operator import attrgetter
from django.db.models import Q


# Index
def index(request):
    songs = Song.objects.all()
    # Group albums by genre
    albums = Album.objects.order_by('genre')
    albums_by_genre = {}
    for genre, albums_in_genre in groupby(albums, key=attrgetter('genre')):
        albums_by_genre[genre] = list(albums_in_genre)

    # Check if the user is authenticated for playlists and recommendations
    playlists = None
    favorites_exists = False
    related_songs = []

    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(user=request.user)
        favorites_exists = request.user.playlists.filter(name="Favorites").exists()

        # If favorites do not exist, clear related_songs and reload the page
        if not favorites_exists:
            request.session.pop('related_songs', None)  # Clear related_songs
            request.session.modified = True  # Mark session as modified

        # Call the update_recommend_tab function to refresh recommendations
        update_recommend_tab(request)  # Refresh recommendations based on favorites

        related_songs = request.session.get('related_songs', [])

    return render(request, 'music/index.html', {
        'albums_by_genre': albums_by_genre,
        'playlists': playlists,
        'favorites_exists': favorites_exists,
        'related_songs': related_songs,
        'songs':songs,
    })



# Lyrics view
class LyricsView(View):
    def get(self, request, song_id):
        song = get_object_or_404(Song, id=song_id)
        return render(request, 'music/lyrics.html', {'song': song})  # Update with your actual template path


# Album detail
def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    songs = album.songs.all()

    return render(request, 'music/album_detail.html', {'album': album, 'songs': songs})


# Create Playlist
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user  # Link to the current logged-in user
            playlist.save()
            form.save_m2m()  # Save many-to-many data for songs
            return redirect('index')
    else:
        form = PlaylistForm()

    # Prepare the list of songs with additional fields for display
    songs_with_details = [{'song': song, 'song_title': song.song_title, 'artist': song.artist, 'album': song.album} for song in Song.objects.all()]

    return render(request, 'music/create_playlist.html', {
        'form': form,
        'songs_with_details': songs_with_details
    })


# Playlist detail
class PlaylistDetailView(View):
    def get(self, request, pk):
        playlist = get_object_or_404(Playlist, pk=pk)  # Get the playlist by its primary key
        songs = playlist.songs.all()  # Get all songs related to this playlist
        return render(request, 'music/playlist_detail.html', {'playlist': playlist, 'songs': songs})


# Remove song from playlist
def remove_from_playlist(request, playlist_id, song_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    song = get_object_or_404(Song, id=song_id)
    playlist.songs.remove(song)  # Remove the song from the playlist
    return redirect('/music/playlist_detail.html', playlist_id=playlist_id)


# Delete playlist
def delete_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)  # Ensure the user owns the playlist
    playlist.delete()  # Delete the playlist
    return redirect('index')


# Favourites
def get_or_create_favorites_playlist(user):
    playlist, created = Playlist.objects.get_or_create(name="Favorites", user=user)
    return playlist


@login_required
def favorites_playlist(request):
    favorites = get_object_or_404(Playlist, user=request.user, name="Favorites")
    return render(request, 'music/favorites.html', {'playlist': favorites})


# add fav
@login_required
def add_to_favorites(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    favorites_playlist = get_or_create_favorites_playlist(request.user)
    favorites_playlist.songs.add(song)

    # Redirect back to the album detail page using pk
    return redirect('album_detail', pk=song.album.id)


# remove fav
@login_required
def remove_from_favorites(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    favorites_playlist = get_or_create_favorites_playlist(request.user)  # Assuming this function exists
    favorites_playlist.songs.remove(song)  # Remove the song from the playlist
    return redirect('favorites_playlist')  # Redirect back to the favorites playlist page


# SignUp
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after signing up
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'music/signup.html', {'form': form})

# update recommend
from .model import predict_song_topic
@login_required
def update_recommend_tab(request):
    favorites_playlist = get_or_create_favorites_playlist(request.user)

    if favorites_playlist.songs.exists():
        recommended_songs = []
        liked_genres = set()  # Set to collect unique genres from liked songs

        # Get genres from the fav songs
        for song in favorites_playlist.songs.all():
            liked_genres.add(song.genre)  # Collect the genre of the liked song

            lyrics = song.lyrics
            if lyrics:
                top_topic, top_topic_probability, related_songs = predict_song_topic(lyrics)
                recommended_songs.extend(related_songs)

        # Use set to avoid dupes
        unique_recommended_songs = set(recommended_songs)
        print(f"\nUnique recommended songs: {unique_recommended_songs}")  # Debug

        # Filter the recommended songs based on liked genres
        filtered_recommended_songs = []
        for item in unique_recommended_songs:
            if len(item) == 3:  # Expecting (song_name, genre, probability)
                song_name, genre, probability = item
                if genre in liked_genres:  # Only keep songs with liked genres
                    filtered_recommended_songs.append((song_name, genre))
            else:
                print(f"Unexpected item format in unique_recommended_songs: {item}")  # Debug

        # Match fav song's genre to recommended song's genre
        if not filtered_recommended_songs:
            messages.info(request, "No recommendations found matching your liked genres.")
            request.session.pop('related_songs', None)
            request.session.modified = True  # Mark session as modified
            return redirect('index')

        # Query to get songs from database
        song_queries = Q()
        for song_name, genre in filtered_recommended_songs:
            song_queries |= Q(song_title=song_name, genre=genre)
        recommended_song_objects = Song.objects.filter(song_queries)

        # Debug
        for song in recommended_song_objects:
            print(f"Song Title: {song.song_title}, Genre: {song.genre}, Duration: {song.duration}")

        # Pass to template
        request.session['related_songs'] = [
            {
                'song_title': song.song_title,
                'album': song.album.album_title if song.album else None,
                'artist': song.artist.name if song.artist else None,
                'genre': song.genre,
            } for song in recommended_song_objects
        ]

    else:
        messages.info(request, "No liked songs found. Add songs to your favorites to see recommendations.")
        request.session.pop('related_songs', None)
        request.session.modified = True  # Mark session as modified

    return redirect('index')