# coding: utf-8

import os
import thriftpy
import json
import logging
import time

# URLJOIN Python 3 and 2 import compatibilities
try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

from thriftpy.rpc import make_client

logger = logging.getLogger(__name__)


class AccessStatsExceptions(Exception):
    pass


class ServerError(AccessStatsExceptions):
    pass


class ThriftClient(object):
    ACCESSSTATS_THRIFT = thriftpy.load(
        os.path.join(os.path.dirname(__file__))+'/thrift/access_stats.thrift')

    def __init__(self, domain=None):
        """
        Cliente thrift para o Articlemeta.
        """
        self.domain = domain or 'ratchet.scielo.org:11660'
        self._set_address()

    def _set_address(self):

        address = self.domain.split(':')

        self._address = address[0]
        try:
            self._port = int(address[1])
        except:
            self._port = 11660

    @property
    def client(self):

        client = make_client(
            self.ACCESSSTATS_THRIFT.AccessStats,
            self._address,
            self._port
        )

        return client

    def document(self, code, collection=None):
        result = self.client.document(code=code, collection=collection)

        try:
            return json.loads(result)
        except:
            return None

    def search(self, dsl, params):
        """
        Free queries to ES index.

        dsl (string): with DSL query
        params (list): [(key, value), (key, value)]
            where key is a query parameter, and value is the value required for
            parameter, ex: [('size', '0'), ('search_type', 'count')]
        """

        query_parameters = []

        for key, value in params:
            query_parameters.append(
                self.ACCESSSTATS_THRIFT.kwargs(str(key), str(value))
            )

        try:
            result = self.client.search(dsl, query_parameters)
        except self.ACCESSSTATS_THRIFT.ServerError:
            raise ServerError('you may trying to run a bad DSL Query')

        try:
            return json.loads(result)
        except:
            return None
