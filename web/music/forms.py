from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Playlist, Song, User


# Playlist Form
class PlaylistForm(forms.ModelForm):
    songs = forms.ModelMultipleChoiceField(
        queryset=Song.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False  # Make it optional to select songs
    )

    class Meta:
        model = Playlist
        fields = ['name', 'songs']

# Signup
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


# Login
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)