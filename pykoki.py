from ctypes import *
import os


class Point2Di(Structure):

    _fields_ = [("x", c_int), ("y", c_int)]

    def __repr__(self):
        return "Point2Di (x=%i, y=%i)" % (self.x, self.y)



class Point2Df(Structure):

    _fields_ = [("x", c_float), ("y", c_float)]

    def __repr__(self):
        return "Point2Df (x=%f, y=%f)" % (self.x, self.y)



class Point3Df(Structure):

    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "Point3Df (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)



class PyKoki:

    def __init__(self):

        self._load_library("../libkoki/lib/")



    def _load_library(self, directory):

        libkoki = None

        path = os.path.join(directory, "libkoki.so")

        if os.path.exists(path):
            libkoki = cdll.LoadLibrary(path)

        if libkoki == None:
            raise Exception("pykoki: libkoki.so not found")

        self.libkoki = libkoki



