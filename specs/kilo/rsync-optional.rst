..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=============================
Make Rsync for Guest Optional
=============================

Blueprint:

https://blueprints.launchpad.net/trove-integration/+spec/rsync-optional

Today, the instance rsyncs the guestagent code and trove-guestagent.conf
via http://git.io/qI9ivw (or http://git.io/p88Njw)

The proposal is to introduce an alternative that does not require
guest-to-controller SSH connectivity: bake the guestagent code and
trove-guestagent.conf into the image.

Problem Description
===================

In production, permitting SSH connectivity between guests and the
control-plane is a security no-no. Although trove-integration is considered
to be only a sample reference implementation, we owe it to deployers to
provide insight into how to properly secure Trove.

Use Cases
----------

* As a deployer, I want to avoid ssh connectivity between guests and the
  control-plane.

Proposed Change
===============

Add additional elements in trove-integration to stage the guestagent code
and trove-guestagent.conf during the extra-data.d hook, and subsequently
install them in the install.d hook, vs. relying on upstart/systemd to rsync.

See https://review.openstack.org/#/c/119488/

This is not turned on by default, and therefore is backwards compatible.

Configuration
-------------

To make use of this functionality, it requires setting GUEST_LOCAL_TROVE_DIR
and GUEST_LOCAL_TROVE_CONF. The aforementioned values are used in the newly
introduced diskimage-builder elements.

Database
--------

No database changes.

Public API
----------

No public API changes.

Public API Security
-------------------

No public API Security related changes.

Internal API
------------

No internal API changes.

Guest Agent
-----------

No Guest Agent changes.


Alternatives
------------

No alternatives.


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

See https://review.openstack.org/#/c/119488/

Dependencies
============

No dependencies.


Testing
=======

diskimage-builder element additions/changes are not tested via traditional
means at the moment.


Documentation Impact
====================

No documentation impact.


References
==========

None.
