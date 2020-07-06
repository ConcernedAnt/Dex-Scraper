from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DexUsername = models.CharField(max_length=255)
    DexPassword = models.CharField(max_length=255)


# Represents a Manga
class Manga(models.Model):
    reader = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(primary_key=True, max_length=255)
    img_url = models.CharField(max_length=2083)
    manga_url = models.CharField(max_length=2083)
    manga_id = models.IntegerField()

    def __str__(self):
        return '{}'.format(self.name)


# Represents a Manga
class Search(models.Model):
    reader = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(primary_key=True, max_length=255)
    img_url = models.CharField(max_length=2083)
    manga_url = models.CharField(max_length=2083)
    manga_id = models.IntegerField()

    def __str__(self):
        return '{}'.format(self.name)


# Represents a chapter of a specific manga
class Chapters(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    chap_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    chapter_url = models.CharField(max_length=2083)
    publish_date = models.DateTimeField(null=True)
    read_status = models.BooleanField(default=False)
