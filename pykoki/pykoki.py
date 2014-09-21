
from ctypes import *
import os
import v4l2
import cv2

from .opencv_pytypes import IplImageType

KOKI_MARKER_GRID_WIDTH = 10

### GLib structs ###

# GLib 'primitive' datatypes
class gchar_p(c_char_p): pass
class guint(c_uint): pass
class gpointer(c_void_p): pass


class GArray(Structure):
    "A glib GArray"
    _fields_ = [("data", gchar_p), ("len", guint)]


class GSList(Structure):
    "A glib GSList"
    pass
GSList._fields_ = [("data", gpointer), ("next", POINTER(GSList))]

class GPtrArray(Structure):
    "A glib GPtrArray"
    _fields_ = [("pdata", POINTER(gpointer)), ("len", guint)]


class Bearing(Structure):
    _fields_ = [("x", c_float), ("y", c_float), ("z", c_float)]

    def __repr__(self):
        return "Bearing (x=%f, y=%f, z=%f)" % (self.x, self.y, self.z)


class Point2Di(Structure):
    _fields_ = [("x", c_uint16), ("y", c_uint16)]

    def __repr__(self):
        return "Point2Di (x=%d, y=%d)" % (self.x.value, self.y.value)


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
    _fields_ = [("code", c_uint8), ("centre", MarkerVertex), ("vertices", MarkerVertex * 4),
                ("rotation_offset", c_float), ("rotation", MarkerRotation),
                ("bearing", Bearing), ("distance", c_float)]

    def __repr__(self):
        return "Marker (\n\tcode=%d,\n\tcentre = %s,\n\tbearing = %s,\n\tdistance=%f,\n\trotation = %s,\n\trotation_offset=%f,\n\tvertices = [\n\t\t%s,\n\t\t%s,\n\t\t%s,\n\t\t%s])" % (self.code, self.centre, self.bearing, self.distance, self.rotation, self.rotation_offset, self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3])


class ClipRegion(Structure):
    _fields_ = [("min", Point2Di), ("max", Point2Di), ("mass", c_uint16)]

    def __repr__(self):
        return "ClipRegion (mass=%d, min = %s, max = %s)" % (self.mass.value, self.min, self.max)


class Cell(Structure):
    _fields_ = [("sum", c_uint), ("num_pixels", c_uint16), ("val", c_uint8)]

    def __repr__(self):
        return "Cell (num_pixels=%d, sum=%d, val=%d)" % (self.num_pixels.value, self.sum, self.val.value)


Grid = (Cell * KOKI_MARKER_GRID_WIDTH) * KOKI_MARKER_GRID_WIDTH

def GridRepr(self):
    ret = "Grid:\n["
    for i in range(KOKI_MARKER_GRID_WIDTH):
        ret += "["
        for j in range(KOKI_MARKER_GRID_WIDTH):
            ret += "(%d, %d, %d),\t" % (self[i][j].num_pixels.value, self[i][j].sum, self[i][j].val.value)
        ret = ret[:-3]
        ret += "],\n "

    ret = ret[:-3]
    ret += "]"
    return ret

Grid.__repr__ = GridRepr


class CameraParams(Structure):
    _fields_ = [("principal_point", Point2Df), ("focal_length", Point2Df), ("size", Point2Di)]

    def __repr__(self):
        return "CameraParams (focal_length = %s, principal_point = %s, size = %s)" % (self.focal_length, self.principal_point, self.size)


class Quad(Structure):
    _fields_ = [("vertices", Point2Df * 4), ("links", POINTER(GSList) * 4)]

    def __repr__(self):
        return "Quad (links = [%s, %s, %s, %s], vertices = [%s, %s, %s, %s])" % (self.links[0], self.links[1], self.links[2], self.links[3], self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3])


class LabelledImage(Structure):
    _fields_ = [("data", POINTER(c_uint16)),  ("w", c_uint16), ("h", c_uint16),
                ("clips", POINTER(GArray)), ("aliases", POINTER(GArray))]

    def __repr__(self):
        return "LabelledImage (aliases = %s, clips = %s, data = %s, w=%s, h=%s)" % (self.aliases, self.clips, self.data, self.w, self.h)


class Buffer(Structure):
    _fields_ = [("length", c_size_t), ("start", POINTER(c_uint8))]

    def __repr__(self):
        return "Buffer (length=%s, start = %s)" % (self.length, self.start)

class LoggerCallbacks(Structure):
    _fields_ = [ ("init", CFUNCTYPE(c_void_p) ),
                 ("log", CFUNCTYPE(c_char_p, c_void_p, c_void_p) ) ]


class Koki(Structure):
    _fields_ = [ ("logger", LoggerCallbacks),
                 ("logger_userdata", c_void_p) ]


WIDTH_FROM_CODE_FUNC = CFUNCTYPE(c_float, c_int)

def cv_ipl_p_extract(pyipl):
    "Extract the IplImage pointer from a PyObject wrapping an IplImage"

    p = cast( c_void_p( id(pyipl) ),
              POINTER( IplImageType ) )

    return p[0].a

class V4LCamera(object):
    def __init__(self, filename, libkoki):
        self.libkoki = libkoki

        self.fd = self.libkoki.koki_v4l_open_cam(filename)

        if self.fd < 0:
            raise Exception("Couldn't open camera '%s'" % (cam_dev))

        self.buffers = None
        self.buffer_count = 0

    def __del__(self):
        self._free_buffers()
        self.libkoki.koki_v4l_close_cam(self.fd)

    @property
    def format(self):
        "The camera's image format"
        return self.libkoki.koki_v4l_get_format(self.fd)

    @format.setter
    def format(self, fmt):
        return self.libkoki.koki_v4l_set_format(self.fd, fmt)

    def start_stream(self):
        "Start streaming from the camera"
        return self.libkoki.koki_v4l_start_stream(self.fd)

    def stop_stream(self):
        "Stop streaming from the camera"
        return self.libkoki.koki_v4l_stop_stream(self.fd)

    def prepare_buffers(self, count_p):
        "Allocate all the buffers required for IO with the camera"
        if self.buffers != None:
            self._free_buffers()

        c = c_int(count_p)

        self.buffers = self.libkoki.koki_v4l_prepare_buffers(self.fd, byref(c))
        self.buffer_count = c

    def _free_buffers(self):
        if self.buffers == None:
            return

        self.libkoki.koki_v4l_free_buffers( self.buffers, self.buffer_count )
        self.buffers = None
        self.buffer_count = 0

    def get_frame(self):
        return self.libkoki.koki_v4l_get_frame_array(self.fd, self.buffers)

    def get_control(self, id):
        "Get a V4L2 control value from the camera"
        return self.libkoki.koki_v4l_get_control(self.fd, id)

    def set_control(self, id, value):
        "Set a V4L2 control value on the camera"
        return self.libkoki.koki_v4l_set_control(self.fd, id, value)


class PyKoki:
    def __init__(self, libdir = "../libkoki/lib"):
        self._load_library(libdir)
        self._setup_library()

        # Create ourselves a context
        self.ctx = self.libkoki.koki_new()

    def __del__(self):
        self.libkoki.koki_destroy( self.ctx )

    def _load_library(self, directory):
        libkoki = None

        path = os.path.join(directory, "libkoki.so")

        if os.path.exists(path):
            libkoki = cdll.LoadLibrary(path)

        if libkoki == None:
            raise Exception("pykoki: libkoki.so not found")

        self.libkoki = libkoki

    def _setup_library(self):
        l = self.libkoki

        ### v4l.h ###

        # int koki_v4l_open_cam(const char* filename)
        l.koki_v4l_open_cam.argtypes = [c_char_p]
        l.koki_v4l_open_cam.restype = c_int

        # void koki_v4l_close_cam(int fd)
        l.koki_v4l_close_cam.argtypes = [c_int]

        # struct v4l2_format koki_v4l_get_format()
        l.koki_v4l_get_format.argtypes = [c_int]
        l.koki_v4l_get_format.restype = v4l2.v4l2_format

        # int koki_v4l_set_format(int fd, struct v4l2_format fmt)
        l.koki_v4l_set_format.argtypes = [c_int, v4l2.v4l2_format]
        l.koki_v4l_set_format.restype = c_int

        # struct v4l2_format koki_v4l_create_YUYV_format(unsigned int w, unsigned int h)
        l.koki_v4l_create_YUYV_format.argtypes = [c_uint, c_uint]
        l.koki_v4l_create_YUYV_format.restype = v4l2.v4l2_format

        # void koki_v4l_print_format(struct v4l2_format fmt)
        l.koki_v4l_print_format.argtypes = [v4l2.v4l2_format]

        # koki_buffer_t* koki_v4l_prepare_buffers(int fd, int *count)
        l.koki_v4l_prepare_buffers.argtypes = [c_int, POINTER(c_int)]
        l.koki_v4l_prepare_buffers.restype = POINTER(Buffer)

        # void koki_v4l_free_buffers(koki_buffer_t *buffers, int count)
        l.koki_v4l_free_buffers.argtypes = [ POINTER(Buffer), c_int ]

        # int koki_v4l_start_stream(int fd)
        l.koki_v4l_start_stream.argtypes = [c_int]
        l.koki_v4l_start_stream.restype = c_int

        # int koki_v4l_stop_stream(int fd)
        l.koki_v4l_stop_stream.argtypes = [c_int]
        l.koki_v4l_stop_stream.restype = c_int

        # uint8_t* koki_v4l_get_frame_array(int fd, koki_buffer_t *buffers)
        l.koki_v4l_get_frame_array.argtypes = [c_int, POINTER(Buffer)]
        l.koki_v4l_get_frame_array.restype = POINTER(c_uint8)

        # IplImage *koki_v4l_YUYV_frame_to_RGB_image(uint8_t *frame, uint16_t w, uint16_t h)
        l.koki_v4l_YUYV_frame_to_RGB_image.argtypes = [POINTER(c_uint8), c_uint16, c_uint16]
        l.koki_v4l_YUYV_frame_to_RGB_image.restype = c_void_p

        # IplImage *koki_v4l_YUYV_frame_to_grayscale_image(uint8_t *frame, uint16_t w, uint16_t h)
        l.koki_v4l_YUYV_frame_to_grayscale_image.argtypes = [POINTER(c_uint8), c_uint16, c_uint16]
        l.koki_v4l_YUYV_frame_to_grayscale_image.restype = c_void_p

        # int koki_v4l_get_control(int fd, unsigned int id)
        l.koki_v4l_get_control.argtypes = [c_int, c_uint]
        l.koki_v4l_get_control.restype = c_int

        # int koki_v4l_set_control(int fd, unsigned int id, unsigned int value)
        l.koki_v4l_set_control.argtypes = [c_int, c_uint, c_uint]
        l.koki_v4l_set_control.restype = c_int

        # koki_t* koki_new( void );
        l.koki_new.argtypes = []
        l.koki_new.restype = POINTER(Koki)

        # void koki_destroy( koki_t* koki );
        l.koki_destroy.argtypes = [ POINTER(Koki) ]

        # GPtrArray* koki_find_markers(IplImage *frame, float marker_width,
        #                              koki_camera_params_t *params)
        l.koki_find_markers.argtypes = [ POINTER(Koki), c_void_p, c_float, POINTER(CameraParams) ]
        l.koki_find_markers.restype = POINTER(GPtrArray)


        # GPtrArray* koki_find_markers_fp(IplImage *frame, float (*fp)(int),
        #                                 koki_camera_params_t *params)
        l.koki_find_markers_fp.argtypes = [ POINTER(Koki), c_void_p, WIDTH_FROM_CODE_FUNC, POINTER(CameraParams) ]
        l.koki_find_markers_fp.restype = POINTER(GPtrArray)

        # void koki_markers_free(GPtrArray *markers)
        l.koki_markers_free.argtypes = [POINTER(GPtrArray)]

        # void koki_image_free(IplImage *image)
        l.koki_image_free.argtypes = [c_void_p]

        ### crc12.h ###

        # uint16_t koki_crc12 (uint8_t input)
        l.koki_crc12.argtypes = [c_uint8]
        l.koki_crc12.restype = c_uint16


    def _make_copy(self, o):
        ret = type(o)()
        pointer(ret)[0] = o
        return ret

    def open_camera(self, filename):
        return V4LCamera(filename, self.libkoki)

    def v4l_create_YUYV_format(self, w, h):
        return self.libkoki.koki_v4l_create_YUYV_format(w, h)

    def v4l_print_format(self, fmt):
        self.libkoki.koki_v4l_print_format(fmt)

    def v4l_YUYV_frame_to_RGB_image(self, frame, w, h):
        return self.libkoki.koki_v4l_YUYV_frame_to_RGB_image(frame, w, h)

    def v4l_YUYV_frame_to_grayscale_image(self, frame, w, h):
        return self.libkoki.koki_v4l_YUYV_frame_to_grayscale_image(frame, w, h)

    def image_free(self, img):
        self.libkoki.koki_image_free(img)

    def find_markers(self, image, marker_width, params):
        if isinstance(image, cv2.cv.iplimage):
            image = cv_ipl_p_extract(image)

        markers = self.libkoki.koki_find_markers(self.ctx, image, marker_width, params)

        ret = []

        for i in range(markers.contents.len.value):
            # cast the pointer tp a marker pointer, and append to a list
            # of actual (dereferenced) markers
            marker = cast(markers.contents.pdata[i], POINTER(Marker)).contents
            ret.append(self._make_copy(marker))

        # free the markers -- we only need the Python list
        self.libkoki.koki_markers_free(markers)

        return ret

    def find_markers_fp(self, image, func, params):
        if isinstance(image, cv2.cv.iplimage):
            image = cv_ipl_p_extract(image)

        markers = self.libkoki.koki_find_markers_fp(self.ctx, image, WIDTH_FROM_CODE_FUNC(func), params)

        ret = []

        for i in range(markers.contents.len.value):
            # cast the pointer tp a marker pointer, and append to a list
            # of actual (dereferenced) markers
            marker = cast(markers.contents.pdata[i], POINTER(Marker)).contents
            ret.append(self._make_copy(marker))

        # free the markers -- we only need the Python list
        self.libkoki.koki_markers_free(markers)

        return ret

    def crc12(self, n):
        return self.libkoki.koki_crc12(n)
