..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


==============================================
Percona XtraDB Cluster Grow and Shrink Support
==============================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

For the Percona XtraDB Cluster (pxc) datastore we need the ability to grow
and shrink a cluster. This will add these 2 core features to the pxc solution
we currently have.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/pxc-grow-shrink-cluster


Problem Description
===================

PXC is lacking support for grow and shrink clusters. This will allow a user
to create a new instance in the cluster and delete an existing instance from
the cluster.

An example use case would be if an instance in the cluster is having issues
due to the underlying hardware, network, or other issues then a user can
remove the instance and create a new one to keep the cluster healthy.

Proposed Change
===============

PXC will use the existing grow and shrink API calls and implement them for the
pxc manager. This change will allow the cluster to be heterogeneous when
needing to grow or shrink the cluster. A heterogeneous cluster means that the
flavor and volume may not all be the same for every instance in a cluster.

Requirements for grow:

- A new instance in the cluster can be any valid flavor size.
- A new instance in the cluster must have a volume of the smallest size of
  the instances in the cluster or larger. This is to make sure that new
  instances created in the cluster have enough volume space to operate with
  the rest of the cluster instance.
- Quota validation that user has the capacity to grow the cluster by the number
  of instances and volume space in their account.

Requirements for shrink:

- There must be at least 2 instances in the cluster in order to shrink a
  cluster. A cluster instance count must have at least 1 instance to operate.

A few new guestagent API calls will be needed in order for grow to work.

PXC handles joining a cluster automatically when given an ip address of one of
the nodes in the existing cluster. When given all the ips of the existing
cluster instances PXC will sequentially attempt to connect to the ips in the
list and attempt to join the cluster. If one of the instances in the list is
not up (crash or network or otherwise and issue) then PXC will try the next
ip in the list. This will help allow a user to join a new instance to the
cluster so that they can then shrink or remove the problematic instance from
the cluster.

Configuration
-------------

No configuration changes are anticipated.


Database
--------

None


Public API
----------

The following public API calls will be made available to the PXC datastore.

* Cluster Grow - The existing call payload will not be changed. Implementing
  the grow cluster feature will add the new instances to the existing cluster.
* Cluster Shrink - The existing call payload will not be changed. Implementing
  the shrink cluster feature will allow a user to remove instances from their
  existing cluster.

Public API Security
-------------------

None


Python API
----------

None


CLI (python-troveclient)
------------------------

Support for the following existing CLI calls.

* cluster-grow
* cluster-shrink

No changes should be nessesary to accomplish these actions.


Internal API
------------

There are few new guestagent calls that will need to be made to get the data
from the existing instances in the cluster as well as updating the
cluster configuration on the existing instances. [1]_

The process of growing the cluster or adding a new instance(s) to the cluster:

* First set the cluster state to GROWING
* Boot a new pxc instance.
* Once the instance is up then we get the configuration setting of the
  existing cluster from one of the instances in the cluster. These setting
  include the cluster name, replication settings, and ips of the existing
  cluster.
* Once the configuration on the new instance(s) is set then we start mysql on
  each instance. The new instance(s) find the cluster from the ips set and the
  cluster name.
* After mysql is started up on the new instance(s) the cluster recognizes
  the new instances in the cluster.
* At this point the cluster is in a good state but in order to be able to help
  recover or restart an instance in the cluster we push down a new
  configuration that includes the new ip address of the new instance(s) to all
  the instances in the cluster.
* After all the instances in the cluster have the new configuration there is no
  need to restart the mysql process again because the cluster already
  recognizes all the instances in the cluster.
* Then we set the task state of the cluster to complete or NONE.

The process of shrinking a cluster is removing a given instance(s) from the
cluster:

* First we set the task state to SHRINKING.
* Then stop mysql on the given instance(s)
* Then delete these instance(s) as well.
* Next the existing instance(s) in the cluster need to have their
  configurations updated to match the current state of the cluster. This will
  entail just updating the ips of the current instance(s) in the cluster.
* No need for a restart after this since the cluster automatically knows about
  the active instance(s) in the cluster. The configuration update is for
  recovery and restart if needed later.
* After the configuration update is done then we can reset the task state of
  the cluster to completed or NONE.

Guest Agent
-----------

Like mentioned above in the Internal API section there will be a few new
guestagent calls to support grow and shrink.

Methods added to the Guest Agent

* write_cluster_configuration_overrides - This method will write out the
  updated cluster configuration changes needed for the cluster to be grown or
  shrunk.

* get_cluster_context - This method will return the context of the current
  cluster. The context is the information that is used to connect the new
  instances to the existing cluster setup. Context includes cluster settings
  and replication settings.

No calls will be deprecated in order to complete this.

Alternatives
------------

Not to support grow and shrink of a pxc cluster.

Implementation
==============

Assignee(s)
-----------

+---------------+--------------+---------+--------------------+
+ Name          + Launchpad Id + IRC     + Email              +
+===============+==============+=========+====================+
+ Craig Vyvial  + cp16net      + cp16net + cp16net@gmail.com  +
+---------------+--------------+---------+--------------------+


Milestones
----------

Targeting this for milestone:
Mitaka


Work Items
----------

This work will be broken up into 2 separate items.

- Grow a cluster (adding new instance(s) to cluster)
- Shrink a cluster (removing instance(s) from cluster)


Upgrade Implications
====================

The guestagents on the existing cluster instances must be updated prior to
calling the grow or shrink API calls. Otherwise the cluster may get stuck
in a GROWING_CLUSTER or SHRINKING_CLUSTER state, because the guestagent will
not have the calls to support growing or shrinking a cluster.

Dependencies
============

None

Testing
=======

There will be unit tests that test the new calls for the strategy.

There will be integration tests which will test grow and shrink cluster
features.

Documentation Impact
====================

We need to update the docs to show support for grow and shrink clusters for
the pxc manager.

References
==========

.. [1] https://www.percona.com/doc/percona-xtradb-cluster/5.5/howtos/ubuntu_howto.html

.. [2] https://www.percona.com/doc/percona-xtradb-cluster/5.5/manual/bootstrap.html#bootstrap

Appendix
========

None
