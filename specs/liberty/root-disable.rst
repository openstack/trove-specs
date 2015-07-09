..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

============
Root Disable
============

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/root-disable

Since there is the ability to enable a root user on an instance the
ability to disable the root user should be provided as well.

Problem Description
===================

Currently, the root user can be enabled on an instance.  It is expected
that the root user can also be disabled.

Disabling the root user should not change the ability of the command
root-show to determine if the root user has ever been enabled.


Proposed Change
===============

This change will add a new root-disable command.

The command will remove the root user from the specified instance.  No changes
will be made in the root_enable_history table from the execution of the
command.  This ensures the root-show command will continue to operate as
expected.

Configuration
-------------

None

Database
--------

None

Public API
----------

REST API:

    DELETE /instances/{id}/root

Public API Security
-------------------

None

Python API
----------

Python API in class Root:

    def delete(self, instance):
        """Implements root-disable API.

        Removes the root user for the specified db instance.

        :param instance: The instance from which the root user is removed from

        """

CLI (python-troveclient)
------------------------

CLI:

    trove root-disable <instance>

Internal API
------------

None

Guest Agent
-----------

The appropriate root disable method will added only for MySQL.  All other
datastores will also need to have the appropriate not implemented error.

Alternatives
------------

Another option is root-disable will simply call root-enable and not return
the password back to the user.  This alternative also has no impact on the
root-show.

However, an operator may believe the root user to be completely removed from
the database after the root-disable call is made.  Leaving the root user
may not be what the operator is expecting.

Discussion Summary
------------------
Some concerns were raised during the discussion of this blueprint.  The full
details can be found here https://review.openstack.org/#/c/189837/.

In summary the concerns revolved around the fact that after the user performs
a root enable the following issues can occur.

1. A security hole exists where a user can create an alternate root user,
   drop the existing root user and do a backup then restore leaving no trace
   that the root user has been enabled for the restored database and an
   "unknown" alternate root user is left in the restored database.
2. The enabled root user can change the management user access leaving the
   instance in a state that cannot be managed via Trove.

It was determined that adding the root-disable command does not cause or make
the concerns raised above to be any worse than already exists.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  dloi

Milestones
----------

liberty-1

Work Items
----------

- Implement CLI, Python API and REST API calls
- In the guest add disable_root method for MySQL database and not implemented
  stubs for all other datastores
- Unit and integration tests

Upgrade Implications
====================

None

Dependencies
============

None

Testing
=======

Add to existing root enable tests to test disabling the root user.

Documentation Impact
====================

New root-disable command needs to be added to the API documentation.

References
==========

None