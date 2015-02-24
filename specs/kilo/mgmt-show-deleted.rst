..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================================
Enhance Mgmt-Show To Support Deleted Instances
==============================================

Blueprint:

https://blueprints.launchpad.net/trove/+spec/mgmt-show-deleted

Today, ``GET /v1.0/<tenant_id>/mgmt/instances/<instance_id>`` does not work
for Trove instances that are marked as deleted.

The proposal is to introduce an optional query parameter that indicates that
the Trove instance information should be returned irrespective of whether the
Trove instance is marked as deleted or not.

Problem Description
===================

Without an API to retrieve information about a deleted instance, the deployer
is forced to consult the Trove infrastructure database directly.

The mgmt-list operation supports returning deleted instances if
``?deleted=true`` is provided, so it only makes sense that additional
information about a deleted instance be accessible via mgmt-show.

Use Cases
----------

* As a deployer, I want to be able to retrieve information about a deleted
  Trove instance.

Proposed Change
===============

Support the ``?deleted=true/false`` query parameter in
``GET /v1.0/<tenant_id>/mgmt/instances/<instance_id>``

Changes In Behavior:

* If ``deleted=true``, if the Trove instance UUID is present in the
  infrastructure database, the instance information is returned and the
  request is successful.
* If ``deleted=false``, or the deleted query parameter is omitted, the request
  will only succeed if the trove instance is not marked as deleted.
* If the compute_instance_id exists in the trove.instances row, return it in
  the mgmt-show response at instance.server.id, even if the Nova API
  consultation fails.
* If the volume_id exists in the trove.instances row, return it in the
  mgmt-show response at instance.volume.id, even if the Cinder API
  consultation fails.

Configuration
-------------

No Configuration changes.

Database
--------

No Database changes.

Public API
----------

No public API changes.

Public API Security
-------------------

No public API Security related changes.

Management API
--------------

``GET /v1.0/<tenant_id>/mgmt/instances/<instance_id>`` will be enhanced to
support the 'deleted' query parameter.

For reference, the response of a mgmt-show: http://git.io/2RwWWA

Today, if the compute_instance_id is not recognized by the Nova API, the
mgmt-show response will not include instance.server{}. Along the same lines,
if the volume_id is not recognized by the Cinder API, the mgmt-show response
will not include instance.volume{}.

This blueprint changes that behavior by always returning instance.server.id
and instance.volume.id if they exist in the trove.instances table.

Internal API
------------

No internal API changes.

Guest Agent
-----------

No Guest Agent changes.


Alternatives
------------

No relevant alternatives given the prior art on using 'deleted=true/false'
in other Trove routes.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Auston McReynolds (amcrn)

Milestones
----------

Kilo-1

Work Items
----------

See https://review.openstack.org/#/c/128446/

Dependencies
============

No dependencies.


Testing
=======

Standard.


Documentation Impact
====================

If the Management API is documented (which I don't believe it is), then
the addition of the 'deleted' query parameter is relevant.


References
==========

None.
