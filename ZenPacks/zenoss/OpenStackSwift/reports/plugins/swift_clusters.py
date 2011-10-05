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

"""
Plugin that feeds data to the Swift Cluster report.
"""

from itertools import imap

from Products.ZenEvents.browser.EventPillsAndSummaries import getEventsURL
from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceOrganizer import DeviceOrganizer


def getWorstPillFromSummary(summary, url):
    pillTemplate = """
        <table class="eventrainbow eventrainbow_cols_1">
            <tr>
                <td class="severity-icon-small %(severity)s %(noevents)s">
                    <a href="%(url)s" target="_top">%(count)s</a>
                </td>
            </tr>
        </table>
        """

    severity_strings = "critical error warning info debug".split()

    i = 0
    for css, acked, unacked in summary:
        total = acked + unacked
        if total < 1:
            i += 1
            continue

        return pillTemplate % dict(
            url=url,
            severity=severity_strings[i],
            noevents='',
            count=total,
        )

    return pillTemplate % dict(
        url=url,
        severity='clear',
        noevents='no-events',
        count=0,
    )


class AbstractBase(object):
    obj = None
    title = None
    device_ids = None

    def __init__(self, obj):
        self.obj = obj
        self.title = obj.titleOrId()

        if isinstance(self.obj, Device):
            self.device_ids = [self.obj.id]
        elif isinstance(self.obj, DeviceOrganizer):
            self.device_ids = [x.id for x in self.obj.getSubDevicesGen()]

    def _getWhere(self, eventClass):
        return "device IN ('%s') AND eventClass LIKE '%s%%'" % (
            "','".join(self.device_ids), eventClass)

    def _getPill(self, eventClass):
        summary = self.obj.ZenEventManager.getEventSummary(
            self._getWhere(eventClass),
            severity=1,
            state=1,
            prodState=300)

        return getWorstPillFromSummary(summary, getEventsURL(self.obj))

    @property
    def swiftStatusPill(self):
        return self._getPill('/Status/Swift')

    @property
    def serverStatusPill(self):
        return self._getPill('/Status/Ping')

    @property
    def portStatusPill(self):
        return self._getPill('/Status/IpService')

    @property
    def processStatusPill(self):
        return self._getPill('/Status/OSProcess')

    @property
    def swiftPerfPill(self):
        return self._getPill('/Perf/Swift')

    @property
    def serverPerfPill(self):
        return self._getPill('/Perf')

    @property
    def portPerfPill(self):
        return self._getPill('/Perf/IpService')

    @property
    def processPerfPill(self):
        return self._getPill('/Perf/OSProcess')

    @property
    def capacity(self):
        return ""


class Cluster(AbstractBase):
    @property
    def server_types(self):
        for subsystem in self.obj.children():
            yield ServerType(subsystem)


class ServerType(AbstractBase):
    @property
    def servers(self):
        for device in self.obj.getSubDevicesGen():
            if self.title == 'Proxy Servers':
                yield ProxyServer(device)
            elif self.title == 'Object Servers':
                yield ObjectServer(device)
            elif self.title == 'Container Servers':
                yield ContainerServer(device)
            elif self.title == 'Account Servers':
                yield AccountServer(device)


class ProxyServer(AbstractBase):
    pass


class AccountServer(AbstractBase):
    pass


class ContainerServer(AbstractBase):
    pass


class ObjectServer(AbstractBase):
    pass


class swift_clusters:
    def run(self, dmd, args):
        return imap(Cluster, dmd.Systems.OpenStack.Swift.children())
