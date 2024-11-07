from .models import Playlist

def user_playlists(request):
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(user=request.user)
    else:
        playlists = None

    return {
        'playlists': playlists,
    }
