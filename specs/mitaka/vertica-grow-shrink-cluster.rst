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

    Please do not delete any of the sections in this template.  If you have
    nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license
    notice above should remain.


=======================================
Vertica Cluster Grow and Shrink Support
=======================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

The Vertica database has elastic grow/shrink capabilities which are not
currently supported by the Vertica guest agent for Trove.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/vertica-grow-shrink-cluster


Problem Description
===================

The Vertica guest agent currently does not leverage the underlying elastic
capabilities of Vertica. This will enable a user to grow a cluster in the
event that they wish to accommodate more data or enable faster query
performance, while scaling down helps avoid costs associated with
overprovisioning.

Proposed Change
===============

As Vertica was architected from the ground up to be a clustered system, adding
and removing nodes is relatively simple in comparison to other datastores.

Configuration
-------------

A minimum k-safety configuration option will be added for vertica to allow
the operator to decide their desired level of fault tolerance.


Database
--------

None


Public API
----------

The following public API calls will be made available to the Vertica datastore.

* Cluster Grow - The existing call payload will not be changed. Implementing
  the grow cluster feature will add the new instances to the existing cluster.
* Cluster Shrink - The existing call payload will not be changed.
  Implementing the shrink cluster feature will allow a user to remove
  instances from their existing cluster.

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

None.

Guest Agent
-----------

To enable more efficient grow and shrink, local data segmentation will be
enabled on Vertica [1]_. This creates additional local, logical segments of
data on a node to enable easier shipping of data between nodes. The number of
local segments is configurable with the scaling factor variable. Local
segmentation has the drawback of making tables with many hundreds of
projections less efficient [2]_.

Grow
~~~~

Growing a cluster involves two main steps [3]_.

First, a new "host" must be added to the cluster, which in the case of trove
would mean a new instance. The update_vertica script is then called, similar
to the install_vertica script, which handles installation of the vertica
binaries.

Second, the host must be added as a node to the database. The adminTools
utility is called with the db_add_node command to register the host with the
database.

Shrink
~~~~~~

Removing a node from a Vertica cluster proceeds inversely to addition, with
an extra check to ensure that the minimum k-safety level of the system is
maintained.

If a user attempts to remove a node that would lower the k-safety
level below the configured level, an error will be thrown.

After the k-safety check, the host is removed from the database [4]_.
Similarly as with grow, the adminTools utility will be called using the
db_remove_node command.

Then, the host to be removed is removed from the cluster, using the same
update_vertica script but with the --remove-hosts option.

K-safety
~~~~~~~~

Vertica defines three K-safety levels for the number of nodes K that could
fail while allowing the cluster to continue to operate: K=0 for clusters
with 1 or 2 nodes, K=1 for clusters with 3 or 4 nodes, and K=2 for 5 or
more [5]_ [6]_.

Rather than prevent a user from removing nodes that would result in a lower
k-safety value, it is up to the operator to define a minimum level of safety
she is willing to accept. For example, in some cases it may be that the costs
associated with overprovisioning the cluster outweigh the risk of data being
unavailable.

Alternatives
------------

Trove could enforce a minimum k-safety level to ensure the integrity of the
cluster, but this could be too restrictive.


Implementation
==============

Assignee(s)
-----------

atomic77


Milestones
----------

Mitaka-3


Work Items
----------

- Grow cluster
- Shrink cluster


Upgrade Implications
====================

None.

Dependencies
============

None

Testing
=======

Integration tests will be added or modified as needed in order to test
grow/shrink with the new int-test framework.

Documentation Impact
====================

The documentation should be updated to reflect the fact that grow and shrink is
supported for Vertica clusters.

Dashboard Impact (UX)
=====================

There will be some minor changes to the UI to support grow and shrink buttons
for the cluster.

References
==========

.. [1] https://my.vertica.com/docs/7.1.x/HTML/index.htm#Authoring/AdministratorsGuide/ClusterManagement/ElasticCluster/LocalDataSegmentation.htm
.. [2] The Vertica documentation recommends local data segmentation be done
        with numbers of nodes that are a power of two. Some experimentation
        will be required to see what is whether violating this recommendation
        is still worthwhile compared to not using local data segmentation at
        all

.. [3] https://my.vertica.com/docs/7.1.x/HTML/index.htm#Authoring/AdministratorsGuide/ManageNodes/AddingNodes.htm
.. [4] https://my.vertica.com/docs/7.1.x/HTML/index.htm#Authoring/AdministratorsGuide/ManageNodes/RemovingNodes.htm
.. [5] https://my.vertica.com/docs/7.1.x/HTML/index.htm#Authoring/AdministratorsGuide/ManageNodes/LoweringTheK-SafetyLevelToAllowForNodeRemoval.htm
.. [6] https://my.vertica.com/docs/7.1.x/HTML/Content/Authoring/ConceptsGuide/Components/HighAvailabilityAndRecovery.htm

Appendix
========

None
