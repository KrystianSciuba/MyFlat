import widgets
import tkinter as tk


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.main_frame = MainFrame(self)


class MainFrame:
    def __init__(self, parent):
        self.parent = parent

        self.top_frame = tk.Frame(parent)
        self.middle_frame = tk.Frame(parent)
        self.bottom_frame = tk.Frame(parent)

        self.top_frame.grid(column=0, row=0)
        self.middle_frame.grid(column=0, row=1)
        self.bottom_frame.grid(column=0, row=2)

        self.district_buttons_list = widgets.DistrictButtonsFrame(self.top_frame)
        self.flat_data_filter_box = widgets.FlatDataFilterBox(self.middle_frame)
        self.ok_button = widgets.OkButtonFrame(parent=self.middle_frame, box=self.flat_data_filter_box)
        self.result_table = widgets.ResultTable(parent=self.bottom_frame)


if __name__ == "__main__":
    root = tk.Tk()
    my_app = MainApplication(root)
    my_app.pack()
    root.mainloop()
