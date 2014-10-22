#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup( name = "pykoki", 
       version = "0.0.1",
       install_requires = ["v4l2",],
       packages = ["pykoki"],

       author = "Chris Kirkham",
       author_email = "chrisjameskirkham@gmail.com",
       url="https://www.studentrobotics.org/trac/wiki/libkoki",
)
