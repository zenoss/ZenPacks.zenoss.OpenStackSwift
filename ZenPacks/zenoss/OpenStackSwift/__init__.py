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
Custom ZenPack initialization code. All code defined in this module will be
executed at startup time in all Zope clients.
"""

import os

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath


class ZenPack(ZenPackBase):
    """
    ZenPack class to add new zProperties and perform other installation and
    removal tasks.
    """

    packZProperties = [
        ('zSwiftObjectServerPort', '6000', 'int'),
        ]

    def install(self, app):
        super(ZenPack, self).install(app)
        self.symlinkPlugin()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.removePluginSymlink()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlinkPlugin(self):
        os.system('ln -sf %s/poll_swift_recon.py %s/' %
            (self.path('libexec'), zenPath('libexec')))

    def removePluginSymlink(self):
        os.system('rm -f %s/poll_swift_recon.py' % (zenPath('libexec')))
