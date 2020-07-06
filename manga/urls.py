from django.urls import path
from django.views.generic import TemplateView

from . import views  # import views module from the current folder

# map urls to view functions
urlpatterns = [
    path('', views.index, name='home'),  # Root of app
    path('updates', views.updates, name='updates'),
    path('collection', views.collection, name='collection'),
    path('collection/<str:name>', views.manga_details, name="manga-details"),
    path('update_read', views.update_read, name="update_read"),
    path('all_unread', views.collect_all_chapters, name="all_unread"),
    path('new_search', views.new_search, name="new_search"),
    path('add_to_coll', views.add_to_coll, name="add_to_coll"),
]