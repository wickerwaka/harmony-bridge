#! /usr/bin/env python

import requests
import time

class SmartThings:
    def __init__(self, base_url, app_id, access_token):
        self.base_url = base_url
        self.app_id = app_id
        self.access_token = access_token
        self.url = "%s/api/smartapps/installations/%s/" % (self.base_url, self.app_id)
        self.session = requests.Session()
        self.update()

    def _get(self, path, **kwargs):
        params = {}
        params.update(kwargs)
        params.update({'access_token': self.access_token})
        
        url = "%s%s" % (self.url, path)
        r = self.session.get(url, params=params)
        r.raise_for_status()
        return r

    def update(self):
        print "Updating device info"
        self.devices = []
        self.device_by_id = {}
        self.device_by_name = {}
        try:
            r = self._get('devices').json()
        except requests.HTTPError, e:
            print "Update failed:", e
            return

        for root in ['switches', 'hues']:
            devices = r.get(root, [])
            for device in devices:
                commands = device.get('commands', {})
                command_str = ', '.join(commands.keys())
                print "Device '%s' (%s): %s" % (device['name'], device['id'], command_str)
                self.devices.append(device)
                self.device_by_name[device['name']] = device
                self.device_by_id[device['id']] = device
        print "Device info updated"

    def command(self, name_or_id, command, value=None):
        print "Sending command '%s' to '%s', value=%s" % (command, name_or_id, value)
        try:
            device = self.device_by_id[name_or_id]
        except KeyError:
            try:
                device = self.device_by_name[name_or_id]
            except KeyError:
                print "Could not find device '%s'" % (name_or_id, )
                return False

        commands = device.get('commands', {})
        
        try:
            url = commands[command]
        except KeyError:
            print "Could not find command '%s' for device '%s'" % (command, name_or_id)
            return False

        params = {}
        if value is not None:
            params['value'] = value

        r = self.session.put(url, params=params)
        try:
            r.raise_for_status()
        except requests.HTTPError, e:
            print "Could not complete request: ", e

    """ Handler methods """
    @classmethod
    def from_config(cls, initdata):
        return cls(initdata['base_url'], initdata['app_id'], initdata['access_token'])
    
    def handle(self, data):
        return self.command(data.get('name_or_id', ''), data.get('command', 'on'), data.get('value', None))


