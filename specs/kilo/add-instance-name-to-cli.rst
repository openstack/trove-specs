..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

=======================================================
 Add instance name as parameter to various CLI commands
=======================================================

Blueprint:

https://blueprints.launchpad.net/trove/+spec/add-instance-name-to-cli

The proposal is to allow instance-name to be specified wherever instance-ID
is currently used throughout the CLI.

Problem description
===================

Currently, only the "trove show" command will take instance-ID or
instance-name as its parameter. There are many more commands in the
CLI that require an instance reference as a parameter but require that
the instance-ID be used. It would be helpful to customers to be able
to use instance-ID or instance-name interchangeably throughtout the CLI.


Proposed change
===============

Allow instance-id or instance-name to be passed in for the following commands:

- backup-create
- backup-list-instance
- configuration-attach
- configuration-default
- configuration-detach
- database-create
- database-delete
- database-list
- detach-replica
- delete
- metadata-create
- metadata-delete
- metadata-edit
- metadata-list
- metadata-show
- metadata-update
- resize-flavor
- resize-instance
- resize-volume
- restart
- root-enable
- root-show
- update
- user-create
- user-delete
- user-grant-access
- user-list
- user-revoke-access
- user-show
- user-show-access
- user-update-attributes

For example, ``trove delete`` currently looks like this:

::

    usage: trove delete <instance>

    Deletes an instance.

    Positional arguments:
        <instance>  ID of the instance.

The proposal is to make it look like this:

::

    usage: trove delete <instance>

    Deletes an instance.

    Positional arguments:
        <instance>  ID or name of the instance.

This will be a CLI change only.

Currently the ``trove show`` command will display an error if there is
more than one instance with the name provided. The error indicates that,
in this case, the instance ID must be used. This behavior will be preserved
and used across all the commands mentioned above.

Configuration
-------------

None

Database
--------

None

Public API
----------

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

Implementation
==============

Assignee(s)
-----------

Primary assignees:

- 0-doug (dougshelley66)
- peterstac

Milestones
----------

Target Milestone for completion:
  Kilo-2

Work Items
----------

1. Go through python-troveclient/troveclient/v1/shell.py and call
   _find_instance(cs, args.instance) ahead of the "real" work in each "do_<>"
   method.
2. Alter the help text in shell.py to indicate the use of name or ID.
3. Alter the existing unit tests as appropriate.

Dependencies
============

None

Testing
=======

If we had Tempest coverage for the CLI it would be adjusted to exercise
passing instance name to all the altered commands. Also, there is an
existing LP bug [1] that indicates we should write tests for the CLI.

Both of these are considered out of scope for this BP.

[1] https://bugs.launchpad.net/python-troveclient/+bug/1314793

Documentation Impact
====================

The help text for the aforementioned commands will be altered to now
include instance name as a valid parameter. I believe that the CLI
documentation is generated from the code.

References
==========

None
