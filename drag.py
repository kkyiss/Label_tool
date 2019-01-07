#!/usr/bin/env python
# -*- coding:utf8 -*-
import numpy as np
import matplotlib.patches as patches

class DraggablePoint:
    showverts = True
    epsilon = 10  # max pixel distance to count as a vertex hit
    def __init__(self,point):
        self.ax = point.axes
        self.point = point
        self.background = None

        x, y = zip(*self.point.get_path().vertices)
        self.line, = self.ax.plot(x, y, marker='o', linestyle='dashed', markerfacecolor='r', color='blue', lw=2, alpha=0.5)
        self._ind = None  # the active vert


    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes != self.point.axes: return
        contains, attrd = self.point.contains(event)
        if not contains: return

        if event.button != 1: return
        if not self.showverts: return
        self._ind = self.get_ind_under_point(event)

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        self.line.set_animated(True)

        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)
        print "press"


    def draw_callback(self, event):
        pass


    def pathpatch_changed(self, point):
        pass


    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = np.asarray(self.point.get_path().vertices)
        xyt = self.point.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)
        ind = d.argmin()

        if d[ind] >= self.epsilon:
            ind = None

        return ind


    def on_release(self, event):
        'on release we reset the press data'

        if event.button != 1:
            return
        self._ind = None


        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        self.line.set_animated(False)
        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()
        print "release"

    def key_press_callback(self, event):
        pass

    def on_motion(self, event):
        if self._ind is None:
            return
        if event.inaxes != self.point.axes: return
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata

        vertices = self.point.get_path().vertices

        vertices[self._ind] = x, y
        self.line.set_data(zip(*vertices))

        canvas = self.point.figure.canvas
        axes = self.point.axes

        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)
        axes.draw_artist(self.line)

        # blit just the redrawn area
        canvas.blit(axes.bbox)
        print "motion"

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)

    def get_position(self):
        return self.point.get_path().vertices
