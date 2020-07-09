import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Manga, Chapters
from Scripts.scraping_stuff import Scraper
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='login')
def collection(request):
    user = request.user.profile

    if request.GET.get("searchcoll"):
        mangas = Manga.objects.filter(reader=user, name__icontains=request.GET.get('searchcoll'), type=1)
        search = True
    else:
        if request.GET.get('collbtn'):
            my_scraper = Scraper(user)
            my_scraper.get_all()

        search = False
        mangas = Manga.objects.filter(reader=user, type=1)

    paginator = Paginator(mangas, 20)
    page = request.GET.get('page')

    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]

    context = {'mangas': mangas, 'items': items, 'page_range': page_range, 'end_index': end_index, 'search': search}
    return render(request, 'manga/collection.html', context)


@login_required(login_url='login')
def index(request):
    user = request.user.profile
    mangas = Manga.objects.filter(reader=user, type=1).order_by('-date_read')

    has_been_read = []
    for manga in mangas:
        if manga.date_read:
            has_been_read.append(manga)

    return render(request, 'manga/front_page.html', {'mangas': has_been_read[:20]})


@login_required(login_url='login')
def updates(request):
    user = request.user.profile
    if request.GET.get('mybtn'):
        my_scraper = Scraper(user)
        my_scraper.scrape_following()

    Chapters.objects.filter(manga__reader=user, read_status=True).delete()
    updated_chapters = Chapters.objects.filter(manga__reader=user)

    mangas = set()
    for chapter in updated_chapters:
        mangas.add(chapter.manga)

    return render(request, 'manga/updates.html', {'mangas': mangas})


@login_required(login_url='login')
def manga_details(request, name):
    user = request.user.profile
    try:
        manga = Manga.objects.get(reader=user, pk=name)
    except Manga.DoesNotExist:
        raise Http404('Manga does not exist')

    chapters = manga.chapters_set.all()
    context = {'manga': manga, 'chapters': chapters}
    return render(request, 'manga/manga-details.html', context)


def search(request):
    return render(request, 'manga/search_page.html')


@login_required(login_url='login')
def new_search(request):
    search = request.POST.get('search')
    user = request.user.profile
    Manga.objects.filter(reader=user, type=2).delete()

    my_scraper = Scraper(user)
    my_scraper.search(search)

    search_manga = Manga.objects.filter(reader=user, type=2)
    collection_manga = Manga.objects.filter(reader=user, type=1).values_list('manga_id', flat=True)

    in_collection = []
    for manga in search_manga:
        if manga.manga_id in collection_manga:
            in_collection.append(True)
        else:
            in_collection.append(False)

    mangas = zip(search_manga, in_collection)
    stuff_for_frontend = {'mangas': mangas}
    return render(request, 'manga/new_search.html', stuff_for_frontend)


def update_read(request):
    user = request.user.profile
    if request.method == "POST":
        pk = request.POST['pk']
        chapter = Chapters.objects.get(pk=pk)
        chapter.read_status = not chapter.read_status

        my_scraper = Scraper(user)
        if chapter.read_status:
            my_scraper.mark_read(pk)

            # Add last date read
            date = datetime.utcnow()
            manga = chapter.manga
            manga.date_read = date
            manga.save()
        else:
            my_scraper.mark_unread(pk)
        chapter.save()

    return HttpResponse('')


def collect_all_chapters(request):
    user = request.user.profile
    if request.method == "POST":
        if request.POST.get('allunread'):
            my_scraper = Scraper(user)
            manga = Manga.objects.get(pk=request.POST.get('allunread'))
            my_scraper.all_chapters(manga)

    manga = Manga.objects.get(reader=user, pk=request.POST.get('allunread'))
    chapters = manga.chapters_set.all()

    context = {'manga': manga, 'chapters': chapters}
    return render(request, 'manga/manga-details.html', context)


def add_to_coll(request):
    user = request.user.profile
    added = False
    if request.method == "POST":
        pk = request.POST['pk']

        search_manga = Manga.objects.get(manga_id=pk, type=2)
        my_scraper = Scraper(user)
        my_scraper.follow(search_manga)

        if not Manga.objects.filter(name=search_manga.name, reader=user, type=1).exists():
            search_manga.type = 1
            search_manga.save()
            added = True

    added_dict = {'added': added}
    return HttpResponse(json.dumps(added_dict), content_type='application/json')
