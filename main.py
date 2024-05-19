# main.py
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb

import pandas as pd

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import ciso8601 as ciso8601

import time
import datetime
import statistics

class MainWindow:
    def __init__(self):
        self.axisY = list()
        self.device = None
        # other
        self.file_name = None
        self.mainmenu = None
        self.graftype = None
        self.frm_left = None
        self.deviceVariable = None
        self.deviceDropdown = None
        self.chbtn_time = None
        self.fromdate = None
        self.a = None
        self.btngrafh = None
        self.canvas = None
        self.axisYVariable = None
        self.axisYDropdown = None
        self.todate = None
        self.averagetype = None
        self.pdjson = None
        self.devices = {}
        # build
        self.build_widgets()
        #tested
        self.open_file()
    def build_widgets(self):
        self.mainmenu = Menu(main_window, tearoff=0)
        main_window.config(menu=self.mainmenu)

        filemenu = Menu(self.mainmenu, tearoff=0)

        filemenutype = Menu(filemenu, tearoff=0)
        filemenutype.add_command(label="JSON", command=self.open_file)

        filemenu.add_cascade(label="Открыть", menu=filemenutype)

        self.mainmenu.add_cascade(label="Файл", menu=filemenu)
        self.graftype = StringVar()
        self.graftype.set("0")
        self.graftype.trace("w", self.changegraf)

        filemenu = Menu(self.mainmenu, tearoff=0)
        filemenu.add_radiobutton(label="Линейный", value="0", variable=self.graftype)
        filemenu.add_radiobutton(label="Столбчатый", value="1", variable=self.graftype)
        filemenu.add_radiobutton(label="Точечный", value="2", variable=self.graftype)

        self.mainmenu.add_cascade(label="Тип графика", menu=filemenu)

        self.averagetype = StringVar()
        self.averagetype.set("0")
        self.averagetype.trace("w", self.changeaverage)

        filemenu = Menu(self.mainmenu, tearoff=0)
        filemenu.add_radiobutton(label="Отсутствует", value="0", variable=self.averagetype)
        filemenu.add_radiobutton(label="Час", value="1", variable=self.averagetype)
        filemenu.add_radiobutton(label="3 Часа", value="2", variable=self.averagetype)
        filemenu.add_radiobutton(label="Сутки", value="3", variable=self.averagetype)
        filemenu.add_radiobutton(label="Мин. и Макс.", value="4", variable=self.averagetype)

        self.mainmenu.add_cascade(label="Осреднение", menu=filemenu)

        self.frm_left = Frame(main_window)
        self.frm_left.pack(side=TOP, padx="20", pady="7")

        Label(self.frm_left, text="Прибор", justify=LEFT, anchor='w') \
            .grid(sticky="E", row=0, column=1)

        toptionlist = ["Не выбрано"]
        self.deviceVariable = StringVar()
        self.deviceVariable.set(toptionlist[0])
        self.deviceDropdown = OptionMenu(
            self.frm_left,
            self.deviceVariable,
            *toptionlist,
        )
        self.deviceDropdown.grid(sticky="W", row=0, column=2)
        self.deviceDropdown.configure(state="disabled")

        Label(self.frm_left, text="Данные", justify=LEFT, anchor='w') \
            .grid(sticky="E", row=0, column=3)

        self.axisYbtn = Button(self.frm_left, text="Открыть выбор", command=self.selectaxisY)

        self.axisYbtn.grid(sticky="W", row=0, column=4)
        self.axisYbtn.configure(state="disabled")

        self.chbtn_time = BooleanVar()
        self.chbtn_time.set(False)
        Checkbutton(self.frm_left, text="По времени",
                    variable=self.chbtn_time,
                    onvalue=True, offvalue=False,
                    command=self.changechecktime) \
            .grid(sticky="W", row=1, column=0)

        Label(self.frm_left, text="От даты", justify=LEFT, anchor='w') \
            .grid(sticky="E", row=1, column=1)
        self.fromdate = Entry(self.frm_left, state='disabled')
        self.fromdate.grid(sticky="W", row=1, column=2)

        Label(self.frm_left, text="До даты", justify=LEFT, anchor='w') \
            .grid(sticky="E", row=1, column=3)
        self.todate = Entry(self.frm_left, state='disabled')
        self.todate.grid(sticky="W", row=1, column=4)

        self.btngrafh = Button(self.frm_left, text="Построить", command=self.writegraf)
        self.btngrafh.grid(sticky="W", row=0, column=5)
        self.btngrafh.configure(state="disabled")

        fig = Figure(dpi=100)
        self.a = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=main_window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(self.canvas, main_window)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
    def open_file(self):
        try:
            self.file_name = fd.askopenfilename(filetypes=[("JSON file", "*.txt")])
            self.resetall()
            self.pdjson = pd.DataFrame(pd.read_json(self.file_name)).transpose()
            uName = self.pdjson['uName']
            serial = self.pdjson['serial']
            j = 0
            for i in self.pdjson.index.tolist():
                if len(self.devices) == 0 or not self.ishavedevice(uName[i], serial[i]):
                    self.devices[j] = {
                        "serial": serial[i],
                        "uName": uName[i],
                        "data": self.pdjson['data'][i]
                    }
                    j += 1
            self.deviceDropdown['menu'].delete(0, 'end')
            for i in range(0, len(self.devices)):
                self.deviceDropdown['menu'].add_command(
                    label=self.devices[i]['uName'] + " (" + self.devices[i]['serial'] + ")",
                    command=lambda value=i: self.choosedevice(value))
            self.deviceDropdown.configure(state="normal")
            self.btngrafh.configure(state="disabled")

        except FileNotFoundError:
            mb.showinfo("Ошибка", "Файл не загружен")

    def choosedevice(self, value):
        self.device = value
        self.deviceVariable.set(self.devices[value][u'uName'] + ' (' + self.devices[value][u'serial'] + ')')

        self.axisYbtn.configure(state="normal")
        self.btngrafh.configure(state="disabled")


    def selectaxisY(self):
        saYvaloreslist = list()
        for choice in self.devices[self.device][u'data']:
            saYvaloreslist.append(choice)

        saYmain = Tk()
        saYmain.title("Multiple Choice Listbox")
        saYmain.geometry("+50+150")
        saYframe = Frame(saYmain)
        saYframe.grid(column=0, row=0, sticky=(N, S, E, W))

        lstbox = Listbox(saYframe, selectmode=MULTIPLE, width=20, height=10)
        lstbox.grid(column=0, row=0, columnspan=2)
        lstbox.insert(END, *saYvaloreslist)

        def select():
            self.axisY = list()
            seleccion = lstbox.curselection()
            for i in seleccion:
                entrada = lstbox.get(i)
                self.axisY.append(entrada)
            saYmain.destroy()
            self.btngrafh.configure(state="normal")

        btn = Button(saYframe, text="Выбрать", command=select)
        btn.grid(column=1, row=1)

        saYmain.mainloop()

    def writegraf(self):
        if self.device is not None and len(self.axisY) > 0:
            dfdevice = self.pdjson[(self.pdjson.uName == self.devices[self.device]['uName']) & (self.pdjson.serial == self.devices[self.device]['serial'])]\
                .reset_index(drop=True)
            def getdata(i, axisY):
                try:
                    return float(dfdevice['data'][i][axisY])
                except:
                    mb.showinfo('Er', 'Данные не являются числом')

            if self.chbtn_time.get():
                if self.fromdate.get() != "":
                    try:
                        fromdate = time.mktime(ciso8601.parse_datetime(self.fromdate.get()).timetuple())
                    except ValueError as err:
                        mb.showinfo("Ошибка",
                                    "Неверно введено `От даты`\n{0}".format(err))
                if self.todate.get() != "":
                    try:
                        todate = time.mktime(ciso8601.parse_datetime(self.todate.get()).timetuple())
                    except ValueError as err:
                        mb.showinfo("Ошибка",
                                    "Неверно введено `До даты`\n{0}".format(err))
            arrtype = {"Date": []}
            for i in self.axisY:
                arrtype[i] = []
            arrtype4axisY = []
            arrtype4 = {"Date": []}
            for i in self.axisY:
                arrtype4[i + "_min"] = []
                arrtype4[i + "_max"] = []
                arrtype4axisY.append(i + "_min")
                arrtype4axisY.append(i + "_max")
            if self.averagetype.get() == "0":
                timet = datetime.timedelta(seconds = -1)
            elif self.averagetype.get() == "1":
                timet = datetime.timedelta(hours = 1)
            elif self.averagetype.get() == "2":
                timet = datetime.timedelta(hours = 3)
            elif self.averagetype.get() == "3":
                timet = datetime.timedelta(days = 1)
            datecomp = False
            for axY in self.axisY:
                ttime = 0
                storj = [getdata(0, axY)]
                for i in range(0, len(dfdevice)):
                    ts = ciso8601.parse_datetime(dfdevice['Date'][i])
                    if not self.chbtn_time.get() or ((self.fromdate.get() == "" or time.mktime(ts.timetuple()) > fromdate) and (self.todate.get() == "" or time.mktime(ts.timetuple()) < todate)):
                        if self.averagetype.get() != "4":
                            if ttime == 0:
                                ttime = ts
                            if ts - ttime > timet or i == len(dfdevice) - 1:
                                arrtype[axY].append(statistics.mean(storj))
                                if not datecomp:
                                    if self.averagetype.get() == "0":
                                        arrtype['Date'].append(pd.to_datetime(dfdevice['Date'][i]))
                                    else:
                                        arrtype['Date'].append(pd.to_datetime(dfdevice['Date'][i]) - timet / 2)
                                ttime = ts
                                storj = []
                        else:
                            if ttime == 0:
                                ttime = ts.day
                            if ts.day != ttime or i == len(dfdevice) - 1:
                                arrtype4[axY + "_min"].append(min(storj))
                                arrtype4[axY + "_max"].append(max(storj))
                                if not datecomp:
                                    arrtype4['Date'].append(pd.to_datetime(dfdevice['Date'][i]) - datetime.timedelta(days = 1) / 2)
                                ttime = ts.day
                                storj = []
                        storj.append(getdata(i, axY))
                datecomp = True
            self.a.clear()
            self.a.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%m'))
            if(self.averagetype.get() == "4"):
                dftype4 = pd.DataFrame(arrtype4)
                if self.graftype.get() == "0":
                    dftype4.plot(ax=self.a, x = "Date", y = arrtype4axisY);
                if self.graftype.get() == "1":
                    dftype4.plot(kind="bar", ax=self.a, x = "Date", y = arrtype4axisY)
                if self.graftype.get() == "2":
                    dftype4.plot(style='o', ax=self.a, x="Date", y=arrtype4axisY)
            else:
                dftype = pd.DataFrame(arrtype)
                if self.graftype.get() == "0":
                    dftype.plot(ax=self.a, x = "Date", y = self.axisY);
                if self.graftype.get() == "1":
                    dftype.plot(kind="bar", ax=self.a, x = "Date", y = self.axisY)
                if self.graftype.get() == "2":
                    dftype.plot(style='o', ax=self.a, x="Date", y= self.axisY)
            self.canvas.draw()


    def cleargraf(self):
        self.a.clear()
        self.canvas.draw()

    def resetall(self):
        self.deviceDropdown.configure(state="disabled")
        self.axisYbtn.configure(state="disabled")
        self.deviceVariable.set("Не выбрано")
        self.cleargraf()
        self.axisY = list()
        self.device = None

    def changechecktime(self):
        if not self.chbtn_time.get():
            self.fromdate.configure(state='disabled')
            self.todate.configure(state='disabled')
        else:
            self.fromdate.configure(state="normal")
            self.todate.configure(state="normal")

    def changegraf(self, *args):
        self.writegraf()

    def changeaverage(self, *args):
        self.writegraf()

    def ishavedevice(self, uName, serial):
        for ij in self.devices:
            if self.devices[ij]['uName'] == uName and self.devices[ij]['serial'] == serial:
                return True
        return False

main_window = Tk()
main_window.title('chart')
main_window.geometry('1000x800')
window = MainWindow()
main_window.mainloop()
