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


==================================
Datastore-specific API controllers
==================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Improve user and database API extensions to handle datastore-specific
properties and allow them to work with clusters.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/datastore-specific-api-extensions

Also see [1]_


Problem Description
===================

User and database commands are currently routed through MySQL-specific
API extensions. This causes several problems with input validation which
is MySQL-specific and does not work well with other datastores.
It also forces MySQL-specific properties on models and views which do not have
(or have different) meaning on non-MySQL-like datastores.

Another long-lasting problem has been that the above APIs do not work with
cluster instances.


Proposed Change
===============

This document proposes introduction of generic API controllers.

Any datastore-specific parsing, handling and validations would be provided
in derived classes. Trove would load the appropriate derived-controller
dynamically based on the target datastore of the API call.

The goal is to provide a consistent experience to the Trove user.
The base controller implementations would provide the execution flow and handle
common Trove validations (e.g. check for existence, duplicates) and
notifications.

The derived classes would provide datastore-specific parsing and model
validations (e.g. username validation, parsing datastore-specific properties
from the payload).
Datastore-specific views would map models properties on the output payload.

The default controller would also include cluster interface which would,
by default, route all request to one (controller) instance of the cluster
leaving the rest on the cluster itself. This strategy proved successful with
many if not all currently existing datastores.
Datastores may override the node selection or entirely re-implement
any of the calls shall it be necessary.

We would avoid introduction of new (cluster) API endpoints
(e.g. trove cluster-user-create) at this time.
It is not clear whether that is required at all for the above APIs and
it draws yet another distinction between clusters and single Trove instances
which may not be warranted.

This work would be entirely internal to the API engine.
The existing endpoints (guest-agent or user facing) would not be affected.


Configuration
-------------

There would be a datastore-specific property for each controller
implementation.

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

The CLI would be modified to accept cluster IDs for the related commands.

Internal API
------------

There can be only a single controller per ReST API endpoint.

This would be a Rounting Controller. This controller would
be responsible for detecting the target instance's datastore and loading
the derived controller implementation for it (see `Configuration`_).
It would then simply pass the request on this derived controller.

The derived controller would extend the Base implementation with the same
interface.
Generally it would just parse the payload and construct datastore-specific
model objects and views.
The base implementation would handle the generic validations and execution
flow.

The base implementation would also be responsible for detecting the instance
type (i.e. single or cluster) and routing the cluster requests to the
cluster interface which would then pass it down to one (controller) instance
from the cluster.
The controller instance would be selected from the nodes exposed by the
cluster strategy (i.e. nodes displayed by "trove cluster-instances" command).

Guest Agent
-----------

None

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

Petr Malik <pmalik@tesora.com>

Milestones
----------

Ocata-1

Work Items
----------

 - Implement the base controllers.
 - Implement derived controllers.
 - Switch datastores to use their respective derived controllers.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

Unittests will be added to test the base and derived controller functionality.


Documentation Impact
====================

None


References
==========

.. [1] Related bug: https://bugs.launchpad.net/trove/+bug/1498573


Appendix
========

None
