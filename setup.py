#!/usr/bin/env python
from distutils.core import setup

setup( name = "pykoki", 
       version = "0.0.1",
       requires = ["ctypes","v4l2",],
       packages = ["pykoki"],

       author = "Chris Kirkham",
       author_email = "chrisjameskirkham@gmail.com",
       url="https://www.studentrobotics.org/trac/wiki/libkoki",
)
