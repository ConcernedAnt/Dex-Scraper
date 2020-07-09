from django.contrib import admin
from .models import Manga, Chapters, Profile


# Register your models here.
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'publish_date')


admin.site.register(Manga)
admin.site.register(Chapters, ChapterAdmin)
admin.site.register(Profile)
