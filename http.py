#! /usr/bin/env python

import requests

class Requester:
    def __init__(self):
        self.session = requests.Session()

    """ Handler methods """
    @classmethod
    def from_config(cls, initdata):
        return cls()
    
    def handle(self, data):
        try:
            r = self.session.request(**data)
            print "Sending %s request to %s" % (data['method'], r.url)
            r.raise_for_status()
        except requests.HTTPError, e:
            print "Request failed:", e
            return False
        except requests.ConnectionError, e:
            print "Could not connect to %s: %s" % (data['url'], e)
        return True


