from ctypes import *
import os


class Bearing(Structure):

    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "Bearing (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)



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



class MarkerVertex(Structure):

    _fields_ = [("image", Point2Df), ("world", Point3Df)]

    def __repr__(self):
        return "Marker Vertex (image = %s, world = %s)" % (self.image, self.world)


class MarkerRotation(Structure):

    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "MarkerRotation (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)



class Marker(Structure):

    _fields_ = [("code", c_int), ("centre", MarkerVertex), ("bearing", Bearing),
                ("distance", c_float), ("rotation", MarkerRotation),
                ("rotation_offset", c_float), ("vertices", MarkerVertex * 4)]

    def __repr__(self):
        return "Marker (\n\tcode=%d,\n\tcentre = %s,\n\tbearing = %s,\n\tdistance=%f,\n\trotation = %s,\n\trotation_offset=%f,\n\tvertices = [\n\t\t%s,\n\t\t%s,\n\t\t%s,\n\t\t%s])" % (self.code, self.centre, self.bearing, self.distance, self.rotation, self.rotation_offset, self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3])



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



