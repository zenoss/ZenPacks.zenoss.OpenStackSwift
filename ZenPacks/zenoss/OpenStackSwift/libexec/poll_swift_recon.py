#!/usr/bin/env python
###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import json
import urllib2

from optparse import OptionParser


class ReconPoller(object):
    host = None
    port = None

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def run(self):
        requests = (
            'async',
            'ringmd5',
            'replication',
            'load',
            'diskusage',
            'unmounted',
            'quarantined',
            )

        output = {'events': []}

        for request in requests:
            url = 'http://%s:%s/recon/%s' % (self.host, self.port, request)
            try:
                body = urllib2.urlopen(url, timeout=30).read()
                output[request] = json.loads(body)
            except (urllib2.HTTPError, urllib2.URLError) as e:
                output['events'].append(dict(
                    summary=str(e), url=url))

                return output

        return output


if __name__ == '__main__':
    parser = OptionParser('Usage: %prog -H <hostname or IP> -p <port>')
    parser.add_option('--host', '-H',
        help='Hostname of IP address of Swift object server')
    parser.add_option('--port', '-p',
        type='int', default=6000,
        help='Listening port for swift-object-server')

    options, args = parser.parse_args()

    if not options.host:
        parser.error('No host specified.')

    poller = ReconPoller(options.host, options.port)
    print poller.run()
