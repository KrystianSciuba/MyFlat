main_app_running = False


class FlatFilter:

    pages = 5
    min_price = 300000
    max_price = 400000
    wanted_locations = []
    min_area = 40
    max_area = 50
    min_m2_price = 0
    max_m2_price = 9500
    wanted_seller = "Any"
    filter_value_if_no_data = 0


class FlatData:
    def __init__(self, site="Gumtree", title="Title", district="District", price=1, area=1, url="url",
                 seller="Seller", date="2019-01-01"):
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
        print("Site: " + str(self.site))
        print("Title: " + str(self.title))
        print("District: " + str(self.district))
        print("Price: " + str(self.price))
        print("Area: " + str(self.area))
        print("URL: " + str(self.url))
        print("Seller: " + str(self.seller))
        print("Price: " + str(self.date))
        print("M2 price: " + str(self.m2price))


flats = []

