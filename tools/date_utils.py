#!/usr/bin/env python

import time


def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def current_time_path():
    return time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
