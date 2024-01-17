import os
import time
import re
import json

# Tkinter and Tkinter.ttk
from tkinter import *
from tkinter import filedialog
from tkinter.colorchooser import askcolor
# from tkinter.ttk import *

# PIL
from PIL import Image, ImageTk, ImageDraw



mode_to_bpp = {"1":1, "L":8, "P":8, "RGB":24, "RGBA":32, "CMYK":32, "YCbCr":24, "LAB":24, "HSV":24, "I":32, "F":32, "I;16":16}

colorPalette = [(244, 0, 95), (36, 224, 152), (25, 132, 250), (255, 101, 157),
                (249,38,114), (253,151,31), (235, 209, 88), (166,226,46),
                (31, 38, 230), (219, 85, 67), (72, 224, 163), (119, 104, 253),
                (238, 191, 43), (17, 198, 245), (238, 54, 216), (95, 160, 12)]

version = "Version 0.7.1"


def from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code"""
    return "#%02x%02x%02x" % rgb


class ColorCell(Frame):
    """
    Extends class tk.Frame to support a scrollable Frame 
    This class is independent from the widgets to be scrolled and 
    can be used to replace a standard tk.Frame
    """
    def __init__(self, parent, table, index, classId, classColor, active=False, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        self.__parent = parent
        self.__table = table

        self.padX, self.padY = 1, 1

        self.__label1 = Label(self, text= str(index), width=3, bd=0)
        self.__label1.grid(row=index, column=0, sticky="nsew", padx=self.padX, pady=self.padY)
        self.__label1.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))

        self.__label2 = Label(self, text=classId, bd=0)
        self.__label2.grid(row=index, column=1, rowspan=3, sticky="nsew", padx=self.padX, pady=self.padY)
        self.__label2.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))

        self.__label3 = Label(self, text="", bg=from_rgb(classColor), width=5, bd=0)
        self.__label3.grid(row=index, column=2, sticky="nsew", padx=self.padX, pady=self.padY)
        # self.label3.bind("<Double-Button-1>", self.onDoubleClick)
        self.__label3.bind("<Double-Button-1>", lambda event: self.onColorDoubleClick(event, index))

        self.__baseColor = self.__label1.cget('bg')
        self.__activeColor = from_rgb((238, 160, 36)) # "orange" #"red"

        # cell_frame.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        return

    def setStatus(self, status):
        # c = self.cget('bg')
        if status:
            c = self.__activeColor
        else:
            c = self.__baseColor

        self.__label1.configure(bg=c)
        self.__label2.configure(bg=c)

        return    
    
    def onIndexDoubleClick(self, event, index):

        self.__table.setActiveIndex(index)

        return

    def onColorDoubleClick(self, event, index):
        # print("onDoubleClick " + str(index))
        c = self.__label3.cget('bg')
        colors = askcolor(title="Color Chooser", color=c)
        if colors[0] != None and colors[1] != None:
            self.__label3.configure(bg=colors[1])
            colorInt = tuple([int(x) for x in colors[0]])
            self.__table.setColor(index, colorInt)

        return
 

class ColorTable(Frame):

    def __init__(self, master=None, parent=None, colorClasses=None, activeIndex=0):
        # We need the master object to initialize important stuff
        super().__init__(master) # Call tk.Frame.__init__(master)
        self.__master = master # Update the master object after tk.Frame() makes necessary changes to it
        self.__master.geometry('300x400')
        self.__master.title('Color Table')
        self.__master.grid_columnconfigure(0, weight=1)
        self.__master.grid_rowconfigure(0, weight=1)
        # make Esc exit the program
        self.__master.bind('<Escape>', lambda e: self.__master.destroy())

        self.__parent = parent

        # Create our canvas (blue background)
        self.__canvas = Canvas(self.__master, bg="gray") # , width=canvas_width, height=canvas_height)
        self.__canvas.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        self.__frame = Frame(self.__canvas, bg="gray", bd=0, relief="flat")
        self.__frame.grid_columnconfigure(0, weight=1)
        self.__frame_pad = 0
        self.__canvas_frame = self.__canvas.create_window((self.__frame_pad,self.__frame_pad), window=self.__frame, anchor="nw", tags="self.__frame")

        self.__scrollbar = Scrollbar(self.__master)
        # self.__scrollbar.pack(side=RIGHT, fill=Y)
        self.__scrollbar.config(command=self.__canvas.yview)
        self.__scrollbar.grid(row=0, column=1, sticky="nsew")

        # Configures the scrollregion of the Canvas dynamically
        self.__scrollbar.bind("<Configure>", self.onScrollbarConfigure)

        self.__canvas.configure(yscrollcommand=self.__scrollbar.set)
        self.__canvas.bind('<Configure>', self.onCanvasConfigure)

        self.__colorClasses = colorClasses
        self.__activeIndex = activeIndex
        self.__cells = []

        # populate table
        self.populate()
        # set active color
        self.setActiveIndex(self.__activeIndex)

        return

    def __del__(self):
        # print('Destructor called, vehicle deleted.')
        return

    def populate(self):
        """populate table"""

        if self.__colorClasses != None and len(self.__colorClasses) > 0:
            if self.__activeIndex > len(self.__colorClasses):
                self.__activeIndex = 0

            self.__cells = []
            for i, (k, v) in enumerate(self.__colorClasses.items()):
                # c = Cell(self.__frame, index=i, classId=k, colorId=v, bg="#D2E2FB", bd=1, relief="flat")
                c = ColorCell(self.__frame, self, index=i, classId=k, classColor=v, bg="gray", bd=0, relief="flat")
                c.bind("<Double-Button-1>", lambda event: self.onCellDoubleClick(event, i))
                c.grid(row=i, column=0, sticky="nsew", padx=0, pady=0)
                self.__cells.append(c)

        return

    def setActiveIndex(self, index):

        self.__activeIndex = index
        for i, c in enumerate(self.__cells):
            isActive = False
            if i == self.__activeIndex:
                isActive = True
            c.setStatus(isActive)
        
        if self.__parent != None:
            self.__parent.setActiveKey(list(self.__colorClasses)[self.__activeIndex])

        return

    def setColor(self, index, color):
        if self.__parent != None and len(color) == 3:
            self.__parent.setClassColor(list(self.__colorClasses)[index], color)
        return

    def onCellDoubleClick(self, event, index):
        print("Cell: " + str(index))
        return

    def onScrollbarConfigure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))

        return

    def onCanvasConfigure(self, event):
        if self.__canvas.winfo_height() > self.__frame.winfo_height() + (2*self.__frame_pad):
            self.__scrollbar.config(command="")
        else:
            self.__scrollbar.config(command=self.__canvas.yview)

        # self.__canvas.itemconfig(self.__canvas_frame, width = event.width-(2*self.__frame_pad), height=event.height-(2*self.__frame_pad))
        self.__canvas.itemconfig(self.__canvas_frame, width = event.width-(2*self.__frame_pad))

        return


class About(Frame):

    def __init__(self, master=None):
        # We need the master object to initialize important stuff
        super().__init__(master) # Call tk.Frame.__init__(master)
        self.__master = master # Update the master object after tk.Frame() makes necessary changes to it
        self.__master.geometry('300x200')
        self.__master.grid_columnconfigure(0, weight=1)
        self.__master.grid_rowconfigure(0, weight=1)
        self.__master.title("About")
        # make Esc exit the program
        self.__master.bind("<Escape>", lambda e: self.__master.destroy())
        self.__master.bind("<FocusOut>", lambda e: self.__master.destroy())
        # master grid
        # self.grid_columnconfigure(0, weight=1)

        # self grid
        # self.config(anchor=CENTER)
        # self.pack()
        self.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)

        self.__bgColor = self.__master.cget('bg')
        # self.__label = Label(self, text="MECTHO", bg=self.__bgColor, bd=0, relief="flat", anchor=CENTER)
        self.__label1 = Label(self, text="MT SEMSEG LABELER", bg=from_rgb((0, 147, 208)), bd=0, relief="flat", anchor=CENTER)
        self.__label1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.__label2 = Label(self, text=version, bg=from_rgb((238, 160, 36)), bd=0, relief="flat", anchor=CENTER)
        self.__label2.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # self.__label.config(anchor=CENTER)
        # self.__label.pack()
        # self.lblClass = Label(self, text="class:", bd=1, relief=SUNKEN)
        # self.lblClass.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)


        return

    def __del__(self):
        # print('Destructor called, vehicle deleted.')
        return


class InfoBar(Frame):
    """show all into"""
    def __init__(self, parent, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        self.__parent = parent

        self.padX, self.padY = 1, 1

        self.lblClass = Label(self, text="class:", bd=1, relief=SUNKEN)
        self.lblClass.grid(row=0, column=0, sticky="nsew", padx=self.padX, pady=self.padY)
        #self.lblClass.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))

        self.__strClassValue = StringVar(value="")
        self.lblClassValue = Label(self, textvariable=self.__strClassValue, bd=1, anchor="w", relief=SUNKEN)
        self.lblClassValue.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=self.padX, pady=self.padY)

        self.lblFile = Label(self, text="file:", bd=1, relief=SUNKEN)
        self.lblFile.grid(row=0, column=2, sticky="nsew", padx=self.padX, pady=self.padY)
        #self.lblFile.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))

        self.__strFileValue = StringVar(value="")
        self.lblFileValue = Label(self, textvariable=self.__strFileValue, bd=1, anchor="w", relief=SUNKEN)
        self.lblFileValue.grid(row=0, column=3, rowspan=3, sticky="nsew", padx=self.padX, pady=self.padY)

        self.__strFileIndex = StringVar(value="")
        self.lblFileIndex = Label(self, textvariable=self.__strFileIndex, bd=1, relief=SUNKEN)
        self.lblFileIndex.grid(row=0, column=4, sticky="nsew", padx=self.padX, pady=self.padY)
        # self.lblFileIndex.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))
        # self.lblFileIndexValue = Label(self, text="", bd=1, relief=SUNKEN)
        # self.lblFileIndexValue.grid(row=0, column=1, sticky="nsew", padx=self.padX, pady=self.padY)

        self.__strMousePos = StringVar(value="")
        self.lblMousePos = Label(self, textvariable=self.__strMousePos, bd=1, relief=SUNKEN)
        self.lblMousePos.grid(row=0, column=5, sticky="nsew", padx=self.padX, pady=self.padY)
        #self.lblMousePos.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))

        self.__strPixelValue = StringVar(value="")
        self.lblPixelValue = Label(self, textvariable=self.__strPixelValue, bd=1, relief=SUNKEN)
        self.lblPixelValue.grid(row=0, column=6, sticky="nsew", padx=self.padX, pady=self.padY)
        #self.lblMousePos.bind("<Double-Button-1>", lambda event: self.onIndexDoubleClick(event, index))

        self.__strImgSize = StringVar(value="")
        self.lblImgSize = Label(self, textvariable=self.__strImgSize, bd=1, relief=SUNKEN)
        self.lblImgSize.grid(row=0, column=7, sticky="nsew", padx=self.padX, pady=self.padY)
        # self.lblImgSize.bind("<Double-Button-1>", self.onDoubleClick)
        #self.lblImgSize.bind("<Double-Button-1>", lambda event: self.onColorDoubleClick(event, index))

        self.__strImgBpp = StringVar(value="")
        self.lblImgBpp = Label(self, textvariable=self.__strImgBpp, bd=1, relief=SUNKEN)
        self.lblImgBpp.grid(row=0, column=8, sticky="nsew", padx=self.padX, pady=self.padY)

        # cell_frame.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=4)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=4)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(5, weight=1)
        self.grid_columnconfigure(6, weight=1)
        self.grid_columnconfigure(7, weight=1)
        self.grid_columnconfigure(8, weight=1)

        return

    def setClass(self, classId):
        self.__strClassValue.set(classId)
    
        return

    def setFile(self, filePath, index, total, size, bpp):
        self.__strFileValue.set(filePath)
        self.__strFileIndex.set(str(index) + "/" + str(total))

        if len(size) == 2:
            self.__strImgSize.set(str(size[0]) + "x" + str(size[1]))
        
        if bpp > 0:
            self.__strImgBpp.set(str(bpp)+"bpp")

        return
    
    def setMousePos(self, pos, pixel):
        if len(pos) == 2:
            self.__strMousePos.set(str(pos[0]) + ", " + str(pos[1]))
            self.__strPixelValue.set(str(pixel))
    
        return


class MainWindow:

    def __init__(self): #, master = None):
        # self.__master = master
        # object of class Tk, resposible for creating
        # a tkinter toplevel window
        self.__master = Tk()
        self.__master.title('MecTho')
        # self.__master.geometry('750x400')
        self.__master.geometry('800x600')
        # self.__master.config(bg='lightgrey') #(bg='#345')
        # self.__master.config(bg='#345')
        
        self.__startFolder = os.path.dirname(os.path.abspath(__file__))
        self.__maskFileTerm = '_M'
        self.__classFile = "classes.json"
        self.__classes = {}
        self.__classKey = -1
        self.__classesColor = {}
        self.__classesAlpha = 75
        self.__dataFiles = []
        self.__dataIndex = -1

        self.__data = None
        
        self.__maskId = None
        self.__mask = None
        self.__maskUpdated = False

        self.__image = None #Image.open("/home/mectho/Desktop/tk/01/data/test.png")
        self.__imageDisplay = None # self.__image.resize((maxImgW, maxImgH), Image.NONE)
        self.__imageTk = None #ImageTk.PhotoImage(self.__imageDisplay) #(self.__image)
        self.__imageId = None #self.__canvas.create_image(dispX, dispY, image=self.__imageTk, anchor=NW)
        self.__lastImageName = None
        
        self.__layer = None
        self.__layerId = None
        self.__layerColor = (255, 0, 0, 90) #"red"
        self.__layerHide = False

        # history
        self.__historyMask = []
        self.__historyLayer = []
        self.__historyMaxNum = 10 # max number of history data
        self.__historyIndex = -1

        self.__brush = None
        # self.__brushShape = "square"
        self.__brushShape = "circle"
        self.__brushSize = 20
        self.__brushSizeMin = 1
        self.__brushSizeMax = 100
        self.__brushSizeStep = 2
        self.__brushColor = (0, 255, 0) #, 255) #"green"
        self.__brushAlpha = (75,)

        # zoom
        self.__zoomFactor = 1.0
        self.__zoomStep = 0.05
        self.__zoomLowerLimit = 0.01
        self.__zoomUpperLimit = 1.0
        self.__zoomP1 = [0, 0]
        self.__zoomP2 = [0, 0]
        self.__mousePos = [0, 0]
        self.__resetZoom = True

        # mouse 
        self.__mouseLeftBtnPressed = False
        self.__mouseRightBtnPressed = False
        self.__mousePickedPoint = [-1, -1]

        # keyboard
        self.__ctrlPressed = False

        # canvas object to create shape
        self.__canvas = Canvas(self.__master, bg="grey")
        # creating rectangle
        # self.__rectangle = self.__canvas.create_rectangle(self.__recP1.x, self.__recP1.y, 
        #                                               self.__recP2.x, self.__recP2.y, fill = "yellow")
        # self.canvas.pack(anchor=N, fill=BOTH, expand=True, side=LEFT)
        self.__canvasPad = [2, 2]
        self.__canvas.pack(fill=BOTH, expand=YES, padx=self.__canvasPad[0], pady=self.__canvasPad[1])

        # Canvas Events
        self.__canvas.bind("<Configure>", self.__onResize)
        # Moving Mouse Event
        self.__canvas.bind("<Motion>", self.__onMotion)
        # Clicking Mouse Event
        self.__canvas.bind("<Button>", self.__onButtonClick)
        # self.__canvas.bind("<B1-Motion>", self.__on_dragging)
        self.__canvas.bind("<ButtonRelease>", self.__onButtonRelease)
        self.__canvas.bind("<Enter>", self.__onEnter)
        self.__canvas.bind("<Leave>", self.__onLeave)

        # Set up menubar
        self.__menubar = Menu(self.__master) #, bg="grey")
        #
        filemenu = Menu(self.__menubar, tearoff=0)
        # filemenu.add_command(label="New", command=donothing)
        filemenu.add_command(label="Open Folder", command=self.__onFileOpenFolder)
        filemenu.add_command(label="Save", command=self.__onFileSave)
        # filemenu.add_command(label="Save as...", command=donothing)
        # filemenu.add_command(label="Close", command=donothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.__master.quit)
        self.__menubar.add_cascade(label="File", menu=filemenu)
        #
        # editmenu = Menu(self.__menubar, tearoff=0)
        # editmenu.add_command(label="Undo", command=donothing)
        # editmenu.add_separator()
        # editmenu.add_command(label="Cut", command=donothing)
        # editmenu.add_command(label="Copy", command=donothing)
        # editmenu.add_command(label="Paste", command=donothing)
        # editmenu.add_command(label="Delete", command=donothing)
        # editmenu.add_command(label="Select All", command=donothing)
        # self.__menubar.add_cascade(label="Edit", menu=editmenu)
        #
        classmenu = Menu(self.__menubar, tearoff=0)
        classmenu.add_command(label="Open", command=self.__onClassOpen)
        # classmenu.add_separator()
        # classmenu.add_command(label="Cut", command=donothing)
        # classmenu.add_command(label="Copy", command=donothing)
        # classmenu.add_command(label="Paste", command=donothing)
        # classmenu.add_command(label="Delete", command=donothing)
        # classmenu.add_command(label="Select All", command=donothing)
        self.__menubar.add_cascade(label="Class", menu=classmenu)
        #
        helpmenu = Menu(self.__menubar, tearoff=0)
        # helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=self.__onHelpAbout)
        self.__menubar.add_cascade(label="Help", menu=helpmenu)
        # add menu
        self.__master.config(menu=self.__menubar)

        # statusbar
        # self.__stbText = StringVar(value="")
        # self.__statusbar = Label(self.__master, textvariable=self.__stbText, borderwidth=1, relief=SUNKEN, anchor=W)
        # self.__statusbar.pack(side=BOTTOM, fill=X, padx=2, pady=2)

        # infobar
        self.__infoBar = InfoBar(self.__master)
        self.__infoBar.pack(side=BOTTOM, fill=X, padx=2, pady=2)

        self.__colorDialog = None

        # This will bind arrow keys to the tkinter
        # toplevel which will navigate the image or drawing
        # self.__master.bind("<KeyPress-Left>", lambda e: self.on_key_left(e))
        # self.__master.bind("<KeyPress-Right>", lambda e: self.on_key_right(e))
        # self.__master.bind("<KeyPress-Up>", lambda e: self.on_key_up(e))
        # self.__master.bind("<KeyPress-Down>", lambda e: self.on_key_down(e))
        self.__master.bind("<KeyPress>", self.__onKeyPress)
        self.__master.bind("<KeyRelease>", self.__onKeyRelease)

        return

    # utils

    def __canvasToImage(self, x, y):

        pX = -1
        pY = -1
        if(self.__imageId != None):
            bbox = self.__canvas.bbox(self.__imageId)
            if bbox[0] <= x < bbox[2] and bbox[1] <= y < bbox[3]:
                cX, cY = bbox[0], bbox[1]
                cW, cH = bbox[2] - cX + 1, bbox[3] - cY + 1

                iW = self.__zoomP2[0] - self.__zoomP1[0] + 1 
                iH = self.__zoomP2[1] - self.__zoomP1[1] + 1 

                # pX = self.__to_int((x - cX)/cW*iW)+self.__p1[0]
                # pY = self.__to_int((y - cY)/cH*iH)+self.__p1[1]
                pX = int((x - cX)/cW*iW)+self.__zoomP1[0]
                pY = int((y - cY)/cH*iH)+self.__zoomP1[1]

        return pX, pY

    def __imageToCanvas(self, x, y):

        pX = -1
        pY = -1
        if(self.__imageId != None):
            iX = self.__zoomP1[0]
            iY = self.__zoomP1[1]
            iW = self.__zoomP2[0] - self.__zoomP1[0] + 1
            iH = self.__zoomP2[1] - self.__zoomP1[1] + 1
            if iX <= x < iW and iY <= y < iH:
                bbox = self.__canvas.bbox(self.__imageId)
                cX, cY = bbox[0], bbox[1]
                cW, cH = bbox[2] - cX + 1, bbox[3] - cY + 1

                # pX = self.__to_int((x-iX)*cW/iW) + cX
                # pY = self.__to_int((y-iY)*cW/iW) + cY
                pX = int((x-iX)*cW/iW) + cX
                pY = int((y-iY)*cW/iW) + cY

        return pX, pY

    def __drawBrush(self, x=-1, y=-1):
        if x >= 0 and y >= 0 and self.__image != None: 
            # "x" and "y" are referred to "canvas"
            pCX, pCY = self.__canvasToImage(x, y)
            delta = int(self.__brushSize/2)
            p1X, p1Y = pCX - delta, pCY - delta
            p2X, p2Y = pCX + delta, pCY + delta
            # if self.__brushShape == "square":
            #     self.__brush =  self.__canvas.create_rectangle(p1X, p1Y, p2X, p2Y, fill = self.__brushColor, stipple='gray12')
            # elif self.__brushShape == "circle":
            #     self.__brush =  self.__canvas.create_oval(p1X, p1Y, p2X, p2Y, fill = self.__brushColor, stipple='gray12')
            # self.__canvas.move(self.__brushId, x, y)

            shape = self.__brushShape
            if self.__brushSize == 1:
                shape= "circle"

            self.__brush = Image.new("RGBA", self.__image.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(self.__brush, mode=None)
            c1 = self.__brushColor + self.__brushAlpha
            c2 = self.__brushColor + (255,)
            if shape == "square":
                d.rectangle([p1X, p1Y, p2X, p2Y], fill=c1, outline=c2)
            elif shape == "circle":
                d.ellipse([p1X, p1Y, p2X, p2Y], fill=c1, outline=c2)

            bbox = self.__canvas.bbox(self.__imageId)
            cX, cY = bbox[0], bbox[1]
            cW, cH = bbox[2] - cX + 1, bbox[3] - cY + 1

            b = (self.__zoomP1[0], self.__zoomP1[1], self.__zoomP2[0] + 1, self.__zoomP2[1] + 1)
            imageCrop = self.__brush.crop(b)
            imageDisplay = imageCrop.resize((cW, cH), Image.NONE)
            self.__brushTk = ImageTk.PhotoImage(imageDisplay)
            self.__brushId = self.__canvas.create_image(cX, cY, image=self.__brushTk, anchor=NW)

        return
    
    def __updateLayerAndMask(self, action="draw", x=-1, y=-1):
        # "x" and "y" are refered to "canvas"
        pCX, pCY = self.__canvasToImage(x, y)
        delta = int(self.__brushSize/2)
        p1X, p1Y = pCX - delta, pCY - delta
        p2X, p2Y = pCX + delta, pCY + delta

        if action == "draw":
            # color = self.__layerColor #(255, 0, 0, 100)
            # apply alpha channel
            colorLayer = list(self.__classesColor[self.__classKey])
            colorLayer.append(self.__classesAlpha)
            colorLayer = tuple(colorLayer)
            colorMask = self.__classes[self.__classKey]
        elif action == "clear":
            colorLayer = (0, 0, 0, 0)
            colorMask = 0
        else:
            # color = None
            return

        # Draw on layer and mask
        # if not color == None:
        # Creates an object that can be used to draw in the given image.
        d = ImageDraw.Draw(self.__layer, mode=None)

        shape = self.__brushShape
        if self.__brushSize == 1:
           shape= "square"

        if shape == "square":
            d.rectangle([p1X, p1Y, p2X, p2Y], fill=colorLayer, outline=colorLayer)
        elif shape == "circle":
            d.ellipse([p1X, p1Y, p2X, p2Y], fill=colorLayer, outline=colorLayer)

        d = ImageDraw.Draw(self.__mask, mode=None)
        if shape == "square":
            d.rectangle([p1X, p1Y, p2X, p2Y], fill=colorMask, outline=colorMask)
        elif shape == "circle":
            d.ellipse([p1X, p1Y, p2X, p2Y], fill=colorMask, outline=colorMask)

        # useful fot saving data
        self.__maskUpdated = True

        return

    def __drawLayer(self):
        
        if self.__imageId != None:
            bbox = self.__canvas.bbox(self.__imageId)
            cX, cY = bbox[0], bbox[1]
            cW, cH = bbox[2] - cX + 1, bbox[3] - cY + 1

            b = (self.__zoomP1[0], self.__zoomP1[1], self.__zoomP2[0] + 1, self.__zoomP2[1] + 1)
            imageCrop = self.__layer.crop(b)
            imageDisplay = imageCrop.resize((cW, cH), Image.NONE)
            self.__layerTk = ImageTk.PhotoImage(imageDisplay)
            self.__layerId = self.__canvas.create_image(cX, cY, image=self.__layerTk, anchor=NW)

        return

    def __updateImage(self):
        
        if self.__image == None:
            return

        cW = self.__canvas.winfo_width()
        cH = self.__canvas.winfo_height()
        cR = cW/cH
        
        iW = self.__zoomP2[0] - self.__zoomP1[0] + 1
        iH = self.__zoomP2[1] - self.__zoomP1[1] + 1
        iR = iW/iH

        dispW, dispH = 0, 0
        dispX, dispY = 0, 0
        if (cW >= cH and cR >= iR) or (cW < cH and cR >= iR):
            dispW = int(cH*iR)
            dispH = cH
            dispY = 0
            dispX = int((cW - dispW)/2)

        elif (cW >= cH and cR < iR) or (cW < cH and cR < iR):
            dispW = cW
            dispH = int(cW/iR)
            dispY = int((cH - dispH)/2)
            dispX = 0

        b = (self.__zoomP1[0], self.__zoomP1[1], self.__zoomP2[0] + 1, self.__zoomP2[1] + 1)
        image = self.__image.crop(b)
        # image = self.__layer.crop(b)
        # image3 = self.__brush.crop(b)
        # self.__imageDisplay = Image.alpha_composite(image1, image2)
        # self.__imageDisplay = Image.alpha_composite(self.__imageDisplay, image3)
        imageDisplay = image.resize((dispW, dispH), Image.NONE)
        self.__imageTk = ImageTk.PhotoImage(imageDisplay)
        self.__imageId = self.__canvas.create_image(dispX, dispY, image=self.__imageTk, anchor=NW)

        if not self.__layerHide:
            self.__drawLayer()

        if self.__ctrlPressed:
            self.__drawBrush()

        return

    def __maskToLayer(self):
        """create layer image from mask"""
        self.__layer = Image.new("RGBA", self.__image.size, (0, 0, 0, 0))
        for k, v in self.__classes.items():
            threshold = v
            bitmap = self.__mask.point(lambda p: p == threshold and 255)
            # bitmap.save("/home/mectho/Desktop/tk/01/ppp.png")
            color = list(self.__classesColor[k])
            color.append(self.__classesAlpha)
            color = tuple(color)
            self.__layer.paste(color, (0, 0), bitmap)
        return

    # history

    def __cleanHistory(self):
        self.__historyMask.clear()
        self.__historyLayer.clear()
        self.__historyIndex = -1

    def __updateHistory(self):

        if self.__maskUpdated:

            self.__maskUpdated = False

            # se sono andato indietro nella history, cancello la roba successiva all'attuale 
            while self.__historyIndex < len(self.__historyMask)-1 :
                self.__historyMask.pop()
                self.__historyLayer.pop()

            self.__historyMask.append(self.__mask.getdata().copy())
            self.__historyLayer.append(self.__layer.copy())

            if len(self.__historyMask) > self.__historyMaxNum:
                self.__historyMask = self.__historyMask[-self.__historyMaxNum:]
                self.__historyLayer = self.__historyLayer[-self.__historyMaxNum:]

            self.__historyIndex += 1

        return

    def __backwardHistory(self):

        if self.__historyIndex > 0:
            self.__historyIndex -= 1
            self.__mask.putdata( self.__historyMask[self.__historyIndex] )
            self.__layer = self.__historyLayer[self.__historyIndex].copy()

        return
    
    def __forwardHistory(self):

        if self.__historyIndex < len(self.__historyLayer) - 1:
            self.__historyIndex += 1
            self.__mask.putdata( self.__historyMask[self.__historyIndex] )
            self.__layer = self.__historyLayer[self.__historyIndex].copy()
        
        return

    # data

    def __getDataFiles(self, folder, maskFileTerm):

        # output
        dataFiles = []

        validExt = [".bmp", ".dib", ".jpeg", ".jpg", ".jpe", ".jp2", ".png", 
                    ".webp", ".pbm", ".pgm", ".ppm", ".pxm", ".pnm", ".pfm", 
                    ".sr", ".ras", ".tiff", ".tif", ".exr", ".hdr", ".pic"]

        # dataMasks = []
        # get list of files only
        # files = [f for f in os.listdir(folder) 
        #          if os.path.isfile(os.path.join(folder, f))]  # file list only

        for f in os.listdir(folder):
            absFilePath = os.path.join(folder, f)
            fileName, fileExt = os.path.splitext(f)
            if os.path.isfile(absFilePath) and fileExt in validExt:
                # check if the file name does not end with "maskFileTerm" (es. '_M')
                # if not fileName[-2:] == maskFileTerm:
                if not fileName[-len(maskFileTerm):] == maskFileTerm:
                    # dataFiles.append(absFilePath)
                    dataFiles.append(f)

        # for f in files:
        #     # remove extention (with 'os.path.splitext(f)[0]')
        #     fileName = os.path.splitext(f)[0]
        #     if not fileName[-2:] == maskFileTerm:
        #         dataFiles.append(f)

        # remove duplicate (unique)
        dataFiles = list(dict.fromkeys(dataFiles))
        dataFiles.sort()

        # for f in dataFiles:
        #     fileName = os.path.splitext(f)[0]
        #     fileExt = os.path.splitext(f)[1]
        #     fileMask = fileName + m_maskFileTerm + fileExt
        #     if os.path.isfile(fileMask):
        #         dataMasks.append(fileMask)
        #     else:
        #         dataMasks.append("")


        # Windows bitmaps - *.bmp, *.dib (always supported)
        # JPEG files - *.jpeg, *.jpg, *.jpe (see the Note section)
        # JPEG 2000 files - *.jp2 (see the Note section)
        # Portable Network Graphics - *.png (see the Note section)
        # WebP - *.webp (see the Note section)
        # Portable image format - *.pbm, *.pgm, *.ppm *.pxm, *.pnm (always supported)
        # PFM files - *.pfm (see the Note section)
        # Sun rasters - *.sr, *.ras (always supported)
        # TIFF files - *.tiff, *.tif (see the Note section)
        # OpenEXR Image files - *.exr (see the Note section)
        # Radiance HDR - *.hdr, *.pic (always supported)
        # Raster and Vector geospatial data supported by GDAL (see the Note section)

        return dataFiles #, dataMasks

    def __findDuplicate(self, x):
        ret = []
        # intilize an empty list
        unique = []
        # Check for elements
        for v in x:
            # check if exists in unq_list
            if v in unique and v not in ret:
                ret.append(v)
            else:
                unique.append(v)

        return ret

    def __findInvalid(self, x):
        ret = []
        for e in x:
            if not isinstance(e, int):
                ret.append(e)
            else:
                if e < 0:
                    ret.append(e)

        return ret

    def __readData(self): # , fileData, maskFileTerm): #, maskThreshold):

        # output
        res, img, mask = False, None, None

        # dataFile = self.__dataFiles[self.__dataIndex]
        # dataFolder = self.__dataFolder
        imageName = self.__dataFiles[self.__dataIndex]
        imagePath = os.path.join(self.__dataFolder, imageName)
        maskFileTerm = self.__maskFileTerm

        if os.path.isfile(imagePath):
            # read image file
            try:
                # img = cv2.imread(fileData)
                img = Image.open(imagePath) #, format="RGB") #.convert("RGBA")
                # se è un'immagine in float
                if img.mode == 'F':
                    # prendo il minimo e il massimo
                    minDepth = min(img.getdata())
                    maxDepth = max(img.getdata())
                    # la normalizzo
                    normalizedDepthData = [(value - minDepth) / (maxDepth - minDepth) * 255 for value in img.getdata()]
                    # rimpiazzo il data dell'immagine
                    img.putdata(normalizedDepthData)
            except: 
                img = None

            if img is not None:
                # search the mask file
                imageExt = os.path.splitext(imagePath)[1]
                imageName = imageName[ : imageName.rfind('_') ]

                # se il nome dell'immagine è differente dal precedente
                if imageName != self.__lastImageName:
                    self.__resetZoom = True
                else:
                    self.__resetZoom = False
                #  sovrascrivo il last
                self.__lastImageName = imageName

                maskPath = os.path.join(self.__dataFolder, imageName + maskFileTerm + imageExt )
                # se il file non esiste
                if not os.path.isfile(maskPath):
                    newMask = Image.new("L", img.size, 0)
                    newMask.save(maskPath)
                # read mask image
                try: 
                    # mask = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)
                    mask = Image.open(maskPath) #, format="L")
                    if mask.mode != "L":
                        mask = None 
                    else:
                        res = True
                except:
                    mask = None

            else:
                res, img, mask = False, None, None

            self.__data = img
            self.__mask = mask

        return res #, img, mask

    def __initDisplayData(self):
        self.__image = self.__data.convert("RGBA")
        #self.__layer = Image.new("RGBA", self.__image.size, (0, 0, 0, 0))
        # reset zoom
        if self.__resetZoom:
            self.__zoomFactor = 1.0
            self.__zoomP1 = [0, 0]
            self.__zoomP2 = [self.__image.width - 1, self.__image.height - 1]
            self.__resetZoom = False

        self.__layer = Image.new("RGBA", self.__image.size, (0, 0, 0, 0))
        for k, v in self.__classes.items():
            threshold = v
            bitmap = self.__mask.point(lambda p: p == threshold and 255)
            # bitmap.save("/home/mectho/Desktop/tk/01/ppp.png")
            color = list(self.__classesColor[k])
            color.append(self.__classesAlpha)
            color = tuple(color)
            self.__layer.paste(color, (0, 0), bitmap)

        return

    # menu events

    def __onFileOpenFolder(self):

        dataFolder = filedialog.askdirectory(master=self.__master, title='Select data folder', initialdir = self.__startFolder)
        
        # check if folder exists
        if not os.path.isdir(dataFolder):
            # error message
            return
        
        # check if class file exists
        classFile = os.path.join(dataFolder, self.__classFile)
        if not os.path.isfile(classFile):
            # check if default file exists
            classFile = os.path.join(os.getcwd(), self.__classFile)
            if not os.path.isfile(classFile):
                # error message
                return

        # get class dictionary
        classes = {}
        validJson = True
        try:
            with open(classFile) as f:
                classes = json.load(f)
            validJson = True
        except ValueError:
            validJson = False #print("error loading JSON")

        if not validJson:
            # error message
            return
        
        # check all classes
        # find duplicate keys
        dk = self.__findDuplicate(list(classes.keys()))
        if len(dk) > 0:
            # error message
            return

        # find duplicate values
        dv = self.__findDuplicate(list(classes.values()))
        if len(dv) > 0:
            # error message
            return

        # find invalid values
        di = self.__findInvalid(list(classes.values()))
        if len(di) > 0:
            # error message
            return

        self.__dataFolder = dataFolder
        self.__startFolder = dataFolder
        self.__classes = classes
        self.__classKey = list(self.__classes)[0]
        # set class color
        for i, k in enumerate(self.__classes):
            self.__classesColor[k] = colorPalette[i]

        # get file list
        self.__dataFiles = self.__getDataFiles(self.__dataFolder, self.__maskFileTerm)
        if self.__dataFiles == 0:
            # error message
            return

        self.__dataIndex = 0
        
        # Read data
        #f = self.__dataFiles[self.__dataIndex]
        res = self.__readData() #f, self.__maskFileTerm) #, self.__maskThreshold)
        if not res:
            # error message
            return

        # init display data
        self.__initDisplayData()
        self.__cleanHistory()
        self.__maskUpdated = True
        self.__updateHistory()
        self.__updateImage()

        # set info
        self.__infoBar.setClass(self.__classKey)
        f = self.__dataFiles[self.__dataIndex]
        i = self.__dataIndex + 1
        t = len(self.__dataFiles)
        s = self.__data.size
        b = mode_to_bpp[self.__data.mode]
        self.__infoBar.setFile(f, i, t, s, b)

        return

    def __onFileSave(self):

        if self.__mask == None:
            return
        self.__mask.save(self.__mask.filename)

        return

    def __onClassOpen(self):
        if len(self.__classesColor) > 0:
            if self.__colorDialog == None:
                self.__colorDialog = Toplevel(self.__master)
                app = ColorTable(self.__colorDialog, self, colorClasses=self.__classesColor)
            else:
                self.__colorDialog.destroy()
                self.__colorDialog = None

        return

    def __onHelpAbout(self):
        self.__aboutDialog = Toplevel(self.__master)
        app = About(self.__aboutDialog)
        return

    # canvas events

    def __onResize(self, event):
        
        self.__updateImage()
        # self.__drawLayer()
        # if self.__ctrlPressed:
        #     self.__drawBrush()

        return

    # canvas mouse events

    def __onMotion(self, event):

        # Pan
        if self.__mouseLeftBtnPressed and not self.__mouseRightBtnPressed and not self.__ctrlPressed:
            if self.__mousePickedPoint[0] >= 0 and self.__mousePickedPoint[1] >= 0:

                imgW = self.__image.width
                imgH = self.__image.height

                mX, mY = self.__canvasToImage(event.x, event.y)
                dX = mX - self.__mousePickedPoint[0]
                dY = mY - self.__mousePickedPoint[1]

                zoomX1, zoomY1 = self.__zoomP1[0], self.__zoomP1[1]
                zoomX2, zoomY2 = self.__zoomP2[0], self.__zoomP2[1]
                zoomW = zoomX2 - zoomX1 + 1
                zoomH = zoomY2 - zoomY1 + 1

                # P1
                zoomX1 -= dX
                if zoomX1 < 0: 
                    zoomX1 = 0
                zoomY1 -= dY
                if zoomY1 < 0: 
                    zoomY1 = 0
                # P2
                zoomX2 = zoomX1 + zoomW - 1
                if zoomX2 >= imgW:
                    zoomX2 = imgW - 1
                    zoomX1 = zoomX2 - (zoomW - 1)
                zoomY2 = zoomY1 + zoomH - 1
                if zoomY2 >= imgH:
                    zoomY2 = imgH - 1
                    zoomY1 = zoomY2 - (zoomH - 1)
                
                # update
                self.__zoomP1 = [zoomX1, zoomY1]
                self.__zoomP2 = [zoomX2, zoomY2]

                self.__updateImage()

        # elif self.__mouseLeftBtnPressed == False and self.__ctrlPressed == True:
        #     # self.__updateBrush("draw", event.x, event.y)
        #     debug = 0

        # draw layer 
        elif self.__mouseLeftBtnPressed and not self.__mouseRightBtnPressed and self.__ctrlPressed == True:
            #self.__updateBrush("draw", event.x, event.y)
            self.__updateLayerAndMask("draw", event.x, event.y)
            self.__drawLayer()
            self.__drawBrush(event.x, event.y)

        # clear layer
        elif not self.__mouseLeftBtnPressed and self.__mouseRightBtnPressed and self.__ctrlPressed == True:
            #self.__updateBrush("draw", event.x, event.y)
            self.__updateLayerAndMask("clear", event.x, event.y)
            self.__drawLayer()
            self.__drawBrush(event.x, event.y)

        elif not self.__mouseLeftBtnPressed and not self.__mouseRightBtnPressed and self.__ctrlPressed == True:
            #self.__updateBrush("draw", event.x, event.y)
            # self.__updateLayer("clear", event.x, event.y)
            # self.__drawLayer()
            self.__drawBrush(event.x, event.y)

        else:

            pCX, pCY = self.__canvasToImage(event.x, event.y)
            if 0 <= pCX < self.__image.width or 0 <= pCY < self.__image.height:
                pixel=self.__data.getpixel((pCX, pCY))
                self.__infoBar.setMousePos((pCX, pCY), pixel)
                # self.__stbText.set("(" + str(pCX) + ", " + str(pCY) + ") = " + str(pixel) + " - class=" + self.__classKey)

        return

    def __onButtonClick(self, event): # Clicking

        # left mouse button pressed
        if event.num == 1:
            self.__mouseLeftBtnPressed = True
            # save picked point for pan
            # iX, iY = self.__canvasToImage(event.x, event.y)
            # self.__mousePickedPoint = [iX, iY]
            self.__mousePickedPoint = self.__canvasToImage(event.x, event.y)
            if self.__ctrlPressed == True:
                self.__updateLayerAndMask("draw", event.x, event.y)
                self.__drawLayer()

        # right mouse button pressed
        elif event.num == 3:
            self.__mouseRightBtnPressed = True
            self.__mousePickedPoint = self.__canvasToImage(event.x, event.y)
            if self.__ctrlPressed == True:
                self.__updateLayerAndMask("clear", event.x, event.y)
                self.__drawLayer()
            else:
                self.__layerHide = not self.__layerHide
                self.__updateImage()
                

        # zoom with wheel
        elif event.num == 4 or event.num == 5:

            # if an image is not present
            if(self.__imageId == None):
                return

            imgW = self.__image.width
            imgH = self.__image.height

            iX, iY = self.__canvasToImage(event.x, event.y)

            if self.__ctrlPressed == False :
                # respond to Linux or Windows wheel event
                if event.num == 4: # or event.delta == 120:
                    # scroll down
                    self.__zoomFactor = self.__zoomFactor - self.__zoomStep
                    if self.__zoomFactor < self.__zoomLowerLimit:
                        self.__zoomFactor = self.__zoomLowerLimit
                elif event.num == 5: # or event.delta == -120:
                    # scroll up
                    self.__zoomFactor = self.__zoomFactor + self.__zoomStep
                    if self.__zoomFactor > self.__zoomUpperLimit:
                        self.__zoomFactor = self.__zoomUpperLimit

                x1, y1 = -1, -1
                x2, y2 = -1, -1
                if self.__zoomFactor == 1.0:
                    x1, y1 = 0, 0
                    x2, y2 = imgW-1, imgH-1
                else:
                    imgWNew, imgHNew = int(self.__zoomFactor*imgW), int(self.__zoomFactor*imgH)

                    bbox = self.__canvas.bbox(self.__imageId)
                    cX, cY = bbox[0], bbox[1]
                    cW, cH = bbox[2] - cX + 1, bbox[3] - cY + 1

                    # P1
                    x1 = iX - int((event.x - cX)/cW*imgWNew)
                    if x1 < 0: x1 = 0
                    y1 = iY - int((event.y - cY)/cH*imgHNew)
                    if y1 < 0: y1 = 0
                    # P2
                    x2 = x1 + imgWNew - 1
                    if x2 >= imgW:
                        x2 = imgW - 1
                        x1 = x2 - imgWNew
                    y2 = y1 + imgHNew - 1
                    if y2 >= imgH:
                        y2 = imgH - 1
                        y1 = y2 - imgHNew

                self.__zoomP1 = [x1, y1]
                self.__zoomP2 = [x2, y2]
                self.__updateImage()
            # if ctrl pressed
            else:
                # scroll up
                if event.num == 5:
                    self.__brushSize = self.__brushSize - self.__brushSizeStep
                    if self.__brushSize < self.__brushSizeMin:
                        self.__brushSize = self.__brushSizeMin
                # scroll down
                elif event.num == 4:
                    self.__brushSize = self.__brushSize + self.__brushSizeStep
                    if self.__brushSize > self.__brushSizeMax:
                        self.__brushSize = self.__brushSizeMax
                
                # get mouse position
                x = self.__canvas.winfo_pointerx() - self.__canvas.winfo_rootx() # + self.__canvasPad[0]
                y = self.__canvas.winfo_pointery() - self.__canvas.winfo_rooty() # + self.__canvasPad[1]
                self.__drawBrush(x, y)

        return 

    def __onButtonRelease(self, event):
        # print("mouse dragging: " + str(event.num) + ", " + str(event.time))
        
        # left mouse button released
        if event.num == 1:
            self.__mouseLeftBtnPressed = False
            # remove picked point
            self.__mousePickedPoint = None
            self.__updateHistory()

        # right mouse button released
        elif event.num == 3:
            self.__mouseRightBtnPressed = False
            self.__mousePickedPoint = None
            self.__updateHistory()

        return

    def __onEnter(self, event):
        # print("mouse enter: " + str(event.num) + ", " + str(event.time))
        return

    def __onLeave(self, event):
        # print("mouse leave: " + str(event.num) + ", " + str(event.time))
        return

    # keyboard events

    def __onKeyPress(self, event):

        if event.keysym == "Control_R" or event.keysym == "Control_L":
            self.__ctrlPressed = True
            # get mouse position
            x = self.__canvas.winfo_pointerx() - self.__canvas.winfo_rootx() # + self.__canvasPad[0]
            y = self.__canvas.winfo_pointery() - self.__canvas.winfo_rooty() # + self.__canvasPad[1]
            self.__drawBrush(x, y)

        # undo ( ctrl + z )
        elif event.keysym == "z" and self.__ctrlPressed == True:
            self.__backwardHistory()
            self.__drawLayer()
        elif event.keysym == "Z" and self.__ctrlPressed == True:
            self.__forwardHistory()
            self.__drawLayer()
        
        # open ColorTable ( space )
        elif event.keysym == "space" and self.__ctrlPressed == False:
            if len(self.__classesColor) > 0:
                if self.__colorDialog == None:
                    self.__colorDialog = Toplevel(self.__master)
                    app = ColorTable(self.__colorDialog, self, colorClasses=self.__classesColor)
                else:
                    self.__colorDialog.destroy()
                    self.__colorDialog = None
        
        # open new image
        elif self.__ctrlPressed == False and event.keysym in ["Right", "Left", "d", "a"]:
            if len(self.__dataFiles) > 0:

                # save mask
                self.__onFileSave()

                if event.keysym in ["Right", "d"]:
                    self.__dataIndex = self.__dataIndex + 1
                    if self.__dataIndex > len(self.__dataFiles)-1:
                        self.__dataIndex = 0
                elif event.keysym in ["Left", "a"]:
                    self.__dataIndex = self.__dataIndex - 1
                    if self.__dataIndex < 0:
                        self.__dataIndex = len(self.__dataFiles)-1
            
                # read data
                res = self.__readData() #f, self.__maskFileTerm) #, self.__maskThreshold)
                if res:
                    # init display data
                    self.__initDisplayData()
                    self.__cleanHistory()
                    self.__maskUpdated = True
                    self.__updateHistory()
                    self.__updateImage()

                    # set file info
                    f = self.__dataFiles[self.__dataIndex]
                    i = self.__dataIndex + 1
                    t = len(self.__dataFiles)
                    s = self.__data.size
                    b = mode_to_bpp[self.__data.mode]
                    self.__infoBar.setFile(f, i, t, s, b)

        # hide/show layer ( ctrl + h )
        elif event.keysym == "h" and self.__ctrlPressed == True:
            self.__layerHide = not self.__layerHide
            self.__updateImage()

        # reduce/increase the size of the brush 
        elif event.keysym == "plus" or event.keysym == "minus" or \
             event.keysym == "KP_Add" or event.keysym == "KP_Subtract" and self.__ctrlPressed == True:
            
            if event.keysym == "plus" or event.keysym == "KP_Add":
                self.__brushSize = self.__brushSize + self.__brushSizeStep
                if self.__brushSize > self.__brushSizeMax:
                    self.__brushSize = self.__brushSizeMax
            elif event.keysym == "minus" or event.keysym == "KP_Subtract":
                self.__brushSize = self.__brushSize - self.__brushSizeStep
                if self.__brushSize < self.__brushSizeMin:
                    self.__brushSize = self.__brushSizeMin
            
            # get mouse position
            x = self.__canvas.winfo_pointerx() - self.__canvas.winfo_rootx() # + self.__canvasPad[0]
            y = self.__canvas.winfo_pointery() - self.__canvas.winfo_rooty() # + self.__canvasPad[1]
            self.__drawBrush(x, y)

        # change the shape of the brush ( ctrl + . )
        elif event.keysym == "period" and self.__ctrlPressed == True:
            
            if self.__brushShape == "square":
                self.__brushShape = "circle"
            else:
                self.__brushShape = "square"
           
            # get mouse position
            x = self.__canvas.winfo_pointerx() - self.__canvas.winfo_rootx() # + self.__canvasPad[0]
            y = self.__canvas.winfo_pointery() - self.__canvas.winfo_rooty() # + self.__canvasPad[1]
            self.__drawBrush(x, y)

        return

    def __onKeyRelease(self, event):
        # print("Release: " + event.keysym)
        if event.keysym == 'Control_R' or event.keysym == 'Control_L':
            self.__ctrlPressed = False
            
            if not self.__layerHide:
                self.__drawLayer()

            if self.__brush != None:
                self.__canvas.delete(self.__brushId)
                #self.__brush = None
            
        return

    def start(self):
        self.__master.mainloop()
        return

    def setActiveKey(self, key):
        self.__classKey = key
        # update info
        self.__infoBar.setClass(self.__classKey)
        return
    
    def setClassColor(self, classId, color):
        if classId in list(self.__classes.keys()):
            self.__classesColor[classId] = color
            self.__maskToLayer()
            self.__updateImage()

        return


def main():

    win = MainWindow()
    win.start()

# MAIN
if __name__ == "__main__":

    main()


# PILLOW Pixel Type
# https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes

# 1 (1-bit pixels, black and white, stored with one pixel per byte)
# L (8-bit pixels, black and white)
# P (8-bit pixels, mapped to any other mode using a color palette)
# RGB (3x8-bit pixels, true color)
# RGBA (4x8-bit pixels, true color with transparency mask)
# CMYK (4x8-bit pixels, color separation)
# YCbCr (3x8-bit pixels, color video format)
# LAB (3x8-bit pixels, the L*a*b color space)
# HSV (3x8-bit pixels, Hue, Saturation, Value color space)
# I (32-bit signed integer pixels)
# F (32-bit floating point pixels)

# LA (L with alpha)
# PA (P with alpha)
# RGBX (true color with padding)
# RGBa (true color with premultiplied alpha)
# La (L with premultiplied alpha)
# I;16 (16-bit unsigned integer pixels)
# I;16L (16-bit little endian unsigned integer pixels)
# I;16B (16-bit big endian unsigned integer pixels)
# I;16N (16-bit native endian unsigned integer pixels)
# BGR;15 (15-bit reversed true colour)
# BGR;16 (16-bit reversed true colour)
# BGR;24 (24-bit reversed true colour)
# BGR;32 (32-bit reversed true colour)