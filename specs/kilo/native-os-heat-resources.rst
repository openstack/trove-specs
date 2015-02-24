..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst


  This template should be in ReSTructured text. The filename in the git
  repository should match the launchpad URL, for example a URL of
  https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
  awesome-thing.rst.

  Please do not delete any of the sections in this template.  If you
  have nothing to say for a whole section, just write: None

==========================================================
Use native OS::* Heat resources for internal orchestration
==========================================================

https://blueprints.launchpad.net/trove/+spec/native-os-heat-resources

Problem Description
===================

A far-fetching goal in Trove is to use OpenStack Orchestration service (Heat)
for all the internal orchestration tasks.
Current Trove usage of Heat involves exclusively AWS-compatible template
syntax and Heat resources.

As of Icehouse OpenStack release Heat community declared new, native
HOT template format to be stable and ready for wide usage.
Moreover, most of the innovation will happen in native OS::* resources
and HOT template format to fully leverage available OpenStack functionality,
as they do not have to keep compatibility with AWS CloudFormation service.


Proposed Change
===============

Align default Heat template with latest changes in Heat. That involves:

- usage of HOT template format and internal functions;
- usage of native OS::* resources wherever possible.


Configuration
-------------

All the changes are in the `default.heat.template` file.

Database
--------

None

Public API
----------

None

Public API Security
-------------------

No public API Security related changes.

Internal API
------------

None

Guest Agent
-----------

None


Alternatives
------------

Do not change anything and continue to use AWS-compatible resources,
missing many of the new features Heat can offer.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  pshchelo


Milestones
----------

Kilo-2

Work Items
----------

- rewrite `default.heat.template` to use as much of native Heat capabilities
  and OS resources as possible
  (implementation is on review https://review.openstack.org/#/c/112035/)


Dependencies
============

None

Testing
=======

Unfortunately testing Heat-based orchestration is not yet enabled
on Trove gates.
Enabling it might be a topic for another blueprint.

Documentation Impact
====================

None

References
==========

None
