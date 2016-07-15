..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..


================
Quota Management
================

A proposal to expose the existing Quota.update API from the management
API to the user through the non-management API.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/quota-management


Problem Description
===================

There is a Quota.update API in the management API to allow an operator
to change the quota allocation for a resource.  Unfortunately, there
is no CLI to access that call.


Proposed Change
===============

Add the v1.Quotas class to the v1.client so that an operator can
execute a command to change the allocation for a resource.


Configuration
-------------

No impact.

Database
--------

No impact.

Public API
----------

No impact (the REST API already exists).

Public API Security
-------------------

The added call will be restricted to admin users.

Python API
----------

Adds client.quotas.update to the python client:

.. code-block:: python

    def update(self, id, quotas):
        """Set limits for quotas."""

This call takes a dict indicating the change to be made:

    trove_client.quotas.update(project.id, {'instances': 10})


Also adds client.quotas.show to the python client:

.. code-block:: python

    def show(self, id):
        """Shows usage information for quota managed resources."""

This call takes the id of the project and returns all resources with
their usage:

    trove_client.quotas.show(project.id)




CLI (python-troveclient)
------------------------

Two new shell commands will be added::

  $ trove quota-show <project id>

  $ trove quota-update <project id> volumes 50


Internal API
------------

No impact.

Guest Agent
-----------

No Impact.

Alternatives
------------



Dashboard Impact (UX)
=====================

This will be available only via the command line.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  6-morgan


Milestones
----------

Target Milestone for completion:
  Newton

Work Items
----------

Patch already delivered to gerrit.


Upgrade Implications
====================

None.


Dependencies
============



Testing
=======

Tests already exist for this functionality.


Documentation Impact
====================



References
==========


Appendix
========

Any additional technical information and data.
