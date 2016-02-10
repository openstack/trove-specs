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


=======================================
Support for 'root' actions to Cassandra
=======================================

Implement root enable (with password)/disable and show calls in the Cassandra
guest agent.
Also include datastore-agnostic scenario tests for the root actions.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/cassandra-root-enable


Problem Description
===================

Continuing the work on add user/database support for Cassandra
guests [1]_ we should also enable the Trove users to create superuser accounts.


Proposed Change
===============

The Cassandra's superuser is called 'cassandra'.
It comes with any new Cassandra installation, but it can be deleted.

In Cassandra only SUPERUSERS can create other users and grant permissions to
database resources.
Trove uses the 'os_admin' superuser to perform its administrative tasks. [1]_
The users it creates are all 'normal' (NOSUPERUSER) accounts.

The built-in 'cassandra' superuser is proactively removed on prepare as it is
not needed.

During normal operation (no 'root' enabled), there should be only
one superuser in the system (os_admin). The 'root' is therefore **not**
enabled.

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

The 'enable' action will be implemented by creating a new superuser
('cassandra') and granting it full access to all
keyspaces. The username ('cassandra') and password (user-supplied or random
otherwise) will be returned back to the client.

Now on, there will be more than one superuser accounts in the system and
the 'root' will hence be reported as 'enabled'.

The 'disable' action will merely reset the user's password to a new random
string without exposing it to the end-user. The account itself **will not** be
removed so the *root-show* will keep reporting root as 'enabled' as it should.

When a backup is restored the presence of superusers other than 'os_admin'
will be checked and the root-status of the new instance will be reported as
'enabled' if there are any.

Note that a superuser cannot remove its *super* privileges or delete itself.
It should therefore not be possible to bypass the root check by creating a new
superuser, deleting the old one and restoring the state into a new instance.

Once having the superuser access to the database the end-user could of course
alter/drop the 'os_admin', but doing that would render the instance
unmanageable from Trove.

Alternatives
------------

None


Dashboard Impact (UX)
=====================

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Petr Malik <pmalik@tesora.com>

Milestones
----------

Mitaka

Work Items
----------

* Implement root-related calls in the Cassandra manager.

* Add datastore-agnostic scenario tests to exercise the new functionality.


Upgrade Implications
====================

None


Dependencies
============

This implementation largely depends on work done as a part of
blueprint cassandra-database-user-functions [1]_


Testing
=======

* Manager unittests will be added where appropriate.

* Datastore-agnostic scenario tests to exercise the related functionality will
  be implemented.


Documentation Impact
====================

Document the newly enabled functionality for the Cassandra datastore.


References
==========

.. [1] Cassandra user/database implementation review: https://review.openstack.org/#/c/206739/

Appendix
========

None
