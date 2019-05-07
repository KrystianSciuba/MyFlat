main_app_running = True


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


class FlatData:
    def __init__(self, site="Serwis", title="Tytuł", district="Dzielnica", price=100000, area=10, url="link",
                 seller="Sprzedający", date="2019-01-01"):
        self.site = site
        self.title = title
        self.district = district
        self.price = price
        self.area = area
        self.url = url
        self.seller = seller
        self.date = date
        self.m2price = int(self.price / self.area)

    def print_flat_data(self):
        print("serwis: " + str(self.site))
        print("tytuł: " + str(self.title))
        print("dzielnica: " + str(self.district))
        print("cena: " + str(self.price))
        print("powierzchnia: " + str(self.area))
        print("link: " + str(self.url))
        print("sprzedawca: " + str(self.seller))
        print("data: " + str(self.date))
        print("cena za m2: " + str(self.m2price))

flats = []
