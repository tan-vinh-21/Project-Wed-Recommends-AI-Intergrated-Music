# Generated by Django 4.2.6 on 2024-09-27 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_song_genre'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='album_cover',
            field=models.ImageField(blank=True, null=True, upload_to='music/images/'),
        ),
    ]
