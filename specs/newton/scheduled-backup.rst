..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..


=================
Scheduled Backups
=================

Trove currently has no way to schedule backups of instances.  This
document proposes to implement scheduled backups by utilizing Mistral
workflows.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/scheduled-backup


Problem Description
===================

Trove does not support scheduled backups.


Proposed Change
===============

Scheduled backups will be supported by utilizing Mistral workflows [1]_.
The Trove python API will be extended to provide a Trove centric
interface to Mistral workflows.

A Trove workbook will be loaded into Mistral to support calling the
trove.backup_create python API via a schedule.  Trove python API
methods will be added to support scheduling backups and listing
scheduled backups and their executions.  Using these Trove commands a user
will be able to manage backup schedules (create/delete/list, etc.) and view the
executions of said schedules.  Like is done with Nova flavors however, Trove
will not actually execute any commands itself, just pass them down to Mistral.
Any errors that occur will be visible when viewing the executions, however
will be limited to whatever Mistral exposes.

All changes will be within the python-troveclient module with the exception
of the workbook.  This will be available in the Trove repo to (possibly)
be loaded by the devstack plugin if Mistral is enabled.

See the `Appendix`_ for a sample Trove workbook.



Configuration
-------------

No configuration changes.

Database
--------

No database changes.

Public API
----------

No changes to the REST API.

Public API Security
-------------------

No security impact.

Python API
----------

Note: The referenced 'cron pattern' is the standard cron expression. [2]_

.. code-block:: python

    def schedule_create(self, instance, pattern, name,
                        description=None, parent_id=None,
                        mistral_client=None):
        """Create a new schedule to backup the given instance.

        :param instance: instance to backup.
        :param pattern: cron pattern for schedule.
        :param name: name for backup.
        :param description: (optional).
        :param parent_id: base for incremental backup (optional).
        :returns: :class:`Backups`
        """

    def schedule_list(self, instance, mistral_client=None):
        """Get a list of all backup schedules for an instance.

        :param: instance for which to list schedules.
        :rtype: list of :class:`Schedule`.
        """

    def schedule_show(self, schedule, mistral_client=None):
        """Get details of a backup schedule.

        :param: schedule to show.
        :rtype: :class:`Schedule`.
        """

    def schedule_delete(self, schedule, mistral_client=None):
        """Remove a given backup schedule.

        :param schedule: schedule to delete.
        """

    def execution_list(self, schedule, mistral_client=None,
                       marker='', limit=None):
        """Get a list of all executions of a scheduled backup.

        :param: schedule for which to list executions.
        :rtype: list of :class:`ScheduleExecution`.
        """

    def execution_delete(self, execution, mistral_client=None):
        """Remove a given schedule execution.

        :param execution: id of execution to remove.
        """

CLI (python-troveclient)
------------------------

Load trove workbook
///////////////////

.. code-block:: bash

    $ mistral workbook-create ~/mwj/mistral/trove.yaml

Create Schedule
///////////////

.. code-block:: bash

    $ trove schedule-create m "*/2 * * * *" myback
    +---------------------+----------------------------------------------------------------------------------------------------------------+
    | Property            | Value                                                                                                          |
    +---------------------+----------------------------------------------------------------------------------------------------------------+
    | created_at          | 2016-06-14 14:47:16.865731                                                                                     |
    | id                  | fb149a29-be9b-49c1-a2f7-ca6c1213896f                                                                           |
    | input               | {"instance": "5328f62a-d999-4be3-90bb-83cc6af4469c", "description": null, "parent_id": null, "name": "myback"} |
    | instance            | 5328f62a-d999-4be3-90bb-83cc6af4469c                                                                           |
    | name                | myback                                                                                                         |
    | next_execution_time | 2016-06-14 07:48:00                                                                                            |
    | parent_id           | None                                                                                                           |
    | pattern             | */2 * * * *                                                                                                    |
    +---------------------+----------------------------------------------------------------------------------------------------------------+

List Schedule
/////////////

.. code-block:: bash

    $ trove schedule-list m
    +--------------------------------------+--------+-------------+---------------------+
    | ID                                   | Name   | Pattern     | Next Execution Time |
    +--------------------------------------+--------+-------------+---------------------+
    | fb149a29-be9b-49c1-a2f7-ca6c1213896f | myback | */2 * * * * | 2016-06-14 07:50:00 |
    +--------------------------------------+--------+-------------+---------------------+

Show Schedule
/////////////

.. code-block:: bash

    trove schedule-show fb149a29-be9b-49c1-a2f7-ca6c1213896f
    +---------------------+----------------------------------------------------------------------------------------------------------------+
    | Property            | Value                                                                                                          |
    +---------------------+----------------------------------------------------------------------------------------------------------------+
    | created_at          | 2016-06-14 14:47:16                                                                                            |
    | id                  | fb149a29-be9b-49c1-a2f7-ca6c1213896f                                                                           |
    | input               | {"instance": "5328f62a-d999-4be3-90bb-83cc6af4469c", "description": null, "parent_id": null, "name": "myback"} |
    | instance            | 5328f62a-d999-4be3-90bb-83cc6af4469c                                                                           |
    | name                | myback                                                                                                         |
    | next_execution_time | 2016-06-14 07:52:00                                                                                            |
    | parent_id           | None                                                                                                           |
    | pattern             | */2 * * * *                                                                                                    |
    | updated_at          | 2016-06-14 14:49:59                                                                                            |
    +---------------------+----------------------------------------------------------------------------------------------------------------+


Delete Schedule
///////////////

.. code-block:: bash

    $ trove schedule-delete fb149a29-be9b-49c1-a2f7-ca6c1213896f

List Executions
///////////////

.. code-block:: bash

    trove execution-list fb149a29-be9b-49c1-a2f7-ca6c1213896f
    +--------------------------------------+---------------------+---------+-------------------------------+
    | ID                                   | Execution Time      | State   | Output                        |
    +--------------------------------------+---------------------+---------+-------------------------------+
    | 38ef2289-4330-4554-8574-4b5351f69713 | 2016-06-14 14:49:59 | SUCCESS | {"status": "Backup complete"} |
    | 3713355a-b65e-44e0-ac43-150b863a6e6e | 2016-06-14 14:51:59 | SUCCESS | {"status": "Backup complete"} |
    +--------------------------------------+---------------------+---------+-------------------------------+

Delete Executions
/////////////////

.. code-block:: bash

    $ trove execution-delete 3713355a-b65e-44e0-ac43-150b863a6e6e

Internal API
------------

No internal API changes.

Guest Agent
-----------

No guest changes.

Alternatives
------------

The alternative would be for Trove to implement its own scheduling mechanism.


Dashboard Impact (UX)
=====================

An action will be added to the instance actions pulldown to show the
scheduled backups for an instance.  This will lead to a chain of
panels for scheduled backups, details of a schedule, and executions of
a schedule.  The scheduled backups list will have an option to create
a new schedule.  The panels which list schedules and executions will
have an action to delete the corresponding resource.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  6-morgan

Dashboard assignee:
  duktesora


Milestones
----------

Target Milestone for completion:
  Newton

Work Items
----------

- already prototyped [3]_
- implement unit tests


Upgrade Implications
====================

No upgrade implications.


Dependencies
============

n/a


Testing
=======

If we add support in scenario tests (through the python API) that would
mean we'd require Mistral to be installed.  As such, no scenario tests
will be created.


Documentation Impact
====================

New python API methods and CLI commands would need to be documented.


References
==========

.. [1] https://wiki.openstack.org/wiki/Mistral
.. [2] https://en.wikipedia.org/wiki/Cron#CRON_expression
.. [3] https://review.openstack.org/#/c/329160/


Appendix
========

This is an idea of what the Trove workbook for Mistral would look like:

.. code-block:: yaml

    ---
    version: '2.0'

    name: trove

    description: Trove Workflows

    workflows:

      backup_create:
        input: [instance, name, description, parent_id]
        output:
          status: <% $.message %>

        tasks:
          backup_create:
            action: trove.backups_create instance=<% $.instance %> name=<% $.name %> description=<% $.description %> parent_id=<% $.parent_id %>
            publish:
              message: <% 'Backup complete' %>
