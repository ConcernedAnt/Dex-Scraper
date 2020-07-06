from django.contrib import admin
from .models import Manga, Chapters, Profile


# Register your models here.

class MangaAdmin(admin.ModelAdmin):
    list_display = ('name', 'img_url')


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'publish_date')


admin.site.register(Manga, MangaAdmin)
admin.site.register(Chapters, ChapterAdmin)
admin.site.register(Profile)
