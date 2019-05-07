import tkinter as tk
from tkinter import ttk
import appdata
import scrapers
import webbrowser


class DistrictButtonsFrame:
    def __init__(self, parent):
        district_list = ["Bemowo", "Białołęka", "Bielany", "Mokotów", "Ochota", "Praga Południe", "Praga Północ",
                         "Rembertów", "Śródmieście", "Targówek", "Ursus", "Ursynów", "Wawer", "Wesoła", "Wilanów",
                         "Wola", "Włochy", "Żoliborz"]
        for i, district in enumerate(district_list):
            self.district_button = self.DistrictButton(parent, i, district)

    class DistrictButton:
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
                print("added", self.district_name, " to district list")
                appdata.FlatFilter.wanted_locations.append(self.district_name)
                print(appdata.FlatFilter.wanted_locations)
            else:
                print("removed", self.district_name, " from district list")
                appdata.FlatFilter.wanted_locations.remove(self.district_name)
                print(appdata.FlatFilter.wanted_locations)


class FlatDataFilterBox:
    def __init__(self, parent):
        self.parent = parent

        self.price = self.FilterMinMax(parent, "Price", 300000, 400000, 0)
        self.area = self.FilterMinMax(parent, "Area", 40, 60, 1)
        self.m2_price = self.FilterMinMax(parent, "M2 price", 0, 9500, 2)
        self.pages = self.Filter(parent, "Pages to search  ", 4, 3)

    class Filter:
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
            FlatDataFilterBox.Filter.__init__(self, parent, name, defmin, row)
            self.separator = tk.Label(parent, text="   do   ")
            self.max = tk.IntVar()
            self.max.set(defmax)
            self.max_entry = tk.Entry(parent, textvariable=self.max)
            self.separator.grid(row=row, column=2)
            self.max_entry.grid(row=row, column=3)


class OkButtonFrame:

    def __init__(self, parent, box):
        self.parent = parent
        self.ok_button = tk.Button(parent, text="go go go go go",
                                   command=lambda temp=box: self.ok_button_click(temp)).grid(column=1, row=4)
        self.stop_button = tk.Button(parent, text="HOLD! HOLD!", command=self.stop_button_click).grid(column=3, row=4)

    @staticmethod
    def ok_button_click(box):
        OkButtonFrame.apply_filters(box)
        appdata.main_app_running = True
        scrapers.MainScraper()

    @staticmethod
    def stop_button_click():
        appdata.main_app_running = False
        print("STOP!!!")

    @staticmethod
    def apply_filters(box):
        appdata.FlatFilter.min_price = int(box.price.min.get())
        appdata.FlatFilter.max_price = int(box.price.max.get())
        appdata.FlatFilter.min_area = int(box.area.min.get())
        appdata.FlatFilter.max_area = int(box.area.max.get())
        appdata.FlatFilter.min_m2_price = int(box.m2_price.min.get())
        appdata.FlatFilter.max_m2_price = int(box.m2_price.max.get())
        appdata.FlatFilter.pages = int(box.pages.min.get())

        print(appdata.FlatFilter.min_price)
        print(appdata.FlatFilter.max_price)
        print(appdata.FlatFilter.min_area)
        print(appdata.FlatFilter.max_area)
        print(appdata.FlatFilter.min_m2_price)
        print(appdata.FlatFilter.max_m2_price)
        print(appdata.FlatFilter.pages)


class ResultTable:
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
            args.price, args.area, args.seller, args.m2price, args.district, args.title, args.url), )

    def callback(self, event):
        input_id = self.table.selection()
        item_text = self.table.item(input_id, "values")

        try:
            webbrowser.open(item_text[-1])
        except IndexError:
            pass

    def treeview_sort_column(self, col, reverse):
        list = [(self.table.set(k, col), k) for k in self.table.get_children('')]
        list.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(list):
            self.table.move(k, '', index)

        # reverse sort next time
        self.table.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))
