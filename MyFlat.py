import tkinter as tk
from tkinter import ttk
import threading
from bs4 import BeautifulSoup
import re
import requests
import webbrowser


class MainScraper(BeautifulSoup):

    main_app_running = False

    def __init__(self):

        self.filter = FlatFilter
        thread = threading.Thread(target=self.gumtree_main_scraper, args=())
        thread.daemon = True
        thread.start()

    def gumtree_main_scraper(self):
        page = 1
        while page <= self.filter.pages and MainScraper.main_app_running:
            url = 'https://www.gumtree.pl/s-mieszkania-i-domy-sprzedam-i-kupie/warszawa/mieszkanie/page-' + str(
                page) + '/v1c9073l3200008a1dwp' + str(page)
            print("########   STRONA " + str(page) + ":")
            page += 1
            source_code = requests.get(url)
            plain_text = source_code.text
            plain_text_soup = BeautifulSoup(plain_text, features="html.parser")
            advertisements = plain_text_soup.find(
                lambda tag: tag.name == 'div' and tag.get('class') == ['view'])
            for single_ad in advertisements.findAll("div", {"class": "container"}):
                if MainScraper.main_app_running:
                    single_flat = MainScraper.gumtree_single_ad_scan(single_ad)
                    if MainScraper.primary_filter_chceck(single_flat, filter=self.filter):
                        single_flat.get_flat_data_gumtree()
                        if MainScraper.secondary_filter_check(single_flat, filter=self.filter):
                            print("OK 2 + OK 1")
                            my_app.main_frame.result_table.add_line(single_flat)
                        else:
                            print("OK 1 + NIE OK 2")
                    else:
                        print("NIE OK 1")

    def gumtree_single_ad_scan(args):
        ad_link = args.find('a', {'class': 'href-link'})
        href = 'https://www.gumtree.pl' + ad_link.get('href')
        flat_location = args.find("div", {"class": "category-location"})
        flat_district = flat_location.find("span").string
        flat_district = flat_district.strip()
        flat_district = flat_district[31:]  # "mieszkania i domy - sprzedam , Mokotów"
        flat_price: object = args.find("span", {"class": "amount"})
        try:
            flat_price: int = int(str(re.sub("\D", "", flat_price.string)))
        except AttributeError:
            flat_price: int  = 0

        single_flat = FlatData(price=flat_price, district=flat_district, url=href)
        return single_flat

    def primary_filter_chceck(args, filter):
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

    def secondary_filter_check(args, filter):
        if args.pricem2 == 0:
            price_filter_bool = filter.filter_value_if_no_data
        elif filter.max_price == 0:
            price_filter_bool = 1
        elif filter.max_m2_price >= args.pricem2 >= filter.min_m2_price:
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

class FlatFilter:
    pages = 5
    min_price = 300000
    max_price = 400000
    wanted_locations = []
    min_area = 40
    max_area = 50
    min_m2_price = 0
    max_m2_price = 9500
    wanted_seller = "Dowolny"

    filter_value_if_no_data = 0

class FlatData(BeautifulSoup):
    def __init__(self, site="Serwis", title="Tytuł", district="Dzielnica", price=1, area=1, url="link",
                 seller="Sprzedający", date="2019-01-01"):
        self.site = site
        self.title = title
        self.district = district
        self.price = price
        self.area = area
        self.url = url
        self.seller = seller
        self.date = date
        self.pricem2 = int(self.price / self.area)

    def get_flat_data_gumtree(self):
        source_code = requests.get(self.url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, features="html.parser")
        # TYTUŁ
        for flat_title in soup.find("div", {"class": "vip-title clearfix"}).findAll("span", {'class': 'myAdTitle'}):
            self.title = flat_title.string

        ################################pętla!!!!!!#################################
        gumtree_attributes_dict = {'DATA': "Data dodania",
                                   'POWIERZCHNIA': "Wielkość (m2)",
                                   'SPRZEDAWCA': "Na sprzedaż przez"}
        flat_data = {}
        for key, value in gumtree_attributes_dict.items():
            flat_attributes = soup.find("div", {"class": 'vip-details'})
            attribute_title = flat_attributes.find("span", string=value)
            try:
                attribute_value = attribute_title.findNextSibling("span")
                data = attribute_value.string
                data = data.strip()
                flat_data[key] = data
            except AttributeError as error:
                flat_data[key] = 0
        self.date = flat_data['DATA']
        self.area = float(flat_data['POWIERZCHNIA'])
        self.seller = flat_data['SPRZEDAWCA']
        # cena za m2
        try:
            self.pricem2 = int(float(self.price) / float(self.area))
        except (UnicodeEncodeError, ValueError, ZeroDivisionError):
            self.pricem2 = 0


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.main_frame = MainFrame(self)


class MainFrame(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        self.top_frame = tk.Frame(parent)
        self.middle_frame = tk.Frame(parent)
        self.bottom_frame = tk.Frame(parent)

        self.top_frame.grid(column=0, row=0)
        self.middle_frame.grid(column=0, row=1)
        self.bottom_frame.grid(column=0, row=2)

        self.district_buttons_list = DistrictButtonsFrame(self.top_frame)
        self.flat_data_filter_box = FlatDataFilterBox(self.middle_frame)
        self.ok_button = OkButtonFrame(parent=self.middle_frame, box=self.flat_data_filter_box)
        self.result_table = ResultTable(parent=self.bottom_frame)


class DistrictButtonsFrame(tk.Frame):
    def __init__(self, parent):
        district_buttons_frame = tk.Frame
        self.parent = parent
        district_list = ["Bemowo", "Białołęka", "Bielany", "Mokotów", "Ochota", "Praga Południe", "Praga Północ",
                         "Rembertów", "Śródmieście", "Targówek", "Ursus", "Ursynów", "Wawer", "Wesoła", "Wilanów",
                         "Wola", "Włochy", "Żoliborz"]
        for i, district in enumerate(district_list):
            self.district_button = self.District_Button(parent, i, district)

    class District_Button:
        def __init__(self, parent, i, district):
            self.district_name = district
            self.var = tk.IntVar()
            self.parent = parent
            self.button = tk.Checkbutton(parent,
                                         text=district,
                                         variable=self.var,
                                         indicatoron=0,
                                         width=15,
                                         command=self.district_button_click,
                                         onvalue=1,
                                         offvalue=0)
            self.button.grid(column=i % 6, row=i // 6)

        def district_button_click(self):
            if self.var.get():
                print("dodano", self.district_name, "do listy")
                FlatFilter.wanted_locations.append(self.district_name)
                print(FlatFilter.wanted_locations)
            else:
                print("usunięto", self.district_name, "do listy")
                FlatFilter.wanted_locations.remove(self.district_name)
                print(FlatFilter.wanted_locations)


class FlatDataFilterBox(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        self.price = FilterMinMax(parent, "Cena", 300000, 400000, 0)
        self.area = FilterMinMax(parent, "Powierzchnia", 40, 60, 1)
        self.m2_price = FilterMinMax(parent, "Cena za m2", 0, 9500, 2)
        self.pages = Filter(parent, "Zakres stron:  ", 4, 3)


class OkButtonFrame(tk.Frame):

    def __init__(self, parent, box):
        self.parent = parent
        self.ok_button = tk.Button(parent, text="go go go go go",
                                   command=lambda temp=box: self.ok_button_click(temp)).grid(column=1, row=4)
        self.stop_button = tk.Button(parent, text="HOLD! HOLD!", command=self.stop_button_click).grid(column=3, row=4)

    def ok_button_click(self, box):
        self.apply_filters(box)
        MainScraper.main_app_running = True
        self.main_spider = MainScraper()

    def stop_button_click(self):
        MainScraper.main_app_running = False
        print("STOOOOOOP!!!")

    def apply_filters(self, box):
        FlatFilter.min_price = int(box.price.min.get())
        FlatFilter.max_price = int(box.price.max.get())
        FlatFilter.min_area = int(box.area.min.get())
        FlatFilter.max_area = int(box.area.max.get())
        FlatFilter.min_m2_price = int(box.m2_price.min.get())
        FlatFilter.max_m2_price = int(box.m2_price.max.get())
        FlatFilter.pages = int(box.pages.min.get())

        print(FlatFilter.min_price)
        print(FlatFilter.max_price)
        print(FlatFilter.min_area)
        print(FlatFilter.max_area)
        print(FlatFilter.min_m2_price)
        print(FlatFilter.max_m2_price)
        print(FlatFilter.pages)

class ResultTable(ttk.Treeview):
    def __init__(self, parent):
        self.parent = parent

        self.table = ttk.Treeview(parent, columns=(
            "DATA", "CENA", "POW.", "SPRZEDAWCA", "CENA ZA M2", "DZIELNICA", "TYTUŁ", "URL"))
        self.table.heading('#0', text="DATA", command=lambda: self.treeview_sort_column("DATA", False))
        self.table.heading('#1', text="CENA", command=lambda: self.treeview_sort_column("CENA", False))
        self.table.heading('#2', text="POW.", command=lambda: self.treeview_sort_column("POW.", False))
        self.table.heading('#3', text="SPRZEDAWCA", command=lambda: self.treeview_sort_column("SPRZEDAWCA", False))
        self.table.heading('#4', text="CENA ZA M2", command=lambda: self.treeview_sort_column("CENA ZA M2", False))
        self.table.heading('#5', text="DZIELNICA", command=lambda: self.treeview_sort_column("DZIELNICA", False))
        self.table.heading('#6', text="TYTUŁ", command=lambda: self.treeview_sort_column("TYTUŁ", False))
        self.table.heading('#7', text="URL", command=lambda: self.treeview_sort_column("URL", False))
        self.table.column('#0', width=100, stretch=tk.NO)
        self.table.column('#1', width=75, stretch=tk.NO)
        self.table.column('#2', width=75, stretch=tk.NO)
        self.table.column('#3', width=100, stretch=tk.NO)
        self.table.column('#4', width=100, stretch=tk.NO)
        self.table.column('#5', width=100, stretch=tk.NO)
        self.table.column('#6', width=250, stretch=tk.NO)
        self.table.column('#7', width=400, stretch=tk.NO)
        self.table.pack()

        self.table.bind("<Double-Button-1>", self.callback)

    def add_line(self, args):
        self.table.insert('', 'end', text=args.date, values=(
            args.price, args.area, args.seller, args.pricem2, args.district, args.title, args.url), )

    def callback(self, event):
        input_id = self.table.selection()
        item_text = self.table.item(input_id, "values")

        try:
            webbrowser.open(item_text[-1])
        except (IndexError) as error:
            pass

    #   print("CLICK!!!!!!!!!!!!!!")

    def test_button_click(self):
        self.table.insert('', 'end', values=('test przycisku', 'cos'))

    def treeview_sort_column(self, col, reverse):
        # https://www.reddit.com/r/learnpython/comments/4fdqr2/help_understanding_this_treeview_sort_function/
        l = [(self.table.set(k, col), k) for k in self.table.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.table.move(k, '', index)

        # reverse sort next time
        self.table.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))


class Filter(tk.Frame):
    def __init__(self, parent, name, defmin, row):
        self.parent = parent
        self.text = tk.Label(parent, text=name)
        self.min = tk.IntVar()
        self.min.set(defmin)
        self.min_entry = tk.Entry(parent, textvariable=self.min)
        self.text.grid(row=row, column=0)
        self.min_entry.grid(row=row, column=1)


class FilterMinMax(Filter):
    def __init__(self, parent, name, defmin, defmax, row):
        Filter.__init__(self, parent, name, defmin, row)
        self.separator = tk.Label(parent, text="   do   ")
        self.max = tk.IntVar()
        self.max.set(defmax)
        self.max_entry = tk.Entry(parent, textvariable=self.max)
        self.separator.grid(row=row, column=2)
        self.max_entry.grid(row=row, column=3)


if __name__ == "__main__":
    root = tk.Tk()
    my_app = MainApplication(root)
    my_app.pack()
    root.mainloop()
