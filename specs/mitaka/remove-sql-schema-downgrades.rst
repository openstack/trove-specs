..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


============================
Remove SQL Schema Downgrades
============================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Trove still has the downgrade method on its migration files. Following the
cross-project spec https://review.openstack.org/#/c/152337/ we are supposed to
remove the downgrade to avoid data inconsistency, lack of integrity, etc.
This approach was already done in many projects like Keystone, Magnum, Nova
and others [2][3][4][5].

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/remove-sql-schema-downgrades


Problem Description
===================

Downgrades are not the best idea when thinking about data integrity. A cross
project spec was proposed to start removing downgrades and it was already done
in many projects. We need to delete downgrade from migration files.

Proposed Change
===============

Remove downgrades from migration files and remove the command from
trove-manage.

Configuration
-------------

None

Database
--------

None

Public API
----------

None

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

None

Internal API
------------

None

Guest Agent
-----------

None

Alternatives
------------

None


Dashboard Impact (UX)
=====================

TBD (section added after approval)


Implementation
==============

Assignee(s)
-----------

<tellesmvn>

Milestones
----------

Mitaka-1

Work Items
----------

This work is basically removing downgrades, removing the command from
trove-manage and update the tests.

Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

We need to update the tests so they will not fail when trying to downgrade.


Documentation Impact
====================

None

References
==========

.. [1] https://review.openstack.org/#/c/152337/
.. [2] https://review.openstack.org/#/c/167554/2
.. [3] https://review.openstack.org/#/c/167834/
.. [4] https://review.openstack.org/#/c/167189/2
.. [5] https://review.openstack.org/#/c/165740/


Appendix
========

None
