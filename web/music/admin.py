from django.contrib import admin
from .models import Artist, Album, Song, User, Playlist


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_staff', 'is_superuser')  # Customize the displayed fields
    search_fields = ('username',)  # Add search capability


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('album_title', 'artist', 'release_date', 'genre')
    list_filter = ('artist', 'genre')
    search_fields = ('album_title', 'artist__name')


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('song_title', 'artist', 'album', 'duration', 'release_date', 'genre')  # Include genre
    list_filter = ('artist', 'album', 'genre')  # Filter by genre
    search_fields = ('song_title', 'artist__name', 'album__album_title', 'genre')  # Search by genre


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'song_count', 'created_at')
    search_fields = ('name', 'user__username')

    def song_count(self, obj):
        return obj.songs.count()  # Returns the count of songs in the playlist

    song_count.short_description = 'Song Count'  # Optional: customize the column header
