#!/usr/bin/env python
# -*- coding:utf8 -*-
import os,sys
import matplotlib
matplotlib.use("Qt4Agg")
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.image as mpimg
from matplotlib.lines import Line2D

import random
import numpy as np

# Personnal modules
#from drag import DraggablePoint

# set initial 4 points
x1=400
y1=100

x2=700
y2=400

x3=700
y3=450

x4=200
y4=500


class DraggablePoint:
    lock = None #only one can be animated at a time
    def __init__(self, parent, point, x, y, ind):
        self.point = point
        self.parent = parent
        self.press = None
        self.background = None
        self.x, self.y = x, y

        if ind == 0:
             self.ind = 1
        else:
             self.ind = ind

        if self.parent.list_points:
            line_x = [self.parent.list_points[-1].x, self.x]
            line_y = [self.parent.list_points[-1].y, self.y]
            print line_x,line_y,x,y
            self.line = Line2D(line_x, line_y, color='r', alpha=0.5)
            parent.figure.axes[0].add_line(self.line)


    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)

        if self == self.parent.list_points[self.ind]:
            self.line.set_animated(True)
            if self.ind < len(self.parent.list_points)-1:
                self.parent.list_points[self.ind+1].line.set_animated(True)
        else:
            self.parent.list_points[self.ind].line.set_animated(True)


        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)

        if self == self.parent.list_points[self.ind]:
            axes.draw_artist(self.line)
            if self.ind < len(self.parent.list_points)-1:
                self.parent.list_points[self.ind+1].line.set_animated(True)
                axes.draw_artist(self.parent.list_points[self.ind+1].line) 

        else:
            self.parent.list_points[self.ind].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[self.ind].line)


        self.x = self.point.center[0]
        self.y = self.point.center[1]

        if self == self.parent.list_points[self.ind]:
            line_x = [self.parent.list_points[self.ind-1].x, self.x]
            line_y = [self.parent.list_points[self.ind-1].y, self.y]
            self.line.set_data(line_x, line_y)

            if self.ind < len(self.parent.list_points)-1:
                line_x = [self.x, self.parent.list_points[self.ind+1].x]
                line_y = [self.y, self.parent.list_points[self.ind+1].y]

                self.parent.list_points[self.ind+1].line.set_data(line_x, line_y)                

        else:
            line_x = [self.x, self.parent.list_points[self.ind].x]
            line_y = [self.y, self.parent.list_points[self.ind].y]

            self.parent.list_points[self.ind].line.set_data(line_x, line_y)


        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)

        if self == self.parent.list_points[self.ind]:
            self.line.set_animated(False)
            if self.ind < len(self.parent.list_points)-1:
                self.parent.list_points[self.ind+1].line.set_animated(False)

        else:
            self.parent.list_points[self.ind].line.set_animated(False)


        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

        self.x = self.point.center[0]
        self.y = self.point.center[1]


    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)


class Window(QWidget):
    def __init__(self,path):
        super(Window,self).__init__()
        self.setWindowTitle("Images")

        # a figure instance to plot on
        self.figure = Figure(tight_layout=True)
        self.axes = self.figure.add_subplot(111)

        img = mpimg.imread(os.getcwd()+"/data/train/1492635012549702766/12.jpg")
        self.axes.imshow(img)

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

        # To store the 2 draggable points
        self.list_points = []
#        circles = [patches.Circle((0.32, 0.3), 0.03, fc='r', alpha=0.5),
#               patches.Circle((0.3,0.3), 0.03, fc='g', alpha=0.5)]

#        self.plotDraggablePoints(circles)

#        verts = [(x1, y1),(x2, y2),(x3, y3),(x4, y4),]

#        codes = [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,]

#        path = Path(verts, codes)
#        patch = [patches.PathPatch(path, facecolor='none', lw=2)]


        patch = [patches.Ellipse((x1, y1), 30, 30, fc='r', alpha=0.5, edgecolor='r'),
                 patches.Ellipse((x2, y2), 30, 30, fc='r', alpha=0.5, edgecolor='r'),
                 patches.Ellipse((x3, y3), 30, 30, fc='r', alpha=0.5, edgecolor='r'),
                 patches.Ellipse((x4, y4), 30, 30, fc='r', alpha=0.5, edgecolor='r'),
                ]

        # update reference line
#        self.lineA = Line2D([x1,x2], [y1,y2], color='r', alpha=0.5)
#        self.axes.add_line(self.lineA)

        self.plotDraggablePoints(patch)


    def plotDraggablePoints(self, circles):

        """Plot and define the 2 draggable points of the baseline"""
        i = 0
        verts = [(x1, y1),(x2, y2),(x3, y3),(x4, y4)]
        for circ, vert in zip (circles,verts):
            self.axes.add_patch(circ)
            dr = DraggablePoint(self,circ,vert[0],vert[1],i)
            dr.connect()
            self.list_points.append(dr)
            i+=1

        print self.list_points

    def updateFigure(self):

        """Update the graph. Necessary, to call after each plot"""

        self.draw()

    def onclick(self,event):
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(event.button, event.x, event.y, event.xdata, event.ydata)

    def plot(self):
        ''' plot some random stuff '''
        self.canvas.draw()
        self.figure.canvas.mpl_connect('button_press_event', self.onclick)


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

