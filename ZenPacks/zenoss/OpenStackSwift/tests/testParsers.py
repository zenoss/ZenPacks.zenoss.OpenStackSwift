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

from Products.ZenRRD.CommandParser import ParsedResults
from Products.ZenRRD.zencommand import Cmd, DataPointConfig
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ..parsers.SwiftRecon import SwiftRecon as SwiftReconParser

from .util import loadData


class FakeCmdResult(object):
    exitCode = None
    output = None

    def __init__(self, exitCode, output):
        self.exitCode = exitCode
        self.output = output


class TestParsers(BaseTestCase):
    def _getCmd(self, output_filename):
        cmd = Cmd()

        # DeviceConfig no longer exists as of Zenoss 4.
        try:
            from Products.ZenRRD.zencommand import DeviceConfig
            cmd.deviceConfig = DeviceConfig()
        except ImportError:
            from Products.ZenCollector.services.config import DeviceProxy
            cmd.deviceConfig = DeviceProxy()

        cmd.deviceConfig.device = 'swift'
        cmd.component = 'swift'
        cmd.command = 'poll_swift_recon -H 127.0.0.1'
        cmd.eventClass = '/Status/Swift'
        cmd.eventKey = 'rabbitmq_node_status'
        cmd.result = FakeCmdResult(0, loadData(output_filename))

        metrics = (
            'asyncPending',
            'diskSizeAvg',
            'diskSizeMax',
            'diskSizeMin',
            'diskUsageAvg',
            'diskUsageMax',
            'diskUsageMin',
            'load1',
            'load15',
            'load15PerDisk',
            'load5',
            'pidRate',
            'quarantinedAccounts',
            'quarantinedContainers',
            'quarantinedObjects',
            'replicationTime',
            'runningProcs',
            'totalDisks',
            'totalProcs',
            'unmountedDisks',
            )

        points = []
        for metric in metrics:
            dpc = DataPointConfig()
            dpc.id = metric
            dpc.component = 'swift'
            points.append(dpc)

        cmd.points = points

        return cmd

    def testSwiftReconError(self):
        cmd = self._getCmd('poll_swift_recon_error.json')
        parser = SwiftReconParser()
        results = ParsedResults()
        parser.processResults(cmd, results)

        self.assertEquals(len(results.events), 1)
        self.assertEquals(results.events[0]['severity'], cmd.severity)

        self.assertEquals(len(results.values), 0)

    def testSwiftReconSuccess(self):
        cmd = self._getCmd('poll_swift_recon_success.json')
        parser = SwiftReconParser()
        results = ParsedResults()
        parser.processResults(cmd, results)

        self.assertEquals(len(results.events), 1)
        self.assertEquals(results.events[0]['severity'], 0)

        self.assertEquals(len(results.values), 20)

    def testSwiftReconUnmounted(self):
        cmd = self._getCmd('poll_swift_recon_unmounted.json')
        parser = SwiftReconParser()
        results = ParsedResults()
        parser.processResults(cmd, results)

        self.assertEquals(len(results.events), 1)
        self.assertEquals(results.events[0]['severity'], 0)

        self.assertEquals(len(results.values), 20)

        for dp, value in results.values:
            if dp.id == 'unmountedDisks':
                self.assertEquals(value, 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestParsers))
    return suite
