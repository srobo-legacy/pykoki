import ctypes

pyobject_head = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__)]

class IplImage(ctypes.Structure):
    "An IplImage"
    pass

class IplImageType(ctypes.Structure):
    _fields_ = pyobject_head + [ ("a", ctypes.POINTER(IplImage)),
                                 ("data", ctypes.py_object),
                                 ("offset", ctypes.c_size_t) ]
