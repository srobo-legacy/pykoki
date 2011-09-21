from ctypes import *
import os

KOKI_MARKER_GRID_WIDTH = 10


### GLib structs ###

# GLib 'primitive' datatypes
class gchar_p(c_char_p): pass
class guint(c_uint): pass
class gpointer(c_void_p): pass


class GArray(Structure):

    _fields_ = [("data", gchar_p), ("len", guint)]


class GSList(Structure): pass
GSList._fields_ = [("data", gpointer), ("next", POINTER(GSList))]



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



class ClipRegion(Structure):

    _fields_ = [("mass", c_int), ("min", Point2Di), ("max", Point2Di)]

    def __repr__(self):
        return "ClipRegion (mass=%d, min = %s, max = %s)" % (self.mass, self.min, self.max)



class Cell(Structure):

    _fields_ = [("num_pixels", c_int), ("sum", c_int), ("val", c_int)]

    def __repr__(self):
        return "Cell (num_pixels=%d, sum=%d, val=%d)" % (self.num_pixels, self.sum, self.val)


Grid = (Cell * KOKI_MARKER_GRID_WIDTH) * KOKI_MARKER_GRID_WIDTH

def GridRepr(self):
    ret = "Grid:\n["
    for i in range(KOKI_MARKER_GRID_WIDTH):
        ret += "["
        for j in range(KOKI_MARKER_GRID_WIDTH):
            ret += "(%d, %d, %d),\t" % (self[i][j].num_pixels, self[i][j].sum, self[i][j].val)
        ret = ret[:-3]
        ret += "],\n "

    ret = ret[:-3]
    ret += "]"
    return ret

Grid.__repr__ = GridRepr



class CameraParams(Structure):

    _fields_ = [("focal_length", Point2Df), ("principal_point", Point2Df), ("size", Point2Di)]

    def __repr__(self):
        return "CameraParams (focal_length = %s, principal_point = %s, size = %s)" % (self.focal_length, self.principal_point, self.size)



class Quad(Structure):

    _fields_ = [("links", POINTER(GSList) * 4), ("vertices", Point2Df * 4)]

    def __repr__(self):

        return "Quad (links = [%s, %s, %s, %s], vertices = [%s, %s, %s, %s])" % (self.links[0], self.links[1], self.links[2], self.links[3], self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3])





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



