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

import urllib2

from StringIO import StringIO

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ..libexec.poll_swift_recon import ReconPoller


def mock_urlopen(url, timeout=None):
    """
    Provide fake urllib2.urlopen responses for unit testing the command plugin.
    """
    if url.endswith('/recon/async'):
        return StringIO("""{"async_pending": 0}""")
    elif url.endswith('/recon/ringmd5'):
        return StringIO("""{"/etc/swift/object.ring.gz": "aebd12a3191826d480bd7ffd22b11dcf", "/etc/swift/account.ring.gz": "fad22f0496120fd851ee24ab99744c8c", "/etc/swift/container.ring.gz": "349b7614291d6f294d739d8f22609e92"}""")
    elif url.endswith('/recon/replication'):
        return StringIO("""{"object_replication_time": -1}""")
    elif url.endswith('/recon/load'):
        return StringIO("""{"15m": 1.6299999999999999, "1m": 1.4299999999999999, "5m": 1.51, "processes": 19100, "tasks": "5/176"}""")
    elif url.endswith('/recon/diskusage'):
        return StringIO("""[{"device": "sdb1", "avail": 10663620608, "mounted": true, "used": 62263296, "size": 10725883904}]""")
    elif url.endswith('/recon/unmounted'):
        return StringIO("""[]""")
    elif url.endswith('/recon/quarantined'):
        return StringIO("""{"objects": 0, "accounts": 0, "containers": 0}""")

    raise Exception("Call for unexpected swift-recon endpoint")

# Monkeypatch for testing.
urllib2.urlopen = mock_urlopen


class TestCommandPlugins(BaseTestCase):
    def testPollSwiftRecon(self):
        poller = ReconPoller('127.0.0.1', 6000)
        r = poller.run()

        self.assertEquals(r['async']['async_pending'], 0)

        self.assertEquals(r['replication']['object_replication_time'], -1)

        self.assertEquals(r['load']['1m'], 1.4299999999999999)
        self.assertEquals(r['load']['5m'], 1.51)
        self.assertEquals(r['load']['15m'], 1.6299999999999999)
        self.assertEquals(r['load']['processes'], 19100)
        self.assertEquals(r['load']['tasks'], '5/176')

        self.assertEquals(len(r['diskusage']), 1)

        self.assertEquals(len(r['unmounted']), 0)

        self.assertEquals(r['quarantined']['accounts'], 0)
        self.assertEquals(r['quarantined']['containers'], 0)
        self.assertEquals(r['quarantined']['objects'], 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCommandPlugins))
    return suite
