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
import numpy as np
import cv2


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
    imgIndex = -1
    saveFlag = True

    def __init__(self,path):
        super(Window,self).__init__()
        self.img_path = os.getcwd()+ '/' +path

        # a figure instance to plot on
        self.figure = Figure(tight_layout=True, dpi=96)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_axis_off()
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)


        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setSizePolicy(sizePolicy)        
        self.canvas.updateGeometry()

        # To store the draggable polygon
        self.list_points = []
        self.list_points_type = []

        # To store img path
        self.list_img_path = []
        self.loadImg(self.img_path)

        # To generate output path
        if not os.path.exists(self.img_path+"label_txt"):
            os.makedirs(self.img_path+"label_txt")

        if not os.path.exists(self.img_path+"label_png"):
            os.makedirs(self.img_path+"label_png")

        # plot background image
        self.plotBackGround(self.img_path,0,True)

        # Just some button connected to `plot` method
        loadImgButton = QPushButton('Load Image')
        loadImgButton.clicked.connect(lambda: self.plotBackGround(self.img_path,0))

        preImgButton = QPushButton('Pre Image')
        preImgButton.clicked.connect(lambda: self.plotBackGround(self.img_path,1))

        curPosButton = QPushButton('Show current position')
        curPosButton.clicked.connect(self.showPosition)

        addLaneButton = QComboBox()
        addLaneButton.addItems(["--Select line type--","White line", "White dash line", "Yellow line"])
        addLaneButton.activated.connect(self.addNewLine)

        delLaneButton = QPushButton('Del last Lane')
        delLaneButton.clicked.connect(self.delLastLine)

        saveButton = QPushButton('Save')
        saveButton.clicked.connect(lambda: self.saveAll(self.img_path))

        # Prepare a group button
        upperLayout = QHBoxLayout()
        upperLayout.addWidget(loadImgButton)
        upperLayout.addWidget(preImgButton)
        upperLayout.addWidget(curPosButton)
        upperLayout.addWidget(addLaneButton)

        lowerLayout = QHBoxLayout()
        lowerLayout.addWidget(delLaneButton)
        lowerLayout.addWidget(saveButton)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(upperLayout)
        layout.addLayout(lowerLayout)
        self.setLayout(layout)

    def plotBackGround(self,img_path,action,isFirst=False):
        ''' Plot background method '''
        isPlot = True
        isEdge = False

        if not isFirst:
            # if not saved, popup message box
            if self.imgIndex == len(self.list_img_path):
                self.saveFlag = self.isPosNotChange(img_path,self.imgIndex-1)
            else:
                self.saveFlag = self.isPosNotChange(img_path,self.imgIndex)

            if not self.saveFlag:
                isPlot = self.msgBoxEvent()

        if isPlot:
            # increase img index
            if action == 0 and self.imgIndex < len(self.list_img_path):
                if self.imgIndex == -1 and isFirst == False :    # boundary scenario
                    self.imgIndex += 1
                self.imgIndex += 1
            elif action == 1 and self.imgIndex > -1:
                if self.imgIndex == len(self.list_img_path):
                    self.imgIndex -= 1
                self.imgIndex -= 1

            if self.imgIndex == len(self.list_img_path) or (isFirst == False and self.imgIndex == -1):
                isEdge = self.msgBoxReachEdgeEvent()

            if not isEdge:
                # clean up list points
                while self.list_points:
                    self.delLastLine()

                path = img_path + "/" + self.list_img_path[self.imgIndex]
                img = mpimg.imread(path)
                height, width, channels = img.shape
                self.resize(width,height)

                if isFirst:
                    self.pyt = self.axes.imshow(img)
                else:
                    self.pyt.set_data(img)

                # initial (x,y) position in image range
                global x1,y1,x2,y2,x3,y3,x4,y4
                x_range = width - 0
                y_range = height - 0

                # Divide into six equal segments
                x1,x2,x3,x4 = x_range*(4.0/6), x_range*(3.0/6), x_range*(2.0/6), x_range*(1.0/6)
                y1,y2,y3,y4 = y_range*(1.0/6), y_range*(2.0/6), y_range*(3.0/6), y_range*(4.0/6)

                # Produce an height*width black basemap
                self.basemap = np.zeros([height,width,1], dtype=np.uint8)

                # If label text exist, draw previous output
                isLabel = self.isLabelExist(img_path,self.imgIndex)
                if not isLabel and not isFirst:
                    self.isLabelExist(img_path,self.imgIndex-1)

                # Edit window title
                self.setWindowTitle(self.list_img_path[self.imgIndex])
                self.canvas.draw()

    def plotDraggablePoints(self, lineType, lineColor):
        ''' Plot and define the 2 draggable points of the baseline '''
        verts = [(x1, y1),(x2, y2),(x3, y3),(x4, y4),]
        codes = [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', edgecolor=lineColor, lw=3, linestyle=lineType)

        self.axes.add_patch(patch)

        dr = DraggablePoint(patch)
        self.list_points.append(dr)

    def loadImg(self,directory):
        ''' store img name to list dict '''
        try:
            img_directory = [i for i in os.listdir(directory) if not os.path.isdir(os.path.join(directory, i))]
            if not img_directory:
                sys.exit("No such images to be founded!")

            for filename in sorted(img_directory, key=lambda x:int(x[:-4])):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    self.list_img_path.append(filename)
                else:
                    sys.exit("Filename not end with .jpg or .png")
        except Exception as e:
            sys.exit(str(e))

    def showPosition(self):
        ''' display current 4 points position '''
        for lineType, pts in zip(self.list_points_type,self.list_points):
            print lineType,pts.get_position()
        print ""

    def addNewLine(self,select):
        ''' add a new line points to figure '''
        lineType = ''
        lineColor = ''

        if select == 1:
            lineType = '-'
            lineColor = 'r'
            self.list_points_type.append('White')
        elif select == 2:
            lineType = '--'
            lineColor = 'r'
            self.list_points_type.append('WhiteDash')
        elif select == 3:
            lineType = '-'
            lineColor = 'b'
            self.list_points_type.append('Yellow')

        if select != 0:
            self.plotDraggablePoints(lineType,lineColor)
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

        if self.list_points_type:
            self.list_points_type.pop()


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

    def savePng(self,inputName,outputName):
        ''' save current figure to png '''
#        self.figure.savefig('test.png',bbox_inches='tight', pad_inches = 0)
        with open(inputName+".txt", "r") as text_file:
            text_line = [text_line.rstrip('\n') for text_line in text_file]

        curvepoints = 20
        thickness = 3
        for item in text_line:
            pos = item.split(',')
            line_type, pos = pos[0],pos[1:]
            nodes = self.bezierCurve(pos,curvepoints)
            nodes = nodes.reshape((-1, 1, 2))

            if line_type == 'White':
                cv2.polylines(self.basemap, [nodes], False, (255, 0, 0), thickness)
            elif line_type == 'WhiteDash':
                cv2.polylines(self.basemap, [nodes], False, (200, 0, 0), thickness)
            elif line_type == 'Yellow':
                cv2.polylines(self.basemap, [nodes], False, (150, 0, 0), thickness)

#            cv2.imshow('image',self.basemap)

        cv2.imwrite(outputName, self.basemap)
#        x = cv2.imread(outputName)
#        print x[np.nonzero(x)]

    def saveText(self,outputName):
        ''' save line type and positions to txt '''
        with open(outputName+".txt", "w") as text_file:
            for lineType, pts in zip(self.list_points_type,self.list_points):
                pos = pts.get_position()
                text_file.write("%s," % lineType)
                for index, (x,y) in enumerate(pos):
                    text_file.write("%s,%s" % (x,y))
                    if index != len(pos)-1:
                        text_file.write(",")
                text_file.write("\n")

        self.saveFlag = True

    def saveAll(self,img_path):
        ''' save text and save png '''
        ind = self.imgIndex
        if self.imgIndex == len(self.list_img_path):
            ind = ind - 1

        if self.imgIndex == -1:
            ind = ind + 1

        f1 = img_path+"label_txt/"+self.list_img_path[ind][:-4]
        f2 = img_path+"label_png/"+self.list_img_path[ind][:-4]+".png"
        self.saveText(f1)
        self.savePng(f1,f2)

    def msgBoxEvent(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle('WARNING')
        msgBox.setText( "Your changes have not been saved.\nAre you sure you want to discard the changes?" )
        msgBox.setInformativeText( "Press OK to continue, or Cancel to stay on the current page." )
        msgBox.addButton( QMessageBox.Ok )
        msgBox.addButton( QMessageBox.Cancel )

        msgBox.setDefaultButton( QMessageBox.Cancel )
        ret = msgBox.exec_()

        if ret == QMessageBox.Ok:
            if self.imgIndex == len(self.list_img_path):
                self.saveFlag = False
            else:
                self.saveFlag = True
            return True
        else:
            return False

    def msgBoxReachEdgeEvent(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle('WARNING')
        msgBox.setText( "Reach the end of image" )
        msgBox.setInformativeText( "Press OK to continue" )
        msgBox.addButton( QMessageBox.Ok )

        msgBox.setDefaultButton( QMessageBox.Ok )
        ret = msgBox.exec_()

        if ret == QMessageBox.Ok:
            return True
        else:
            return False

    def isPosNotChange(self,img_path,index):
        # load label txt
        fileName = img_path+"label_txt/"+self.list_img_path[index][:-4]+".txt"
        lab = []
        labnp = np.array(lab)
        curnp = np.array(lab)
        try:
            with open(fileName, 'r') as f:
                x = f.read().splitlines()
                for line in x:
                    select,xstr1,ystr1,xstr2,ystr2,xstr3,ystr3,xstr4,ystr4 = line.split(',')
                    x1,y1,x2,y2,x3,y3,x4,y4 = float(xstr1),float(ystr1),float(xstr2),float(ystr2),float(xstr3),float(ystr3),float(xstr4),float(ystr4)
                    lab.append([x1,y1,x2,y2,x3,y3,x4,y4])
                labnp = np.array(lab)

        except IOError:
            lab = []

        # current dp
        if self.list_points:
            curnp = self.list_points[0].get_position()
            for pts in range(1,len(self.list_points)):
                curnp = np.vstack((curnp,self.list_points[pts].get_position()))
            curnp = curnp.reshape(-1,8)

        # check xdim
        if labnp.shape[0] != curnp.shape[0]:
            return False

        # check content
        for l in curnp:
            if l not in labnp:
                return False

        return True

    def isLabelExist(self,img_path,index):
        fileName = img_path+"label_txt/"+self.list_img_path[index][:-4]+".txt"
        select = ''
        try:
            with open(fileName, 'r') as f:
                x = f.read().splitlines()
                global x1,y1,x2,y2,x3,y3,x4,y4
                tmpx1, tmpy1, tmpx2, tmpy2, tmpx3, tmpy3, tmpx4, tmpy4 = x1,y1,x2,y2,x3,y3,x4,y4
                for line in x:
                    select,xstr1,ystr1,xstr2,ystr2,xstr3,ystr3,xstr4,ystr4 = line.split(',')
                    x1,y1,x2,y2,x3,y3,x4,y4 = float(xstr1),float(ystr1),float(xstr2),float(ystr2),float(xstr3),float(ystr3),float(xstr4),float(ystr4)

                    if select == 'White':
                        lineType = 1
                    elif select == 'WhiteDash':
                        lineType = 2
                    elif select == 'Yellow':
                        lineType = 3

                    self.addNewLine(lineType)

                x1,y1,x2,y2,x3,y3,x4,y4 = tmpx1, tmpy1, tmpx2, tmpy2, tmpx3, tmpy3, tmpx4, tmpy4
                self.saveFlag = True

            return True
        except IOError:
#            print "Could not read file:", fileName
            return False

    def bezierCurve(self,pos,num=2):
        ''' bezier Curve formula
        X = (1-t)^3A + 3t(1-t)^2B + 3t^2(1-t)C + t^3D
        '''
        x1,y1,x2,y2,x3,y3,x4,y4 = pos
        x1,y1,x2,y2,x3,y3,x4,y4 = float(x1),float(y1),float(x2),float(y2),float(x3),float(y3),float(x4),float(y4)
        T_list = np.arange(0., 1+1./num, 1./num)

        X = [ pow(1-t,3)*x1 + 3*t*pow(1-t,2)*x2 + 3*pow(t,2)*(1-t)*x3 + pow(t,3)*x4 for t in T_list]
        Y = [ pow(1-t,3)*y1 + 3*t*pow(1-t,2)*y2 + 3*pow(t,2)*(1-t)*y3 + pow(t,3)*y4 for t in T_list]
        return np.array(zip(X,Y),dtype=np.int32)

    def closeEvent(self, event):
        if self.imgIndex == len(self.list_img_path):
            self.saveFlag = self.isPosNotChange(self.img_path,self.imgIndex-1)
        else:
            self.saveFlag = self.isPosNotChange(self.img_path,self.imgIndex)

        if not self.saveFlag:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setWindowTitle('WARNING')
            msgBox.setText( "Your changes have not been saved.\nAre you sure you want to discard the changes?" )
            msgBox.setInformativeText( "Press OK to exit, or Cancel to stay on the current page." )
            msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok);
            msgBox.setDefaultButton(QMessageBox.Cancel);
            if msgBox.exec_() == QMessageBox.Ok:
                event.accept()
            else:
                event.ignore()

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

