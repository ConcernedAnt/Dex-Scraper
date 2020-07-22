from manga.models import Manga, Chapters
from django.utils import timezone
import requests
import re
import datetime
from bs4 import BeautifulSoup
import logging
import multiprocessing

logger = logging.getLogger(__name__)
MAX_THREADS = 30


def get_lang_read_id(manga):
    # Extract the language, read status and chapter id
    language_class = manga.find(class_="chapter-list-flag col-auto text-center order-lg-4").contents[1]
    language = language_class.get("title")

    if manga.find(class_="chapter_mark_unread_button"):
        read = True
        button = manga.find(class_="chapter_mark_unread_button")
        chap_id = button['data-id']
    else:
        read = False
        button = manga.find(class_="chapter_mark_read_button grey")
        chap_id = button['data-id']

    return language, read, chap_id


def get_nav_pagecount(mangasoup, index):
    nav = mangasoup.find(class_="page-item paging")

    if nav:
        page_count_string = nav.a.get("href")
        digit_list = [int(s) for s in re.findall(r'\b\d+\b', page_count_string)]
        page_count = digit_list[index]
    else:
        page_count = 1

    return page_count


def clean_title(title):
    chap_index = title.index("Ch.")
    return title[chap_index:]


class Scraper:
    def __init__(self, profile):
        self.user = profile
        self.date_regex = re.compile("^col-2 col-lg-1 ml-1 text-right text-truncate order-lg-8")

        url = "https://mangadex.org/ajax/actions.ajax.php?function=login"

        self.session = requests.session()
        self.header = {
            'x-requested-with': 'XMLHttpRequest'
        }
        payload = {
            "login_username": self.user.DexUsername,
            "login_password": self.user.DexPassword,
        }
        response = self.session.post(url, headers=self.header, data=payload)

    # Retrieve the image for that manga
    def get_image(self, image_link):
        resp = self.session.get(image_link)
        image_soup = BeautifulSoup(resp.text, "html.parser")
        image_tag = image_soup.find('img', {'class': 'rounded'})
        return image_tag.get("src")

    # Mark manga as read
    def mark_read(self, chapter):
        url = f"https://mangadex.org/ajax/actions.ajax.php?function=chapter_mark_read&id={chapter}"
        response = self.session.get(url, headers=self.header)

    # Mark manga as unread
    def mark_unread(self, chapter):
        url = f"https://mangadex.org/ajax/actions.ajax.php?function=chapter_mark_unread&id={chapter}"
        response = self.session.get(url, headers=self.header)

    # Follow a manga
    def follow(self, manga):
        mid = manga.manga_id
        url = f'https://mangadex.org/ajax/actions.ajax.php?function=manga_follow&id={mid}&type=1'
        response = self.session.get(url, headers=self.header)

    # Unfollow a manga
    def unfollow(self, manga):
        mid = manga.manga_id
        url = f'https://mangadex.org/ajax/actions.ajax.php?function=manga_unfollow&id={mid}&type={mid}'
        response = self.session.get(url, headers=self.header)

    # Write the Chapter to the DB
    def set_class(self, title, manga_href):
        try:
            img_src = self.get_image(manga_href)
        except AttributeError:
            img_src = "https://www.google.com/imgres?imgurl=https%3A%2F%2Fsoftsmart.co.za%2Fwp-content%2Fuploads%2F2018%2F06%2Fimage-not-found-1038x576.jpg&imgrefurl=https%3A%2F%2Fsoftsmart.co.za%2F2018%2F06%2F09%2Ffacebook-share-button-missing-image%2F&tbnid=2jFbS8YPMzN1RM&vet=12ahUKEwj-0IDMhtLqAhXuQDABHeNEBEcQMygAegUIARDBAQ..i&docid=hgexmzgF0JveAM&w=1038&h=576&q=missing%20image&ved=2ahUKEwj-0IDMhtLqAhXuQDABHeNEBEcQMygAegUIARDBAQ"
            logger.error("Dex database was lagging and didn't return an image")

        if not Manga.objects.filter(name=title, reader=self.user).exists():
            digit_list = [int(s) for s in re.findall(r'\b\d+\b', manga_href)]
            manga_id = digit_list[0]

            new_manga = Manga(reader=self.user, name=title, img_url=img_src, manga_url=manga_href, manga_id=manga_id)
            new_manga.save()
        else:
            updated_manga = Manga.objects.get(name=title, reader=self.user)
            updated_manga.img_url = img_src
            updated_manga.save()

    # Get all manga from following
    def get_all(self):
        url_string = "https://mangadex.org/follows/manga/0/0/1/"
        response = self.session.get(url_string)
        soup = BeautifulSoup(response.text, "html.parser")

        page_count = get_nav_pagecount(soup, 2)

        for i in range(page_count):
            url = f"https://mangadex.org/follows/manga/0/0/{i + 1}/"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            mangas = soup.find_all(class_="manga-entry col-lg-6 border-bottom pl-0 my-1")

            for manga in mangas:
                link_class = manga.find(class_="rounded large_logo mr-2")
                manga_href = "https://mangadex.org/" + link_class.a.get("href")
                title = manga.find(class_="ml-1 manga_title text-truncate").string

                self.set_class(title, manga_href)

    # Get all updated chapters
    def scrape_following(self):
        num = 10
        today = datetime.datetime.today()
        margin = datetime.timedelta(days=1)

        previous_title = None
        previous_image = None

        for i in range(num):
            response = self.session.get(f"https://mangadex.org/follows/chapters/1/{i + 1}/")
            soup = BeautifulSoup(response.text, "html.parser")

            mangas = soup.find_all(class_="row no-gutters")
            for manga in mangas:
                title_class = manga.find(class_="manga_title text-truncate")
                no_title_class = manga.find(class_="col col-md-3 d-none d-md-flex row no-gutters flex-nowrap "
                                                   "align-items-center p-2 font-weight-bold border-bottom")

                if not (title_class or no_title_class):
                    continue
                else:
                    # Get language, read status and chapter id
                    (language, read, chap_id) = get_lang_read_id(manga)

                    # Extract the title. Take the previous title if one wasn't provided
                    if title_class:
                        title = title_class.string
                        manga_href = "https://mangadex.org/" + title_class.get("href")

                        previous_title = title
                        previous_image = manga_href
                    else:
                        title = previous_title
                        manga_href = previous_image

                    # Don't add if not in English or if already Read
                    # Could change to do multiple languages (language in ["english", "french", etc])
                    if language != "English":
                        continue
                    if read:
                        if Chapters.objects.filter(chap_id=chap_id, manga__reader=self.user).exists():
                            chapter_object = Chapters.objects.get(chap_id=chap_id, manga__reader=self.user)
                            chapter_object.read_status = True
                            chapter_object.save()
                        continue

                    # Extract the chapter link and chapter name
                    chapter_class = manga.find(lambda tag: tag.name == "a" and tag.get("class") == ["text-truncate"])
                    link = "https://mangadex.org/" + chapter_class.get("href")
                    chapter = clean_title(chapter_class.string)

                    # Get published date and time
                    date = manga.find('div', {"class": self.date_regex})
                    cleaned_date = date.get("title")[:-4]
                    publish_date = datetime.datetime.strptime(cleaned_date, '%Y-%m-%d %H:%M:%S')

                    if publish_date < today - margin:
                        logger.error("Too old")
                        return

                    publish_date = timezone.make_aware(publish_date)
                    # Store info in DB
                    self.set_class(title, manga_href)

                    if not Chapters.objects.filter(chap_id=chap_id, manga__reader=self.user).exists():
                        manga_obj = Manga.objects.get(name=title)
                        new_chapter = Chapters(name=chapter, chapter_url=link, manga=manga_obj,
                                               chap_id=chap_id, publish_date=publish_date)
                        new_chapter.save()

    def all_chapters(self, manga_to_scrape):
        url_string = f"https://mangadex.org/title/{manga_to_scrape.manga_id}/{manga_to_scrape.name}/chapters/1/"

        response = self.session.get(url_string)
        soup = BeautifulSoup(response.text, "html.parser")
        page_count = get_nav_pagecount(soup, 1)

        for i in range(page_count):
            url = f"https://mangadex.org/title/{manga_to_scrape.manga_id}/{manga_to_scrape.name}/chapters/{i + 1}/"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            mangas = soup.find_all(class_="row no-gutters")

            for manga in mangas[1:]:
                # Get language, read status and chapter id
                (language, read, chap_id) = get_lang_read_id(manga)

                if language != "English":
                    continue
                if read:
                    if Chapters.objects.filter(chap_id=chap_id, manga__reader=self.user).exists():
                        chapter_object = Chapters.objects.get(chap_id=chap_id, manga__reader=self.user)
                        chapter_object.read_status = True
                        chapter_object.save()
                    continue

                # Extract the chapter link and chapter name
                chapter_class = manga.find(lambda tag: tag.name == "a" and tag.get("class") == ["text-truncate"])
                link = "https://mangadex.org/" + chapter_class.get("href")
                chapter = clean_title(chapter_class.string)

                # Get published date and time
                date = manga.find('div', {"class": self.date_regex})
                cleaned_date = date.get("title")[:-4]
                publish_date = datetime.datetime.strptime(cleaned_date, '%Y-%m-%d %H:%M:%S')
                publish_date = timezone.make_aware(publish_date)

                if not Chapters.objects.filter(chap_id=chap_id, manga__reader=self.user).exists():
                    manga_obj = manga_to_scrape
                    new_chapter = Chapters(name=chapter, chapter_url=link, manga=manga_obj,
                                           chap_id=chap_id, publish_date=publish_date)
                    new_chapter.save()

    # Collects information on the manga from search page
    def collect_data(self, manga):
        link_class = manga.find(class_="rounded large_logo mr-2").a.get("href")
        manga_href = "https://mangadex.org/" + link_class
        title = manga.find(class_="ml-1 manga_title text-truncate").string
        img_src = self.get_image(manga_href)

        digit_list = [int(s) for s in re.findall(r'\b\d+\b', manga_href)]
        manga_id = digit_list[0]

        new_search = Manga(reader=self.user, name=title, img_url=img_src, manga_url=manga_href,
                           manga_id=manga_id, type=2)
        new_search.save()

    def scrape_search_page(self, mangas):
        for manga in mangas:
            self.collect_data(manga)

    def search(self, search_string):
        url = f"https://mangadex.org/search?title={search_string}"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        page_count = get_nav_pagecount(soup, 1)

        mangas = soup.find_all(class_="manga-entry col-lg-6 border-bottom pl-0 my-1")
        self.scrape_search_page(mangas)

        for i in range(1, page_count):
            url = f"https://mangadex.org/search?s=0&p={i + 1}&tag_mode_inc=all&tag_mode_exc=any&title={search_string}"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            mangas = soup.find_all(class_="manga-entry col-lg-6 border-bottom pl-0 my-1")

            self.scrape_search_page(mangas)

    # def featured(self):
    #     url = "https://mangadex.org/featured"
    #     response = self.session.get(url)
    #     soup = BeautifulSoup(response.text, "html.parser")
    #     mangas = soup.find_all(class_="manga-entry col-lg-6 border-bottom pl-0 my-1")
    #
    #     for manga in mangas:
    #         self.collect_data(manga)
    #
    #         manga_href, title, img_src, manga_id = self.collect_data(manga)

    # Scrape the main page of mangadex to get the most followed
    def most_followed(self):
        url = "https://mangadex.org"
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        popular_tab = soup.find(id="top_follows")

        mangas = popular_tab.find_all(class_="list-group-item px-2 py-1")
        for manga in mangas:
            link_class = manga.find(class_="hover tiny_logo rounded float-left mr-2").a.get("href")
            manga_href = "https://mangadex.org/" + link_class

            title = manga.find(class_="manga_title text-truncate ").string
            self.set_class(title, manga_href)
