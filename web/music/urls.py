from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .views import album_detail, create_playlist, PlaylistDetailView, delete_playlist, signup, add_to_favorites, \
    favorites_playlist, remove_from_favorites, remove_from_playlist, predict_song_topic, LyricsView

urlpatterns = [
    # Index
    path('', views.index, name='index'),

    # Album detail
    path('album/<int:pk>/', album_detail, name='album_detail'),

    # Lyrics view
    path('songs/<int:song_id>/lyrics/', LyricsView.as_view(), name='song_lyrics'),

    # Create playlist
    path('create_playlist/', create_playlist, name='create_playlist'),
    # Playlist detail
    path('playlist/<int:pk>/', PlaylistDetailView.as_view(), name='playlist_detail'),
    # Remove song from playlist
    path('playlist/<int:playlist_id>/remove/<int:song_id>/', remove_from_playlist, name='remove_from_playlist'),
    # Delete playlist
    path('delete_playlist/<int:pk>/', delete_playlist, name='delete_playlist'),

    # Add to favorites
    path('like/<int:song_id>/', add_to_favorites, name='add_to_favorites'),
    # View favorites playlist
    path('favorites/', favorites_playlist, name='favorites_playlist'),
    # Remove fav
    path('favorites/remove/<int:song_id>/', remove_from_favorites, name='remove_from_favorites'),
    
    # Logout + Login + SignUp
    path('login/', LoginView.as_view(template_name='music/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', signup, name='signup'),

    # Prediction
    path('predict_song_topic/', predict_song_topic, name='predict_song_topic'),
]
