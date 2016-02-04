#!/usr/bin/env python

import requests
import time
import json

__author__ = 'rvanleeuwen'
__email__ = 'rvanleeuwen@ebay.com'


class NoCheckData(Exception):
    pass


class NoServerUrl(Exception):
    pass


class PostError(Exception):
    pass


class Client(object):
    """ A client object that can send a result to an ammonitrix server
    """

    def __init__(self, name, interval=300,
                 tags=None, alert_indiviually=True):
        """
        :param name: the name of the object that is measured. Note that this
        can be something else than a servicename.
        :param hostname: optional: the host to tie the name to
        :param interval: interval in seconds to the next expected result
        :return:
        """
        self.name = name
        self.interval = interval
        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self.alert_individually = alert_indiviually
        self.event = None
        self.check_data = None
        self.server_hostname = None
        self.server_port = None
        self.server_path = None
        self.server_protocol = None
        self.server_url = None

    @staticmethod
    def get_timestamp():
        """ get Epoch time in UTC """
        return int(time.time())

    def set_name(self, name):
        self.name = name

    def set_check_data(self, check_data):
        # TODO: sanity checks
        self.check_data = check_data

    def set_tags(self, tags):
        # TODO: sanity checks
        self.tags = tags

    def set_server(self, server_hostname, port=5858, path="data", protocol='https'):
        self.server_hostname = server_hostname
        self.server_port = port
        self.server_path = path
        self.server_protocol = protocol

    def get_server_url(self):
        if self.server_hostname and self.server_port and self.server_path:
            return "{}://{}:{}/{}".format(self.server_protocol,
                                          self.server_hostname,
                                          self.server_port,
                                          self.server_path)
        else:
            raise NoServerUrl

    def create_event(self):
        if not self.check_data or len(self.check_data) == 0:
            raise NoCheckData
        self.event = dict()
        self.event['name'] = self.name
        self.event['timestamp'] = self.get_timestamp()
        self.event['next_timestamp_deadline'] = self.get_timestamp() + \
                                                self.interval
        self.event['alert_individually'] = self.alert_individually
        self.event['check_data'] = self.check_data
        if len(self.tags) > 0:
            self.event['tags'] = self.tags

    def send_result(self):
        self.create_event()
        payload = json.dumps(self.event)
        try:
            r = requests.put(self.get_server_url(), data=payload)
        except Exception as e:
            raise PostError("Error during post: {}".format(e))
        if r.status_code != 201:
            raise PostError("Error during post; status {}".
                            format(r.status_code))
