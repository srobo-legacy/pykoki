#!/usr/bin/env python

from pykoki import *

WIDTH = 800
HEIGHT = 600
DEFAULT_RES = (WIDTH, HEIGHT)

koki = PyKoki()

cam = koki.open_camera( "/dev/video0" )

cam.format = koki.v4l_create_YUYV_format(WIDTH, HEIGHT)
actual_res = cam.format.fmt.pix

res = (actual_res.width, actual_res.height)

if res != DEFAULT_RES:
    # If we force the use of a resolution which isn't supported then
    # libkoki will seg-fault during the greyscale conversion.
    tpl = "Warning: default resolution {0} not supported. Using {1} instead."
    print(tpl.format(DEFAULT_RES, res))
    WIDTH, HEIGHT = res

cam.prepare_buffers(1)
cam.start_stream()

def width_from_code(code):

    if code <= 100:
        code -= 100

    if code <= 27:
        return 0.25 * (10.0/12.0) #0.25 is printed width, inc. white border

    return 0.1 * (10.0/12.0)


params = CameraParams(Point2Df(WIDTH/2, HEIGHT/2),
                      Point2Df(571, 571),
                      Point2Di(WIDTH, HEIGHT))


try:
    while True:
        frame = cam.get_frame()
        print "frame"

        img = koki.v4l_YUYV_frame_to_grayscale_image(frame, WIDTH, HEIGHT)

        markers = koki.find_markers_fp(img, width_from_code, params)

        for m in markers:
            print "Code: %d, %s, distance: %f" % (m.code,
                                                  m.bearing,
                                                  m.distance)

        koki.image_free(img)

except KeyboardInterrupt:
    cam.stop_stream()
