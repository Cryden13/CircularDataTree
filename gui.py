from tkinter.filedialog import asksaveasfilename as Askfile
from tkinter import StringVar, Tk, Canvas, Frame, Entry
from scrolledframe import ScrolledFrame as SFrame
from tkinter import LabelFrame as LFrame
from tkinter.ttk import Style, Button
from PIL.ImageTk import PhotoImage
from typing import Optional as O
from PIL.Image import Image
from pathlib import Path
from re import split
import json

try:
    from .datachart import DataChart
except ImportError:
    from subprocess import run
    pth = Path(__file__).parent
    run(['py', '-m', pth.name], cwd=pth.parent)
    raise SystemExit


class GUI(Tk):
    """This app allows for easy editing of circular datatrees"""
    dataset: dict[str, dict[str, list[str]]] = dict()
    datapth = Path(__file__).with_name('dataset.json')
    imgcanvas: Canvas
    image: Image
    imagetk: PhotoImage
    cnvimg: int
    saveBtn: Button
    dataScrl: SFrame
    dataFrm: Frame
    datadict: dict[Entry, dict[Entry, list[Entry]]]
    imgargs: tuple[StringVar, StringVar, StringVar, StringVar]

    def __init__(self):
        Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        wd = (self.winfo_screenwidth() // 2)
        ht = (self.winfo_screenheight() // 2)
        self.geometry(f'{wd * 1.5:.0f}'
                      f'x{ht * 1.5:.0f}'
                      f'+{wd - wd * 0.75:.0f}'
                      f'+{ht - ht * 0.75:.0f}')

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.option_add('*font', 'Ebrima 12')
        self.option_add('*Entry.width', 15)
        s = Style()
        s.configure('TButton', font='Ebrima 12')
        s.configure('sm.TButton', width=6, font='Ebrima 8')
        self.datadict = dict()
        self.build()

    def on_exit(self):
        self.quit()
        self.destroy()

    def build(self):
        # data buttons
        dataBtns = LFrame(master=self,
                          text="Dataset")
        dataBtns.grid(column=0,
                      row=0)
        self.buildDataBtns(dataBtns)
        # data
        self.dataScrl = SFrame(master=self)
        self.dataScrl.grid(column=0,
                           row=1,
                           sticky='nsew')
        self.buildData()
        # image buttons
        imgBtns = LFrame(master=self,
                         text="Image")
        imgBtns.grid(column=0,
                     row=2,
                     pady=3)
        self.buildImgBtns(imgBtns)
        # canvas
        cnvfrm = SFrame(master=self,
                        padding=3)
        cnvfrm.grid(column=1,
                    row=0,
                    rowspan=3,
                    sticky='nsew')
        self.buildCanvas(cnvfrm)

#  ___ _   _ _____ _____ ___  _  _ ___
# | _ ) | | |_   _|_   _/ _ \| \| / __|
# | _ \ |_| | | |   | || (_) | .` \__ \
# |___/\___/  |_|   |_| \___/|_|\_|___/

  #    ___  ___ _________
  #   / _ \/ _ /_  __/ _ |
  #  / // / __ |/ / / __ |
  # /____/_/ |_/_/ /_/ |_|

    def buildDataBtns(self, parent):
        loadBtn = Button(master=parent,
                         text="Load",
                         command=self.loadData)
        loadBtn.grid(column=0,
                     row=0,
                     padx=3)
        clearBtn = Button(master=parent,
                          text="Clear",
                          command=self.clearData)
        clearBtn.grid(column=1,
                      row=0,
                      padx=3)
        saveBtn = Button(master=parent,
                         text="Save",
                         command=self.saveData)
        saveBtn.grid(column=2,
                     row=0,
                     padx=3)

    def loadData(self):
        with self.datapth.open('r') as f:
            self.dataset = json.load(f)
        self.datadict.clear()
        for w in self.dataFrm.winfo_children():
            w.destroy()
        for inr, sub in self.dataset.items():
            mfrm, k = self.addInner(inr)
            for mid, items in sub.items():
                ofrm, v = self.addMid(mfrm, k, mid)
                for out in items:
                    self.addOuter(ofrm, k, v, out)

    def clearData(self):
        self.dataset.clear()
        self.datadict.clear()
        for w in self.dataScrl.winfo_children():
            w.destroy()
        self.buildData()

    def saveData(self):
        self.getData()
        with self.datapth.open('w') as f:
            json.dump(self.dataset, f, indent=4)

  #    ______  ______  _________
  #   /  _/  |/  / _ |/ ___/ __/
  #  _/ // /|_/ / __ / (_ / _/
  # /___/_/  /_/_/ |_\___/___/

    def buildImgBtns(self, parent):
        def lblent(txt, var, col, row) -> None:
            lfrm = LFrame(master=parent,
                          text=txt,
                          font='Ebrima 8')
            lfrm.grid(column=col,
                      row=row,
                      padx=3)
            ent = Entry(master=lfrm,
                        textvariable=var)
            ent.pack()

        cmapnm = StringVar()
        offset = StringVar()
        ffamily = StringVar()
        fsize = StringVar()
        self.imgargs = (cmapnm, offset, ffamily, fsize)
        cmapnm.set('hsv')
        offset.set('20')
        ffamily.set('Ebrima')
        fsize.set('8, 7, 6.5')

        lblent("Colormap Name", cmapnm, 0, 0)
        lblent("Color Offset", offset, 1, 0)
        lblent("Font Family", ffamily, 0, 1)
        lblent("Font Size (inner, mid, outer)", fsize, 1, 1)
        drawBtn = Button(master=parent,
                         text="Draw",
                         command=self.drawImg)
        drawBtn.grid(column=0,
                     row=2,
                     padx=3)
        self.saveBtn = Button(master=parent,
                              text="Save",
                              command=self.saveImg,
                              state='disabled')
        self.saveBtn.grid(column=1,
                          row=2,
                          padx=3)

    def drawImg(self):
        self.getData()
        cm, off, fam, sz = self.imgargs
        self.image = DataChart(dataset=self.dataset,
                               colormap_name=cm.get(),
                               offset=float(off.get()),
                               fontfamily=fam.get(),
                               fontsize=[float(n) for n in split(r', ?| ', sz.get())])
        self.imagetk = PhotoImage(self.image)
        self.imgcanvas.itemconfigure(self.cnvimg, image=self.imagetk)
        self.saveBtn.configure(state='normal')

    def saveImg(self):
        saveas = Askfile(parent=self,
                         title="Save image as...",
                         filetypes=[('PNG Image (*.png)', '*.png'),
                                    ('JPG Image (*.jpg)', '*.jpg')],
                         defaultextension='.png')
        if saveas:
            file = Path(saveas)
            if file.suffix == '.jpg':
                self.image.convert('RGB').save(file)
            else:
                self.image.save(file)

#  ___   _ _____ _
# |   \ /_\_   _/_\
# | |) / _ \| |/ _ \
# |___/_/ \_\_/_/ \_\

    def buildData(self):
        self.dataFrm = Frame(self.dataScrl)
        self.dataFrm.grid(column=0,
                          row=0)
        addBtn = Button(master=self.dataScrl,
                        text="Add Category",
                        command=self.addInner)
        addBtn.grid(column=0,
                    row=1,
                    sticky='w',
                    padx=3,
                    pady=3)
        self.addInner()

    def addInner(self, name: str = None) -> O[tuple[Frame, Entry]]:
        def remInner():
            frm.destroy()
            self.datadict.pop(Entry)

        frm = Frame(master=self.dataFrm)
        frm.grid()
        remBtn = Button(master=frm,
                        text='Delete',
                        style='sm.TButton',
                        command=remInner)
        remBtn.grid(column=0,
                    row=0,
                    sticky='ne',
                    pady=3)
        ent = Entry()
        lfrm = LFrame(master=frm,
                      labelwidget=ent,
                      bd=3,
                      padx=5,
                      pady=5)
        lfrm.grid(column=1,
                  row=0,
                  sticky='w')
        subfrm = Frame(master=lfrm)
        subfrm.grid(column=0,
                    row=0)
        addBtn = Button(master=lfrm,
                        text="Add Subcategory",
                        command=(lambda a=(subfrm, ent): self.addMid(*a)))
        addBtn.grid(column=0,
                    row=1,
                    sticky='w',
                    padx=3,
                    pady=3)
        self.datadict[ent] = dict()
        self.dataScrl.redraw()
        if name:
            ent.insert(0, name)
            return (subfrm, ent)
        else:
            self.addMid(subfrm, ent)

    def addMid(self, parent: Frame, key: Entry, name: str = None) -> O[tuple[Frame, Entry]]:
        def remMid():
            frm.destroy()
            self.datadict[key].pop(ent)

        frm = Frame(master=parent)
        frm.grid()
        remBtn = Button(master=frm,
                        text='Delete',
                        style='sm.TButton',
                        command=remMid)
        remBtn.grid(column=0,
                    row=0,
                    sticky='ne',
                    pady=3)
        ent = Entry()
        lfrm = LFrame(master=frm,
                      labelwidget=ent,
                      bd=3,
                      padx=5,
                      pady=5)
        lfrm.grid(column=1,
                  row=0,
                  sticky='w')
        subfrm = Frame(master=lfrm)
        subfrm.grid(column=0,
                    row=0)
        addBtn = Button(master=lfrm,
                        text="Add Item",
                        command=(lambda a=(subfrm, key, ent): self.addOuter(*a)))
        addBtn.grid(column=0,
                    row=1,
                    sticky='w',
                    padx=3,
                    pady=3)
        self.datadict[key][ent] = list()
        self.dataScrl.redraw()
        if name:
            ent.insert(0, name)
            return (subfrm, ent)
        else:
            self.addOuter(subfrm, key, ent)

    def addOuter(self, parent: Frame, key: Entry, val: Entry, name: str = '') -> None:
        def remOuter():
            frm.destroy()
            i = self.datadict[key][val].index(ent)
            self.datadict[key][val].pop(i)

        frm = Frame(master=parent,
                    pady=1)
        frm.grid()
        remBtn = Button(master=frm,
                        text='Delete',
                        style='sm.TButton',
                        command=remOuter)
        remBtn.grid(column=0,
                    row=0,
                    sticky='ne',
                    pady=3)
        ent = Entry(master=frm)
        ent.insert(0, name)
        ent.grid(column=1,
                 row=0,
                 sticky='w',
                 padx=3,
                 pady=3)
        self.datadict[key][val].append(ent)
        self.dataScrl.redraw()

    def getData(self):
        self.dataset = {
            inr.get(): {
                mid.get(): [
                    out.get() for out in items]
                for mid, items in sub.items()}
            for inr, sub in self.datadict.items()}

        #   ___   _   _  ___   ___   ___
        #  / __| /_\ | \| \ \ / /_\ / __|
        # | (__ / _ \| .` |\ V / _ \\__ \
        #  \___/_/ \_\_|\_| \_/_/ \_\___/

    def buildCanvas(self, parent):
        self.imgcanvas = Canvas(master=parent,
                                width=1440,
                                height=1440)
        self.imgcanvas.pack()
        self.cnvimg = self.imgcanvas.create_image(0, 0, anchor='nw')
        self.image = None
        self.imagetk = None
