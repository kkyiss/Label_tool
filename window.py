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

# Personnal modules
from drag import DraggablePoint

# set initial 4 points
x1=400
y1=100

x2=300
y2=200

x3=600
y3=450

x4=200
y4=500

class Window(QWidget):
    def __init__(self,img_path):
        super(Window,self).__init__()
        self.setWindowTitle("Images")

        # a figure instance to plot on
        self.figure = Figure(tight_layout=True)
        self.axes = self.figure.add_subplot(111)

        # plot background image
        self.plotBackGround(img_path)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sizePolicy)        
        self.canvas.updateGeometry()

        # Just some button connected to `plot` method
        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # To store the draggable polygon
        self.list_points = []
        self.plotDraggablePoints()

    def plotBackGround(self,img_path):
        img = mpimg.imread(os.getcwd()+"/data/train/1492635012549702766/12.jpg")
#        img = mpimg.imread(os.getcwd()+img_path)
        height, width, channels = img.shape
        self.resize(width,height)
        self.axes.imshow(img)

    def plotDraggablePoints(self):

        """Plot and define the 2 draggable points of the baseline"""
        verts = [(x1, y1),(x2, y2),(x3, y3),(x4, y4),]
        codes = [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', edgecolor='r', lw=3)

        self.axes.add_patch(patch)
        dr = DraggablePoint(patch)
        dr.connect()
        self.list_points.append(dr)

    def plot(self):
        ''' plot current 4 points position'''
        self.canvas.draw()
        print self.list_points[0].get_position()
#        self.figure.canvas.mpl_connect('button_press_event', self.onclick)

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

