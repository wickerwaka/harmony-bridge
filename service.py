#!/usr/bin/env python

from evdev import InputDevice, ecodes
import sys
import json

######
# Handlers
import smartthings
import http

handler_cls = {
    'smartthings': smartthings.SmartThings,
    'http': http.Requester
}

handlers = {}

######


def read_config(name):
    try:
        with open(name, 'rt') as fp:
            j = json.load(fp)
    except Exception, e:
        print "Could not load config '%s': %s" % (name, e)
        sys.exit(2)
    return j

if len(sys.argv) != 3:
    print "Usage: %s <config> <device>" % (sys.argv[0], )
    sys.exit(1)

config = read_config(sys.argv[1])

for name, initdata in config.get('handlers', {}).items():
    if name not in handler_cls:
        print "Could not initialize unregistered handler '%s'" % (name,)
        continue

    print "Initializing handler '%s'" % (name,)
    handlers[name] = handler_cls[name].from_config(initdata)

device_name = sys.argv[2]

print "Opening device:", device_name
dev = InputDevice(device_name)

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY and event.value != 0:
        keyname = ecodes.KEY[event.code]
        for binding in config.get('bindings', []):
            bindingkey = binding.get('key', '')
            if bindingkey != keyname:
                continue

            handler_name = binding.get('handler', None)
            if handler_name in handlers:
                print "Running handler '%s' for keypress '%s'" % (handler_name, keyname)
                handlers[handler_name].handle(binding.get('parameters', {}))
            else:
                print "Could not find handler '%s' for keypress '%s'" % (handler_name, keyname)

