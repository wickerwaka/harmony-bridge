#!/usr/bin/env python

from evdev import InputDevice, ecodes
import sys

device_name = sys.argv[1]

print "Opening device:", device_name
dev = InputDevice(device_name)

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        print ecodes.KEY[event.code], event.value

