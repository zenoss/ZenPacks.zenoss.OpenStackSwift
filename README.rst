ZenPacks.zenoss.OpenStackSwift
==============================
This project is a [Zenoss][] extension (ZenPack) that allows for monitoring of
Swift. Swift is the project name for the Object Store in OpenStack.

From the [Swift project site][]:

> Swift is a highly available, distributed, eventually consistent object/blob
> store. Organizations can use Swift to store lots of data efficiently,
> safely, and cheaply.

Requirements & Dependencies
---------------------------
This ZenPack is known to be compatible with Zenoss versions 3.2 through 4.0.

All of the monitoring currently performance is done through the optional
swift-recon API endpoint that can be enabled on all of your Swift object
servers. Before using this ZenPack you must install and configure swift-recon
on your Swift object servers.

You can find more information about swift-recon at
<https://github.com/pandemicsyn/swift-recon>.

Installation
------------
You must first have, or install, Zenoss 3.2.0 or later. Core and Enterprise
versions are supported. You can download the free Core version of Zenoss from
<http://community.zenoss.org/community/download>.

Normal Installation (packaged egg)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Depending on what version of Zenoss you're running you will need a different
package. Download the appropriate package for your Zenoss version from the list
below.

* Zenoss 4.1: [Latest Package for Python 2.7][]
* Zenoss 3.0 - 4.0: [Latest Package for Python 2.6][]

Then copy it to your Zenoss server and run the following commands as the zenoss
user.

    zenpack --install <package.egg>
    zenoss restart

Developer Installation (link mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you wish to further develop and possibly contribute back you should clone
the git repository, then install the ZenPack in developer mode using the
following commands.

    git clone git://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift.git
    zenpack --link --install ZenPacks.zenoss.OpenStackSwift
    zenoss restart

Usage
-----
Installing the ZenPack will add the following objects to your Zenoss system.

* Configuration Properties
   * zSwiftObjectServerPort: Listening port of swift-object-server. Defaults to
     6000.

* Monitoring Templates
   * SwiftObjectServer in /Devices

* Process Classes
   * OpenStack/Swift
      * swift-account-auditor
      * swift-account-reaper
      * swift-account-replicator
      * swift-account-server
      * swift-container-auditor
      * swift-container-replicator
      * swift-container-server
      * swift-container-sync
      * swift-container-updater
      * swift-object-auditor
      * swift-object-replicator
      * swift-object-server
      * swift-object-updater
      * swift-proxy-server

* Event Classes
   * /Status/Swift
   * /Perf/Swift

The zSwiftObjectServerPort property is used by the SwiftObjectServer monitoring
template to control what port it will attempt to find the recon API on.
Normally the default of 6000/tcp will work unless you've chosen a different
port for your swift-object-server process.

By default the SwiftObjectServer monitoring template will not be bound to any
devices. To make use of it you will need to either bind it directly to your
Swift object server devices, or put your object servers into their own device
class and bind the template to that device class. Typically this will be under
either /Server/Linux or /Server/SSH/Linux so you get normal operating system
monitoring in addition to the Swift-specific monitoring.

Swift Metrics
~~~~~~~~~~~~~
Assuming you have swift-recon and Zenoss setup properly you can expect to see
the following extra graphs on your Swift object servers.

* Swift Object Server - Async Pending
 + Trend of asynchronous pending tasks. When a Swift proxy server updates an
   object it attempts to synchronously update the object's container with the
   new object information. There is a three second timeout on this task and if
   it can't be completed in that time, it will be put into an asynchronous
   pending bucket to be executed later. By trending and thresholding on how
   many tasks are pending you can get an early read on cluster performance
   problems. By default a maximum threshold of 10 is set on this metric and
   will raise a warning severity event in the /Perf/Swift event class when it
   is breached.

* Swift Object Server - Disks
 + Trend of total and unmounted disks on the storage node. Swift's mechanism
   for detecting failing or failed drives and taking them offline is to
   unmount them. By proactively monitoring for unmounted disks and replacing
   them you can keep your cluster healthy. By default a maximum threshold of 0
   is set on unmounted disks and will raise a warning severity event in the
   /Status/Swift event class.

* Swift Object Server - Quarantine
 + Trend of accounts, containers and objects that have been quarantined. Swift
   has an auditor process that will find corrupt items and move them into a
   quarantine area so good objects will be replicated back into their place.
   Sudden increases in quarantined items can indicate hardware problems on
   storage nodes. Additionally quarantine is not automatically pruned and can
   result in some storage nodes filling up their disk at a faster rate than
   others and running out of space. By default a maximum threshold of 100 is
   set individually on quarantined accounts, containers and objects. A warning
   event will be raised in the /Status/Swift event class if it is breached.

* Swift Object Server - Replication Time
 + Trend of replication time. Swift has a replicator process that cycles
   continually. If a single replication cycle takes more than 30 minutes it
   can reduce the resiliency of the cluster. By default a maximum threshold of
   30 minutes is set on replication time and will raise a warning severity
   event in the /Perf/Swift event class when breached.

* Swift Object Server - Load Averages
 + Trend of 1, 5 and 15 minute operating system load average. Additionally the
   15 minute load average divided by total disks is calculated. A perfectly
   efficient storage node will run at a load average of 1.0 per disk. By
   default a maximum treshold of 2.0 is set on 15 minute load average divided
   by total disks and will raise a warning severity event in the /Perf/Swift
   event class when breached.

* Swift Object Server - Process Churn
 + Trend of processes created per second. High process churn can indicate a
   broken process being unnecessarily restarted. By default a maximum treshold
   of 100 processes per second is set and will raise a warning severity event
   in the /Perf/Swift event class when breached.

* Swift Object Server - Disk Usages
 + Trend of maximum, average and minimum disk usage for all disks in the
   storage node. These are the primary storage capacity metrics within a
   cluster. Depending on the size of each individual disk, weights and the
   skew of store object sizes, an entire cluster can exceed capacity if a
   single disk runs out of capacity. By default a maximum threshold is set on
   the maximum usage metric. It will raise a warning severity in the
   /Status/Swift event class when breached.

* Swift Object Server - Disk Sizes
 + Trend of maximum, average and minimum disk sizes for all disks in the
   storage node. Ideally all disks in a storage node will be the same size
   unless weights are closely managed. No default thresholds are set on these
   metrics.

* Swift Object Server - Processes
 + Trend of total and running processes. No default thresholds are set on
   these metrics.

Process Monitoring
~~~~~~~~~~~~~~~~~~
All Swift processes will be discovered and monitored based on the process
classes listed above. If one of the processes is found to not be running on a
node where it should be, an error severity event will be raised in the
/Status/OSProcess event class.

Each of the individual Swift process will also be monitored for its CPU and
memory utilization.

What's Next
-----------
While this ZenPack currently has wide coverage of metrics that are important to
the successful operation of a Swift cluster, there are more opportunities. The
following is a list of metrics that are not currently monitored, but would be
useful.

* Dispersion Report Results
* Ring consistency between all object, container and account servers.

Screenshots
-----------
|Aggregate Graphs 1|
|Aggregate Graphs 2|
|Total & Unmounted Disks|
|Async Pending Tasks|
|Disk Usages|
|Disk Sizes|
|Load Averages|
|Process Churn|
|Total & Running Processes|
|Quarantined Items|
|Process Monitoring|


[Zenoss]: <http://www.zenoss.com/>
[Swift project site]: <http://swift.openstack.org/>
[Latest Package for Python 2.7]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.OpenStackSwift/ZenPacks.zenoss.OpenStackSwift-0.7.0-py2.7.egg>
[Latest Package for Python 2.6]: <https://github.com/downloads/zenoss/ZenPacks.zenoss.OpenStackSwift/ZenPacks.zenoss.OpenStackSwift-0.7.0-py2.6.egg>

.. |Aggregate Graphs 1| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/aggregate1.png
.. |Aggregate Graphs 2| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/aggregate2.png
.. |Total & Unmounted Disks| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/disks.png
.. |Async Pending Tasks| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/async_pending.png
.. |Disk Usages| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/disk_usages.png
.. |Disk Sizes| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/disk_sizes.png
.. |Load Averages| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/load_averages.png
.. |Process Churn| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/process_churn.png
.. |Total & Running Processes| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/processes.png
.. |Quarantined Items| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/quarantine.png
.. |Process Monitoring| image:: https://github.com/zenoss/ZenPacks.zenoss.OpenStackSwift/raw/master/docs/osprocesses.png