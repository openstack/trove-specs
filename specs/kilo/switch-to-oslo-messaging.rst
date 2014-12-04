..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

========================
Switch to OSLO Messaging
========================

Include the URL of your launchpad blueprint:

https://wiki.openstack.org/wiki/Trove-rpc-versioning

This blueprint is to document the project to switch trove to use OSLO
Messaging.

Problem description
===================

Get Trove on the same page w/ other projects + oslo. This will require
refactoring the rpc layer

Prevent backward incompatibility between Trove components

* The rpc client can send an older version of a message/call to a newer message handler without issue.
* The rpc client can send a newer version of a message/call to an older message handler without killing it (need to confirm this).
* The rpc client can check to see if it can send a newer version of a message/call.

* Reduce the need for downtime during deployments.

** Effectively allows for a mix of versions between the control plane and guest agents (in most cases). There may still be updates that will require down time.

Proposed change
===============

* Remove rpc common components from oslo incubator?
* Use oslo messaging library

** The minimum version will be picked from global-requirements. At the time of this writing, it's >= 1.4.0

*  Keep track of a "version history" in comments in the code

* Update trove calls to the openstack.common.rpc client to include a version cap param. (This is already supported in the client)

** Trove API    --> Task Manager
** Trove API    --> Guest Agent
** Guest Agent  --> Conductor
** Task Manager --> Conductor
** Document the use cases and examples of how to add/modify API calls


Configuration
-------------

oslo.messaging has been designed to be backwards compatible config-wise. All the config compatibilities will be kept until all the projects have been migrated to oslo.messaging.

Database
--------

NA

Public API
----------

NA

Internal API
------------

NA

Guest Agent
-----------

NA


Alternatives
------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
   sgotliv

Milestones
----------

Kilo-1

Work Items
----------

* see above.

Dependencies
============

None

Testing
=======

Additional tests will be proposed if required, existing tests amended.

Documentation Impact
====================

Yes

References
==========

See https://review.openstack.org/#/c/94484/
