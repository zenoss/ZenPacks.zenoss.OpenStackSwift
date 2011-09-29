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
        if 'poll_swift_recon' not in cmd.command:
            return

        data = None
        try:
            data = json.loads(cmd.result.output)
        except ValueError:
            result.events.append(dict(
                device=cmd.deviceConfig.device,
                component=cmd.component,
                eventKey=self.eventKey,
                severity=cmd.severity,
                eventClassKey=self.eventClassKey,
                summary='failed to parse response from swift-recon',
                message=cmd.result.output,
                ))

        if 'events' in data:
            for event in data['events']:
                result.events.append(dict(
                    device=cmd.deviceConfig.device,
                    component=cmd.component,
                    eventKey=self.eventKey,
                    severity=cmd.severity,
                    eventClassKey=self.eventClassKey,
                    **event
                    ))
        else:
            result.events.append(dict(
                device=cmd.deviceConfig.device,
                component=cmd.component,
                eventKey=self.eventKey,
                severity=0,
                eventClassKey=self.eventClassKey,
                summary='swift-recon connectivity restored',
                ))

        metrics = {}

        if 'async' in data:
            metrics['asyncPending'] = data['async'].get('async_pending', None)

        if 'replication' in data:
            metrics['replicationTime'] = \
                data['replication'].get('object_replication_time', None)

        if 'load' in data:
            metrics['load1'] = data['load'].get('1m', None)
            metrics['load5'] = data['load'].get('5m', None)
            metrics['load15'] = data['load'].get('15m', None)
            metrics['pidRate'] = data['load'].get('processes', None)

            process_parts = data['load'].get('tasks', '').split('/')
            if len(process_parts) == 2:
                metrics['runningProcs'] = int(process_parts[0])
                metrics['totalProcs'] = int(process_parts[1])

        if 'diskusage' in data:
            diskSizeSum = 0
            diskUsageSum = 0

            metrics['diskSizeMin'] = None
            metrics['diskSizeMax'] = None
            metrics['diskUsageMin'] = None
            metrics['diskUsageMax'] = None

            for diskusage in data.get('diskusage', []):
                if metrics['diskSizeMin'] is None or \
                    metrics['diskSizeMin'] > diskusage['size']:
                    metrics['diskSizeMin'] = diskusage['size']

                if metrics['diskSizeMax'] is None or \
                    metrics['diskSizeMax'] < diskusage['size']:
                    metrics['diskSizeMax'] = diskusage['size']

                usage = 100 * (
                    float(diskusage['used']) / float(diskusage['size']))

                if metrics['diskUsageMin'] is None or \
                    metrics['diskUsageMin'] > usage:
                    metrics['diskUsageMin'] = usage

                if metrics['diskUsageMax'] is None or \
                    metrics['diskUsageMax'] < usage:
                    metrics['diskUsageMax'] = usage

                diskUsageSum += usage

            if len(data['diskusage']) > 0:
                metrics['totalDisks'] = len(data['diskusage'])
                metrics['diskSizeAvg'] = diskSizeSum / metrics['totalDisks']
                metrics['diskUsageAvg'] = diskUsageSum / metrics['totalDisks']
            else:
                metrics['totalDisks'] = 0

        if 'unmounted' in data:
            metrics['unmountedDisks'] = len(data['unmounted'])

        if 'quarantined' in data:
            metrics['quarantinedAccounts'] = \
                data['quarantined'].get('accounts', None)

            metrics['quarantinedContainers'] = \
                data['quarantined'].get('containers', None)

            metrics['quarantinedObjects'] = \
                data['quarantined'].get('objects', None)

        if 'load15' in metrics and 'totalDisks' in metrics:
            metrics['load15PerDisk'] = \
                metrics['load15'] / metrics['totalDisks']

        dp_map = dict([(dp.id, dp) for dp in cmd.points])

        for metric in metrics.keys():
            if metric not in dp_map:
                continue

            result.values.append((dp_map[metric], metrics[metric]))
