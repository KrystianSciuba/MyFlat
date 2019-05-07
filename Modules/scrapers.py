import appdata
import threading
import requests
import re
from bs4 import BeautifulSoup


class MainScraper:
    filter = appdata.FlatFilter

    def __init__(self):
        GrumtreeScraper()
        filter = appdata.FlatFilter

    @staticmethod
    def primary_filter_check(args, filter):
        if filter.min_price <= args.price <= filter.max_price:
            if filter.wanted_locations:
                if args.district in filter.wanted_locations:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    @staticmethod
    def secondary_filter_check(args, filter):
        if args.m2price == 0:
            price_filter_bool = filter.filter_value_if_no_data
        elif filter.max_price == 0:
            price_filter_bool = 1
        elif filter.max_m2_price >= args.m2price >= filter.min_m2_price:
            price_filter_bool = 1
        else:
            price_filter_bool = 0

        if args.area == 0:
            area_filter_bool = filter.filter_value_if_no_data
        elif filter.max_area == 0:
            area_filter_bool = 1
        elif filter.max_area >= args.area >= filter.min_area:
            area_filter_bool = 1
        else:
            area_filter_bool = 0

        if args.seller == 0:
            seller_filter_bool = filter.filter_value_if_no_data
        elif filter.wanted_seller == "Dowolny":
            seller_filter_bool = 1
        elif filter.wanted_seller == args.seller:
            seller_filter_bool = 1
        else:
            seller_filter_bool = 0

        if price_filter_bool == area_filter_bool == seller_filter_bool == 1:
            return True
        else:
            return False


class GrumtreeScraper:
    def __init__(self):
        thread = threading.Thread(target=self.gumtree_main_scraper, args=())
        thread.daemon = True
        thread.start()

    def gumtree_main_scraper(self):
        page = 1
        while page <= MainScraper.filter.pages and appdata.main_app_running:
            url = 'https://www.gumtree.pl/s-mieszkania-i-domy-sprzedam-i-kupie/warszawa/mieszkanie/page-' + str(
                page) + '/v1c9073l3200008a1dwp' + str(page)
            print("########   STRONA " + str(page) + ":")
            page += 1
            source_code = requests.get(url)
            plain_text = source_code.text
            plain_text_soup = BeautifulSoup(plain_text, features="html.parser")
            advertisements = plain_text_soup.find(
                lambda tag: tag.name == 'div' and tag.get('class') == ['view'])
            for single_ad in advertisements.findAll("div", {"class": "tileV1"}):
                if appdata.main_app_running:
                    single_flat = self.gumtree_single_ad_scan(args=single_ad)
                    if MainScraper.primary_filter_check(single_flat, filter=MainScraper.filter):
                        self.gumtree_get_flat_data(single_flat)
                        if MainScraper.secondary_filter_check(single_flat, filter=MainScraper.filter):
                            print("OK 2 + OK 1")
                            appdata.flats.append(single_flat)
                            appdata.flats[-1].print_flat_data()
                            #my_app.main_frame.result_table.add_line(single_flat)
                        else:
                            print("OK 1 + NIE OK 2")
                    else:
                        print("NIE OK 1")

    @staticmethod
    def gumtree_single_ad_scan(args):
        ad_link = args.find('a', {'class': 'href-link'})
        href = 'https://www.gumtree.pl' + ad_link.get('href')
        flat_location = args.find("div", {"class": "category-location"})
        flat_district = flat_location.find("span").string
        flat_district = flat_district.strip()
        flat_district = flat_district[30:]  # "mieszkania i domy - sprzedam, Mokotów"
        flat_price: object = args.find("span", {"class": "ad-price"})
        try:
            flat_price: int = int(str(re.sub("\D", "", flat_price.string)))
        except AttributeError:
            flat_price: int = 0

        single_flat = appdata.FlatData(price=flat_price, district=flat_district, url=href)
        return single_flat

    @staticmethod
    def gumtree_get_flat_data(args):
        source_code = requests.get(args.url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, features="html.parser")
        # TYTUŁ OGŁOSZENIA
        for flat_title in soup.find("div", {"class": "vip-title clearfix"}).findAll("span", {'class': 'myAdTitle'}):
            args.title = flat_title.string
            # DATA, POWIERZCHNIA, SPRZEDAWCA
            gumtree_attributes_dict = {'date': "Data dodania",
                                       'area': "Wielkość (m2)",
                                       'seller': "Na sprzedaż przez"}
        flat_data = {}
        for key, value in gumtree_attributes_dict.items():
            flat_attributes = soup.find("div", {"class": 'vip-details'})
            attribute_title = flat_attributes.find("span", string=value)
            try:
                attribute_value = attribute_title.findNextSibling("span")
                data = attribute_value.string
                data = data.strip()
                flat_data[key] = data
            except AttributeError:
                flat_data[key] = 0
        args.date = flat_data['date']
        args.area = float(flat_data['area'])
        args.seller = flat_data['seller']
        # CENA ZA M2
        try:
            args.m2price = int(float(args.price) / float(args.area))
        except (UnicodeEncodeError, ValueError, ZeroDivisionError):
            args.m2price = 0
