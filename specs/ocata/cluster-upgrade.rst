..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..


===============
Cluster Upgrade
===============

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Trove currently has support for upgrading since instances from one
datastore version to another, but that functionality is lacking for
clusters.  This blueprint outlines a framework and API for
implementing upgrades for clusters.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/cluster-upgrade


Problem Description
===================

Trove does not currently support upgrading clusters to new datastore
versions.


Proposed Change
===============

Implement a new cluster-upgrade API for upgrading a cluster to a new
datastore version.

This blueprint will outline only the framework and API for
implementing cluster upgrades.  It will not detail the implementation
of upgrade for any specific datastore as the implementation for each
datastore may be different.

If your specification proposes any changes to the Trove REST API such
as changing parameters which can be returned or accepted, or even
the semantics of what happens when a client calls into the API, then
you should add the APIImpact flag to the commit message. Specifications with
the APIImpact flag can be found with the following query:

https://review.openstack.org/#/q/status:open+project:openstack/trove-specs+message:apiimpact,n,z


Code snippets, etc. should be placed in appropriately marked blocks:

.. code-block:: bash

    # This is a bash command
    ls -lf

.. code-block:: python

    # sample code
    for count in range(1, 10):
        print count


Configuration
-------------

No datastore agnostic configuration settings are envisioned.  Setting
for specific datastores will be detailed in the specifications for
each datastore implementation.

Database
--------

No database changes are envisioned.

Public API
----------

A new REST API will be implemented for cluster-upgrade:

Request::

    PATCH v1/{tenant_id}/cluster/{cluster_id}
    {
        "cluster":
        {
            "datastore_version": "<datastore_version_uuid>"
        }
    }

Response::

    {
    }

REST return codes::

    202 - Accepted.
    400 - BadRequest. Server could not understand request.
    404 - Not Found. <datastore_version_id> not found.


Public API Security
-------------------

No security implications.

Python API
----------

A new method will be implemented in the trove API.  This method will
upgrade a cluster to the image specified by the provided
datastore_version.

.. code-block:: python

    upgrade(cluster, datastore_version)

:cluster: the cluster to upgrade
:datastore_version: the datastore version, or its id, to which the
                    trove cluster will be upgraded


CLI (python-troveclient)
------------------------

A new CLI call will be implemented.  This new call will upgrade a
cluster to the image specified by the provided datastore_version.

.. code-block:: bash

    trove cluster-upgrade <cluster> <datastore_version>

:cluster: the cluster to upgrade
:datastore_version: the datastore version to which the instance will
                    be upgraded

Internal API
------------

The implementation of upgrade for single instances will be used to
upgrade the guest agent on an instance.


Guest Agent
-----------

For the initial implementation it is expected that the existing pre
and post upgrade methods will suffice.


Alternatives
------------


Dashboard Impact (UX)
=====================

A new cluster action will be implemented to allow a cluster to be
upgraded.  Said functionality will be similar to the functionality for
a single instance.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  6-morgan

Dashboard assignee:
  <launchpad-id or None>


Milestones
----------

Target Milestone for completion:
  eg. Liberty-1

Work Items
----------

The implementation of this has been posted and is ready for review
subject to this spec being approved.


Upgrade Implications
====================

No upgrade implications.


Dependencies
============


Testing
=======

No int tests will be included with this change as this is only a
framework without implementations for specific datastores.


Documentation Impact
====================

What is the impact on the docs team of this change? Some changes might require
donating resources to the docs team to have the documentation updated. Don't
repeat details discussed above, but please reference them here.


References
==========

None.


Appendix
========

None.
