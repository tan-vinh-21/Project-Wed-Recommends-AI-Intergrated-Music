# Generated by Django 4.2.6 on 2024-10-02 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0006_album_album_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='lyrics',
            field=models.TextField(blank=True, null=True),
        ),
    ]
