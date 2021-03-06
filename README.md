# Harmony Bridge

The Harmony series of universal remotes from Logitech are great remotes with support for a lot of devices. I have been using them for ten years and currently own three of them.
The hub-based remotes are able to talk to IP/Wifi devices such as Rokus, Phillips Hue bulbs or Nest thermostats, however they lack support custom network devices.

This project uses the Harmony's Bluetooth keyboard support and a Raspberry Pi 3 to route commands from the remote control to anything that is accessible from a python script, including local and remote HTTP endpoints.

## Setup

This setup assumes a clean installation of Raspbian Jessie Lite: https://www.raspberrypi.org/downloads/raspbian/ (the full version will work fine also). Everything will be installed into /opt/harmony-bridge/ and that path is hardcoded into some of the configuration files. If you are installing it somewhere else you will need to fix up those references. There is nothing Raspberry Pi specific about this software and could be used on any hardware or distribution.

Jessie ships with almost everything we need. The only thing missing is the python `evdev` module and git. Install those by running the following commands:

    sudo apt-get install python-pip python-dev git
    sudo pip install evdev

Clone the repository anywhere you want and link to it from `/opt`

    git clone https://github.com/wickerwaka/harmony-bridge.git
    sudo ln -s $(realpath harmony-bridge) /opt

## Bluetooth Pairing

You need to add a bluetooth keyboard device to your harmony hub (I choose a Windows keyboard since it seems to have the most options) and then pair it with the Pi. The pair procedure using `bluetoothctl` is described well here: https://wiki.archlinux.org/index.php/bluetooth_keyboard. Run `bluetoothctl -a` and then enter the following series of commands:

    power on
    agent KeyboardOnly
    default-agent
    pairable on
    scan on

Eventually a "Harmony Keyboard" device will appear in the device scan list. Copy it's BT-MAC address and then run:

    pair 01:02:03:04:05:06
    trust 01:02:03:04:05:06
    connect 01:02:03:04:05:06
    quit

That's it. The keyboard is now paired and will connect automatically whenever it is present.

## Configuration
The `harmony-bridge.conf.example` shows the basics of the configuration options, rename/copy it to `harmony-bridge.conf` and make some changes. It is a JSON format file split into two main sections. The `handlers` object specifies options for the key event handlers. There are currently two: `http` and `smartthings`. The `http` handler takes no options while the `smartthings` handler is has some specific options that are explained later.

The `bindings` array contains the keys that trigger each action. Parameters can be passed to each handler. For the `http` handler the parameters are passed directly to a `requests.request` call, `method` and `url` need to be provided at a minimum. For the `smartthings` handler you need to provide a device `name_or_id` and a `command`. Some commands (such as a dimmer `setLevel`) take a `value` parameter.


## udev and systemd

The `service.py` script listens for events from a keyboard input device and performs actions based on that. We want this script to start up whenever we detect the Harmony keyboard device. We will do this my using a udev rule that starts a systemd service whenever a new `/dev/input/event*` device is added.

From `/opt/harmony-bridge` run

    sudo ln -sr harmony-bridge@.service /etc/systemd/system
    sudo ln -sr 99-harmony-bridge.rules /etc/udev/rules.d/
    

## SmartThings Integration

In order to easily control SmartThings connected devices (my main reason for doing this) you need to install a smart app that exposes an HTTP endpoint. The `JSON.groovy` file in this repository is a slightly modified version of a similar smart app created by Jesse Newland (https://github.com/jnewland/SmartThings). You will need to import this code into the smartthings IDE, enable OAuth and publish it. Then you can add the smartapp using the SmartThings mobile app and configure what devices you want to expose. Once configured you can select the "Config" option in the smartapp which will display the configuration data that you should add to the `smartthings` section of the `harmony-bridge.conf`. You should treat the `access_token` and `app_id` as private data. If someone has access to those values they will also be able to control your devices!
