#!/usr/bin/env python

import cv
import sys

from pykoki import PyKoki, Point2Di, Point2Df, CameraParams

if len(sys.argv) != 2:
    print >>sys.stderr, "opencv_example.py IMG_FILE"
    exit(1)

img = cv.LoadImage( sys.argv[1], cv.CV_LOAD_IMAGE_GRAYSCALE )

koki = PyKoki()

params = CameraParams(Point2Df( img.width/2, img.height/2 ),
                      Point2Df(571, 571),
                      Point2Di( img.width, img.height ))

print koki.find_markers( img, 0.1, params )
