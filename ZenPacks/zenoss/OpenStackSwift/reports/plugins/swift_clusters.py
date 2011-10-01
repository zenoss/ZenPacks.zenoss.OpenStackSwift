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

from Products.ZenEvents.browser.EventPillsAndSummaries import getEventPillME


class AbstractBase(object):
    obj = None
    title = None

    def __init__(self, obj):
        self.obj = obj
        self.title = obj.titleOrId()

    @property
    def status(self):
        return getEventPillME(
            self.obj.ZenEventManager, self.obj,
            number=3,
            minSeverity=0,
            showGreen=True,
            prodState=1000)

    @property
    def performance(self):
        return getEventPillME(
            self.obj.ZenEventManager, self.obj,
            number=3,
            minSeverity=0,
            showGreen=True,
            prodState=1000)

    @property
    def capacity(self):
        return getEventPillME(
            self.obj.ZenEventManager, self.obj,
            number=3,
            minSeverity=0,
            showGreen=True,
            prodState=1000)


class Cluster(AbstractBase):
    @property
    def server_types(self):
        for subsystem in self.obj.children():
            yield ServerType(subsystem)


class ServerType(AbstractBase):
    @property
    def members(self):
        for device in self.obj.getSubDevicesGen():
            member = None

            if self.title == 'Object Servers':
                member = ObjectServer(device)

            # TODO: Proxy, Container and Account Servers.

            yield member


class ObjectServer(AbstractBase):
    pass


class swift_clusters:
    def run(self, dmd, args):
        return imap(Cluster, dmd.Systems.OpenStack.Swift.children())
