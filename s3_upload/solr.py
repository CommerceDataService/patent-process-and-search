import json

import requests


class SolrException(BaseException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Solr(object):
    def __init__(self, url, core):
        self.url = url
        self.core = core

    def send_request(self, command, data):
        url = "/".join((self.url, "solr", self.core, command))
        headers = {"Content-type": "application/json"}

        rv = requests.post(url, data=data, headers=headers)

        return rv.json()

    def add_field(self, name, type, indexed=True, stored=True, multi_valued=False):
        rq = {'add-field': {
            'name': name,
            'type': type,
            'stored': stored,
            'indexed': indexed,
            "multiValued": multi_valued,
        }}

        rq = json.dumps(rq)

        rv = self.send_request('schema?wt=json', rq)

        if 'errors' in rv:
            raise SolrException(rv['errors'])

        return rv
