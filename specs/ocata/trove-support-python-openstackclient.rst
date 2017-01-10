..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..


=======================================
Trove support in python-openstackclient
=======================================

Implement a new set of trove commands as python-openstackclient plugins.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/trove-support-in-python-openstackclient


Problem Description
===================

python-openstackclient is becoming the default command line client for many
OpenStack projects. Trove would benefit from implementing all of its client
commands as a single python-openstackclient plugin implemented in the
python-troveclient repository.

Proposed Change
===============

The intent of this spec is to identify the commands to be implemented and
establish conventions for command and argument names. This spec is not
intended to be a full and correct specification of command and argument names.
The details can be left to the code reviews for the commands themselves.

The following conventions will be adopted for command names:

* As per the ``OpenStackClient`` convention, the command name shall always take
  the following form:

.. code-block:: bash

    openstack [<global-options>] <object-1> <action> [<object-2>] \
              [command-arguments]

The following conventions will be adopted for arguments and argument flags:

* Single character flags will be avoided as per the ``openstack`` convention,
  except for very common arguments.

* When the database or cluster name and ID are specified it will be the first
  and second positional arguments respectively after the full command names.

* When an argument is required it will be a positional argument.

The following ``trove`` commands are already implemented for ``openstack``:

.. code-block:: bash

    trove secgroup-add-rule
    openstack security group rule create

    trove secgroup-delete-rule
    openstack security group rule delete

    trove secgroup-list
    openstack security group list

    trove secgroup-list-rules
    openstack security group rule list


The following ``trove`` commands will be implemented for ``openstack``
initially suggesting these command names:

.. code-block:: bash

    trove backup-create <instance> <name>
    openstack database backup create <instance> <name>

    trove backup-delete <backup>
    openstack database backup delete <backup>

    trove backup-list
    openstack database backup list

    trove backup-list-instance <instance>
    openstack database backup list <instance>

    trove backup-show <backup>
    openstack database backup show <backup>

    trove cluster-create <name> <datastore> <datastore_version>
    openstack database cluster create <name> <datastore> <datastore_version>

    trove cluster-delete <cluster>
    openstack database cluster delete <cluster>

    trove cluster-list
    openstack database cluster list

    trove cluster-modules <cluster>
    openstack database module list cluster <cluster>

    trove cluster-show <cluster>
    openstack database cluster show <cluster>

    trove configuration-attach <instance> <configuration>
    openstack database configuration add <instance> <configuration>

    trove configuration-create <name> <values>
    openstack database configuration create <name> <values>

    trove configuration-default <instance>
    openstack database configuration show <instance>

    trove configuration-delete <configuration_group>
    openstack database configuration delete <configuration_group>

    trove configuration-detach <instance>
    openstack database configuration remove <instance>

    trove configuration-instances <configuration_group>
    openstack database configuration list --instance <configuration_group>

    trove configuration-list
    openstack database configuration list

    trove configuration-parameter-list <datastore_version>
    openstack database configuration parameter list <datastore_version>

    trove configuration-parameter-show <datastore_version> <parameter>
    openstack database configuration parameter show <datastore_version> <parameter>

    trove configuration-patch <configuration_group> <values>
    openstack database configuration set --patch <configuration_group> <values>

    trove configuration-show <configuration_group>
    openstack database configuration show <configuration_group>

    trove configuration-update <configuration_group> <values>
    openstack database configuration set <configuration_group> <values>

    trove create <name> <flavor>
    openstack database cluster create <name> <datastore> <datastore_version>

    trove database-create <instance> <name>
    openstack database add <instance> <name>

    trove database-delete <instance> <database>
    openstack database remove <instance> <database>

    trove database-list <instance>
    openstack database list <instance>

    trove datastore-list
    openstack datastore list

    trove datastore-show <datastore>
    openstack datastore show <datastore>

    trove datastore-version-list <datastore>
    openstack datastore version list <datastore>

    trove datastore-version-show <datastore_version>
    openstack datastore version show <datastore_version>

    trove delete <instance>
    openstack database cluster delete <cluster>

    trove detach-replica <instance>
    openstack database replica unset <instance>

    trove flavor-list
    openstack database flavor list

    trove flavor-show <flavor>
    openstack database flavor show <flavor>

    trove limit-list
    openstack database limits list

    trove list
    openstack database instance list
    openstack database cluster list

    trove module-apply <instance> <module>
    openstack database instance set module <instance> <module>

    trove module-create <name> <type> <filename>
    openstack database module create <name> <type> <filename>

    trove module-delete <module>
    openstack database module delete <module>

    trove module-instances <module>
    openstack database instance list module <module>

    trove module-list
    openstack database module list

    trove module-list-instance <instance>
    openstack database module list instance <instance>

    trove module-query <instance>
    openstack database instance list module <instance> --status

    trove module-remove <instance> <module>
    openstack database instance remove module <instance> <module>

    trove module-retrieve <instance>
    openstack database instance show module <instance>

    trove module-show <module>
    openstack database module show <module>

    trove module-update <module>
    openstack database module set <module>

    trove resize-instance <instance> <flavor>
    openstack database instance resize <instance> <flavor>
    openstack database cluster resize <cluster> <flavor>

    trove resize-volume <instance> <size>
    openstack database instance volume resize <instance> <size>
    openstack database cluster volume resize <cluster> <size>

    trove restart <instance>
    openstack database instance restart <instance>
    openstack database cluster restart <cluster>

    trove root-enable <instance_or_cluster>
    openstack database set --root <instance_or_cluster>

    trove root-show <instance_or_cluster>
    openstack database show --root <instance_or_cluster>

    trove show <instance>
    openstack database cluster show <cluster>

    trove update <instance>
    openstack database cluster set <cluster>

    trove user-create <instance> <name> <password>
    openstack database user create <instance> <name> <password>

    trove user-delete <instance> <name>
    openstack database user delete <instance> <name>

    trove user-grant-access <instance> <name> <databases>
    openstack database user add --access <instance> <name> <databases>

    trove user-list <instance>
    openstack database user list <instance>

    trove user-revoke-access <instance> <name> <database>
    openstack database user remove --access <instance> <name> <database>

    trove user-show <instance> <name>
    openstack database user show <instance> <name>

    trove user-show-access <instance> <name>
    openstack database user show --access <instance> <name>

    trove user-update-attributes <instance> <name>
    openstack database user set --attributes <instance> <name>


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

A new directory named osc will be created under /troveclient/osc
for the ``OpenStackClient`` plugin and the commands mentioned above.

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

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  twm2016

Dashboard assignee:
  None

Milestones
----------

Target Milestone for completion:
      Ocata-3

Work Items
----------

CLI commands as stated above.
Integration tests
Functional tests

Upgrade Implications
====================

None

Dependencies
============

python-openstackclient
osc-lib

Testing
=======

Functional tests will be located in: /troveclient/tests/osc/
Functional testing will test the inputs and outputs of listed commands.
Integration tests will verify the ``OpenStackClient`` plugin is working with
other projects. These should be placed in /trove/tests/tempest/tests/api

Documentation Impact
====================

OpenStack Client adoption list will be updated to include python-troveclient.

References
==========

http://docs.openstack.org/developer/python-openstackclient/commands.html
http://docs.openstack.org/cli-reference/trove.html

Appendix
========

None

