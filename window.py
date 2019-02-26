#!/usr/bin/env python
# -*- coding:utf8 -*-
import os,sys
import matplotlib
matplotlib.use("Qt4Agg")
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.image as mpimg
import random, re

# Personnal modules
from drag import DraggablePoint

# set initial 4 points
x1=800
y1=100

x2=500
y2=200

x3=300
y3=300

x4=200
y4=500

class Window(QWidget):
    imgIndex = 0

    def __init__(self,path):
        super(Window,self).__init__()
        img_path = os.getcwd()+ '/' +path

        # a figure instance to plot on
        self.figure = Figure(tight_layout=True)
        self.axes = self.figure.add_subplot(111)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sizePolicy)        
        self.canvas.updateGeometry()

        # To store the draggable polygon
        self.list_points = []

        # To store img path
        self.list_img_path = []
#        self.loadImg(os.getcwd()+"/data/train/1492635012549702766")
        self.loadImg(img_path)

        # plot background image
        self.plotBackGround(img_path,True)

        # Just some button connected to `plot` method
        loadImgButton = QPushButton('Load Image')
        loadImgButton.clicked.connect(lambda: self.plotBackGround(img_path))

        curPosButton = QPushButton('Show current position')
        curPosButton.clicked.connect(self.showPosition)

#        addLaneButton = QPushButton('Add new Lane')
#        addLaneButton.clicked.connect(self.addNewLine)
        addLaneButton = QComboBox()
        addLaneButton.addItems(["--Select line type--","White line", "White dash line", "Yellow line"])
        addLaneButton.activated.connect(self.addNewLine)

        delLaneButton = QPushButton('Del last Lane')
        delLaneButton.clicked.connect(self.delLastLine)

        saveImgButton = QPushButton('Save as png')
        saveImgButton.clicked.connect(self.savePng)

        saveTextButton = QPushButton('Save as text')
#        saveTextButton.clicked.connect(self.disconnect)

        # Prepare a group button
        upperLayout = QHBoxLayout()
        upperLayout.addWidget(loadImgButton)
        upperLayout.addWidget(curPosButton)
        upperLayout.addWidget(addLaneButton)

        lowerLayout = QHBoxLayout()
        lowerLayout.addWidget(delLaneButton)
        lowerLayout.addWidget(saveImgButton)
        lowerLayout.addWidget(saveTextButton)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(upperLayout)
        layout.addLayout(lowerLayout)
        self.setLayout(layout)

    def plotBackGround(self,img_path,flag=False):
        ''' Plot background method '''
        # clean up list points
        if self.list_points:
            self.butdisconnect()
            self.list_points = []

        if self.imgIndex == len(self.list_img_path):
            print 'Reach the end of file'
            self.imgIndex = len(self.list_img_path)-1

#        path = os.getcwd()+ "/data/train/1492635012549702766/" + self.list_img_path[self.imgIndex]
        path = img_path + "/" + self.list_img_path[self.imgIndex]

        img = mpimg.imread(path)
        height, width, channels = img.shape
        self.resize(width,height)

        if flag:
            self.pyt = self.axes.imshow(img)
        else:
            self.pyt.set_data(img)

        # Edit window title
        self.setWindowTitle(self.list_img_path[self.imgIndex])
        self.canvas.draw()

        # increase img index
        self.imgIndex += 1

    def plotDraggablePoints(self, lineType, lineColor, rd):
        ''' Plot and define the 2 draggable points of the baseline '''
        verts = [(x1+rd, y1),(x2+rd, y2),(x3+rd, y3),(x4+rd, y4),]
        codes = [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', edgecolor=lineColor, lw=3, linestyle=lineType)

        self.axes.add_patch(patch)

        dr = DraggablePoint(patch)
        self.list_points.append(dr)

    def loadImg(self,directory):
        ''' store img name to list dict '''
        for filename in sorted(os.listdir(directory), key=lambda x:int(x[:-4])):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                self.list_img_path.append(filename)
            else:
                sys.exit("Filename not end with .jpg or .png")

    def showPosition(self):
        ''' display current 4 points position '''
        for pts in self.list_points:
            print pts.get_position()
        print ""

    def addNewLine(self,select):
        ''' add a new line points to figure '''
        rd = random.randint(10,99)
        lineType = ''
        lineColor = ''

        if select == 1:
            lineType = '-'
            lineColor = 'r'
        elif select == 2:
            lineType = '--'
            lineColor = 'r'
        elif select == 3:
            lineType = '-'
            lineColor = 'b'

        if select != 0:
            self.plotDraggablePoints(lineType,lineColor,rd)
            self.butconnect()

    def delLastLine(self):
        ''' del the last line points to figure '''
        if self.list_points:
            self.butdisconnect()
            self.list_points[-1].line.remove()
            self.list_points.pop()
            self.butconnect()

        if self.axes.patches:
            self.axes.patches[-1].remove()


    def butconnect(self):
        ''' connect current DraggablePoints '''
        for pts in self.list_points:
            pts.connect()
        self.canvas.draw()

    def butdisconnect(self):
        ''' disconnect current DraggablePoints '''
        for pts in self.list_points:
            pts.disconnect()
        self.canvas.draw()

    def savePng(self):
        ''' save current figure to png '''
        self.figure.savefig('test.png')

    def onclick(self,event):
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)

    def UI(self,path):
        self.label = QLabel(self)
        self.pixmap = QPixmap(os.getcwd()+"/data/train/1492635012549702766/12.jpg")
        self.label.setPixmap(self.pixmap)
        self.resize(self.pixmap.width(),self.pixmap.height())
        self.label.mousePressEvent = self.getPos
        self.show()

    def getPos(self,event):
        x = event.pos().x()
        y = event.pos().y()
        print 'Click',(x,y)


def genWindow(path):
    app = QApplication(sys.argv)
    window = Window(path)
    window.show()
    sys.exit(app.exec_())

