from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model


# User Class
# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("The Username field is required")
        user = self.model(username=username)
        user.set_password(password)
        user.is_staff = False  # Default to False for regular users
        user.save(using=self._db)
        # Automatically create a "Favorites" playlist for the new user
        Playlist.objects.create(user=user, name="Favorites")
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_staff = True  # Set to True for superusers
        user.is_superuser = True  # Set to True for superusers
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_superuser = models.BooleanField(default=False)  # Grants all permissions

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


# --- Content Class
# Artist
class Artist(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Album Model
class Album(models.Model):
    album_title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, related_name='albums', on_delete=models.CASCADE)
    release_date = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    album_cover = models.ImageField(upload_to='music/images/', blank=True, null=True)  # New image field

    def __str__(self):
        return f"{self.album_title}"


# Song Model
class Song(models.Model):
    song_title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, related_name='songs', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name='songs', on_delete=models.CASCADE, blank=True, null=True)
    duration = models.DurationField(help_text="Duration of the song (e.g. 00:03:30)", blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    lyrics = models.TextField(blank=True, null=True)
    mp3_file = models.FileField(upload_to='mp3_files/', blank=True, null=True)  # MP3 upload field

    def save(self, *args, **kwargs):
        if self.album and not self.genre:
            self.genre = self.album.genre
        if self.album and self.album.release_date:
            self.release_date = self.album.release_date
        super().save(*args, **kwargs)

    def __str__(self):
        album_title = self.album.album_title if self.album else "No Album"
        return f"{self.song_title} by {self.artist.name} ({album_title})"


# Playlist
class Playlist(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='playlists', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    songs = models.ManyToManyField('Song', related_name='playlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"

    def song_count(self):
        return self.songs.count()


# A method to add a song to the user's favorites playlist
def add_to_favorites(user, song):
    favorites, created = Playlist.objects.get_or_create(user=user, name="Favorites")
    favorites.songs.add(song)
    return favorites
