#!/usr/bin/env python

from pykoki import *

WIDTH = 800
HEIGHT = 600

koki = PyKoki()

camera = koki.open_camera( "/dev/video0" )

camera.fmt = koki.v4l_create_YUYV_format(WIDTH, HEIGHT)

koki.v4l_print_format( camera.fmt )

camera.prepare_buffers(1)
camera.start_stream()

def width_from_code(code):

    if code <= 100:
        code -= 100

    if code <= 27:
        return 0.25 * (10.0/12.0) #0.25 is printed width, inc. white border

    return 0.1 * (10.0/12.0)


params = CameraParams(Point2Df(WIDTH/2, HEIGHT/2),
                      Point2Df(571, 571),
                      Point2Di(WIDTH, HEIGHT))


while True:
    frame = camera.get_frame()

    img = koki.v4l_YUYV_frame_to_RGB_image(frame, WIDTH, HEIGHT)

    markers = koki.find_markers_fp(img, width_from_code, params)

    for m in markers:
        print "Code: %d, %s, distance: %f" % (m.code.value,
                                                       m.bearing,
                                                       m.distance)

    koki.image_free(img)

camera.stop_stream()
