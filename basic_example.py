#!/usr/bin/env python

from __future__ import print_function

from pykoki import CameraParams, Point2Df, Point2Di, PyKoki

WIDTH = 800
HEIGHT = 600

koki = PyKoki()

cam = koki.open_camera( "/dev/video0" )

cam.format = koki.v4l_create_YUYV_format(WIDTH, HEIGHT)

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
        print("frame")

        img = koki.v4l_YUYV_frame_to_grayscale_image(frame, WIDTH, HEIGHT)

        markers = koki.find_markers_fp(img, width_from_code, params)

        for m in markers:
            print("Code: %d, %s, distance: %f" % (m.code,
                                                  m.bearing,
                                                  m.distance))

        koki.image_free(img)

except KeyboardInterrupt:
    cam.stop_stream()
