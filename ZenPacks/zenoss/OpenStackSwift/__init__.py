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

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase


class ZenPack(ZenPackBase):
    """
    Custom ZenPack class to add new zProperties.
    """

    packZProperties = [
        ('zSwiftStoragePort', '6000', 'int'),
        ]
