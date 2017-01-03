#!/usr/bin/env python

from evdev import InputDevice, ecodes
import sys
import json

import smartthings

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
st = None

if 'smartthings' in config:
    print "Initializing SmartThings"
    cfg = config['smartthings']
    st = smartthings.SmartThings(cfg['host'], cfg['appid'], cfg['token'])

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
            if st and binding.get('handler', '') == 'smartthings':
                p = binding.get('parameters', {})
                st.command(p.get('name_or_id', ''), p.get('command', 'on'), p.get('value', None))

