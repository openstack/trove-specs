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


==========================
Module Management Ordering
==========================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::


Modules currently are applied in any order, however operators may wish to
control the order that modules are applied to ensure proper functionality.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/module-management-ordering


Problem Description
===================

Trove now supports module management, in that 'modules' containing a payload
can be applied to running Trove instances.  This allows end users the ability
to 'bring your own license' for datastores (among other things), as long as
a corresponding driver plugin exists.  The original implementation doesn't
take into account the case where one module must be applied before another
(for example, if multiple licenses must be applied in the correct sequence).

The ability for an operator to ensure that 'admin' modules are applied before
user modules is also lacking.

This spec addresses these shortcomings.


Proposed Change
===============

A method for specifying 'priority' modules, plus a way to rank the order in
which modules are applied would be created.  Two new attributes
'priority_apply' and 'apply_order' would need to be added to the payload
on create and update.  In addition, an is_admin flag will be added as an
automatic attribute, set when someone with admin credentials creates a
module.  This will allow better control on the driver plugin side with
regards to security concerns, etc.

The default for 'priority_apply' will be False and the default for
'apply_order' will be 5.  This will allow modules to be ordered before or
after if the options are not supplied.


Configuration
-------------

No new configuration changes are required.


Database
--------

New columns will be added to the modules table of the Trove schema:

    =================  ============  ===========  ==============================
    Column             Type          Allow Nulls  Description
    =================  ============  ===========  ==============================
    priority_apply     tinyint(1)    No           Should this module be applied
                                                  before all non-priority ones.
                                                  Admin only option.
    apply_order        int(11)       No           Order that modules should be
                                                  applied in.  Value between
                                                  0-9 with lower order numbers
                                                  applied first.  Priority
                                                  modules can also ordered this
                                                  way.
    is_admin           tinyint(1)    No           This module was created or
                                                  updated by a user with admin
                                                  credentials.  Once this flag
                                                  is set, only an admin user
                                                  can subsequently update the
                                                  module.
    =================  ============  ===========  ==============================

Creating modules that have 'priority' will require admin credentials.  All
priority modules will be applied before non-priority ones, and will follow the
same apply_order sequence.

For example, given modules with the following priority/order, they will be
applied in the following order::

   ==============      ===========
   Priority Apply      Apply Order
   ==============      ===========
   Yes                 0
   Yes                 4
   Yes                 9
   No                  0
   No                  1
   No                  9
   ==============      ===========

Public API
----------

The following new options will be added to the payload of the module-create
and module-update ReST APIs:

Request::

    POST /v1.0/modules (or PATCH /v1.0/modules/{module_id})
    {
        <current payload>,
        'priority_apply': True,
        'apply_order': 5
    }

Response::

    {
        "module": {
            <current payload>,
            'priority_apply': True,
            'apply_order': 5
        }
    }


Response Codes::

    The response codes will remain the same

The is_admin flag will be set automatically, and as such will not need
to be passed in the payload.  If a module created by a non-admin is
updated by an admin, the is_admin flag will be set but only if an 'admin-only'
option is turned on.  Once a module is designated as 'admin' then only
a user with admin credentials can modify it from that time forward.

Public API Security
-------------------

This change is not expected to introduce any security concerns.

Python API
----------

New arguments to the module create and update methods will be added to
facilitate the ordering.


.. code-block:: python

    def module_create(self, module_type, name, description, contents,
                      datastore, datastore_version='all', auto_apply=False,
                      all_tenants=False, visible=True, live_update=False,
                      priority_apply=False, apply_order=5):
        """Create a new module."""

    def module_update(self, module, module_type=None, name=None,
                      description=None, contents=None, datastore=None,
                      datastore_version=None, auto_apply=None,
                      all_tenants=None, visible=None, live_update=None,
                      priority_apply=False, apply_order=5):
        """Update an existing module."""

CLI (python-troveclient)
------------------------

The following Trove CLI commands will support two new arguments,
priority_apply and apply_order.  priority_apply will be a flag
that requires admin credentials, and apply_order will be restricted
to an integer between 0-9.

- module-create        Creates a new module resource.
- module-update        Updates module details for a particular module
                       resource.

Internal API
------------

The internal API will change in that new fields will be included in the
module structure.  No coding changes are anticipated though.

Guest Agent
-----------

In the Guest Agent, the modules will be ordered based on the priority and
order values.  No other changes are anticipated with the exception that
the is_admin flag will now be taken from the module payload (if it exists)
instead of being inferred from other attributes.

Alternatives
------------

None


Dashboard Impact (UX)
=====================

The module detail panel will need to have two new attributes: priority-apply
and apply-order.  The first as a flag (defaulting to false) and the second
restricted to integer values between 0 and 9.  These should be added to the
python call to create or update a module.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
    [peterstac]

Milestones
----------

Newton

Work Items
----------

The work will be undertaken with the following tasks:

    * Client (Python and CLI) changes
    * Guest Agent changes to ensure the modules are ordered
      correctly


Upgrade Implications
====================

No upgrade issues are expected, however the Trove database will need
to be updated for the feature to work.


Dependencies
============

None.


Testing
=======

Scenario tests will be enhanced to include ordering (including
at least one priority module).  It may be difficult to test
that the ordering is adhered to (since this would require some
sort of dependency and there is only a ping driver plugin) so
this may have to be handled by unit tests only.


Documentation Impact
====================

The fact that modules can now be ordered should be added to the
documentation.


References
==========

None


Appendix
========

None
