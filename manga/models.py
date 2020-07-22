from django.dispatch import receiver
import urllib.request
from django.db import models
from django.core.files import File
from django.contrib.auth.models import User
from os import path
from fernet_fields import EncryptedCharField
import logging
logger = logging.getLogger(__name__)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DexUsername = models.CharField(max_length=255)
    DexPassword = EncryptedCharField(max_length=255)


# Represents a Manga
class Manga(models.Model):
    reader = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    image_file = models.ImageField(upload_to='images')
    img_url = models.URLField()
    manga_url = models.CharField(max_length=2083)
    manga_id = models.IntegerField()
    date_read = models.DateTimeField(null=True)
    type = models.IntegerField(default=1)

    class Meta:
        unique_together = (("name", "type"),)

    def __str__(self):
        return '{}'.format(self.name)

    def save(self, *args, **kwargs):
        self.get_remote_image()
        super(Manga, self).save(*args, **kwargs)

    def get_remote_image(self):
        if self.img_url and not self.image_file:
            result = urllib.request.urlretrieve(self.img_url)
            if path.exists(f"media/images/{self.manga_id}.jpg"):
                self.image_file = f"images/{self.manga_id}.jpg"
            else:
                with open(result[0], "rb") as downloaded_file:
                    self.image_file.save(f"{self.manga_id}.jpg", File(downloaded_file), save=False)


# Represents a chapter of a specific manga
class Chapters(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE)
    chap_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    chapter_url = models.CharField(max_length=2083)
    publish_date = models.DateTimeField(null=True)
    read_status = models.BooleanField(default=False)


@receiver(models.signals.post_delete, sender=Manga)
def submission_delete(sender, instance, **kwargs):
    instance.image_file.delete(False)
