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

from Products.ZenRRD.CommandParser import CommandParser


class SwiftRecon(CommandParser):
    eventKey = eventClassKey = 'swift_recon_status'

    def processResults(self, cmd, result):
        # Guard against this parser being used for the wrong command.
        if 'poll_swift_recon' not in cmd.command:
            return

        data = json.loads(cmd.result.output)

        # Error
        # {
        #     'events': [
        #         {
        #             'url': 'http://127.0.0.123:6000/recon/async',
        #             'summary': '<urlopen error timed out>',
        #         },
        #     ],
        # }

        # Success
        # {
        #     'load': {
        #         u'5m': 1.4,
        #         u'1m': 0.69,
        #         u'processes': 21775,
        #         u'tasks': u'2/171',
        #         u'15m': 1.52,
        #     },
        #     'ringmd5': {
        #         u'/etc/swift/object.ring.gz': u'aebd12a3191826d480bd7ffd22b11dcf',
        #         u'/etc/swift/account.ring.gz': u'fad22f0496120fd851ee24ab99744c8c',
        #         u'/etc/swift/container.ring.gz': u'349b7614291d6f294d739d8f22609e92',
        #     },
        #     'quarantined': {
        #         u'objects': 0,
        #         u'accounts': 0,
        #         u'containers': 0,
        #     },
        #     'replication': {
        #         u'object_replication_time': -1,
        #     },
        #     'unmounted': [],
        #     'diskusage': [
        #         {
        #             u'device': u'sdb1',
        #             u'avail': 10663620608,
        #             u'mounted': True,
        #             u'used': 62263296,
        #             u'size': 10725883904,
        #         },
        #     ],
        #     'async': {
        #         u'async_pending': 0,
        #     },
        #     'events': [],
        # }

        for event in data.get('events', []):
            event.update(dict(
                device=cmd.deviceConfig.device,
                component=cmd.component,
                eventKey=self.eventKey,
                severity=cmd.severity,
                eventClassKey=self.eventClassKey,
                ))

            result.events.append(event)

        unmounted_disks = len(data['unmounted'])

        diskUsageMin = None
        diskUsageSum = 0
        diskUsageAvg = 0
        diskUsageMax = None

        for diskusage in data['diskusage']:
            usage = 100 * (float(diskusage['used']) / float(diskusage['size']))
            if diskUsageMin is None or diskUsageMin > usage:
                diskUsageMin = usage

            if diskUsageMax is None or diskUsageMax < usage:
                diskUsageMax = usage

            diskUsageSum += usage

        if len(data['diskUsage']) > 0:
            diskUsageAvg = diskUsageSum / len(data['diskUsage'])

        metrics = dict(
            load1=data['load']['1m'],
            load5=data['load']['5m'],
            load15=data['load']['15m'],
            quarantinedAccounts=data['quarantined']['accounts'],
            quarantinedContainers=data['quarantined']['containers'],
            quarantinedObjects=data['quarantined']['objects'],
            replicationTime=data['replication']['object_replication_time'],
            unmountedDisks=unmounted_disks,
            diskUsageMin=diskUsageMin,
            diskUsageAvg=diskUsageAvg,
            diskUsageMax=diskUsageMax,
            asyncPending=data['async']['async_pending'],
            )

        dp_map = dict([(dp.id, dp) for dp in cmd.points])

        for metric in metrics.keys():
            if metric not in dp_map:
                continue

            result.values.append((dp_map[metric], metrics[metric]))
