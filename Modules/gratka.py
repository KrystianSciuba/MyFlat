import appdata
import requests
import re
from bs4 import BeautifulSoup
from scrapers import MainScraper
import threading


class GratkaScraper:
    def __init__(self):
        thread = threading.Thread(target=self.gratka_main_scraper, args=())
        thread.daemon = True
        thread.start()

    def gratka_main_scraper(self):
        page = 1
        while page <= 1:
            #<= MainScraper.filter.pages and appdata.main_app_running:
            url = "https://gratka.pl/nieruchomosci/mieszkania/warszawa/sprzedaz?page="+str(page)+"&rynek=wtorny"
            print("########   PAGE " + str(page) + ":")
            print(url)
            page += 1
            source_code = requests.get(url)
            plain_text = source_code.text
            print(plain_text)
            plain_text_soup = BeautifulSoup(plain_text, features="html.parser")
            advertisements = plain_text_soup.find(
                lambda tag: tag.name == 'div' and tag.get('class') == ['dfp dfp--teaser dfp--marginTop'])
            print(advertisements)


gratka = GratkaScraper()
