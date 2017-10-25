..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..


======================================================
Implement root-enable/root-disable/root-show for Redis
======================================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Trove currently has support for enabling root user, disabling root user
and showing root-enabled status for database instances, but that functionality
is lacking for redis. This blueprint outlines a framework and API for
implementing authentication management for redis.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/root-enable-in-redis


Problem Description
===================

Trove does not currently support root-enable, root-disable, root-show for
redis instances.


Proposed Change
===============

Implement root-enable, root-disable and root-show API for redis. It will
support two scenarios including redis single instance and redis replica
instances which these operations only support master instance but can make
effect on slave instances.

This implementation does not support a cluster of redis instances.

Here are the details:

Root-enable
-----------

* Precondition checks to make sure that it's not cluster or slave instance to
  execute this action.

* Get slave instances of given instance.

* Try to get original auth password for the sake of rolling back.

* Do root enable for given instance. Considering it's a single instance or
  a master of redis replica sets, roll back once using original auth password
  and raise exception if any error occurs.

* If things go well, and there are some slave instances, get root password and
  use root password above to do root enable. Get failed slave instances' id
  if any, store them into a list.

* Return redis root created view alongside the failed slave instances' id list.

Root-disable
------------

* Precondition checks to make sure that it's not cluster or slave instance to
  execute this action.

* Get slave instances of given instance.

* Try to get original auth password for the sake of rolling back.

* Do root disable for given instance. Considering it's a single instance or
  a master of redis replica sets, roll back once using original auth password
  and raise exception if any error occurs.

* If things go well, and there are some slave instances, do root disable. Get
  failed slave instances' id if any, store them into a list.

* If there are any failed slaves, return http code 200 with failed slaves list.
  If not, just return None with http code 204.

Root-show
---------

Using root-show of mysql. It can satisfy what we ask for.

Configuration
-------------

Changing the follow configuration value:

.. code-block:: python

    cfg.StrOpt('root_controller',
               default='trove.extensions.redis.service.RedisRootController',
               help='Root controller implementation for redis.'),


Remove requirepass in trove/templates/redis/validation-rules.json to avoid
modifying authentication by configuration group.

Database
--------

None

Public API
----------

Change the return contents of root-enable and root-disable. Since redis does
not have a root user, just show '-' as user name. Return failed slaves if any.
For example:

.. code-block:: python

    {
        "failed_slaves": [
            "67c2f6d6-7c01-4ce9-bb18-aa951ca5a39b"
        ],
        "user": {
            "password": "bdQhBXVpk7TE689aGgqdNmJmg4qHdpdBegae",
            "name": "-"
        }
    }

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

Change the return content to meet API above.

Internal API
------------

None

Guest Agent
-----------

The work will require some implementation of the guest manager:

* Add requirepass and masterauth into redis.conf when executing root enable,
  and apply overrides to bring into effect without restarting redis service.
  Rebuild admin client to make sure guest agent can still talk to task manager
  after adding enabling/disabling root in redis, which has been done in this
  patch [1]_.

* Remove requirepass and masterauth in redis.conf when executing root disable,
  and apply overrides to bring into effect without restarting redis service.
  Still, rebuild admin client.


Alternatives
------------

We can achieve authentication management for redis by configuration group, but
it looks like less convenient than using root-enable and root-disable.


Dashboard Impact (UX)
=====================

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  fanzhang <zh.f@outlook.com>

Milestones
----------

Target Milestone for completion:
  Queens-Q2


Work Items
----------

* Implement redis root controller, service, models and views.

* Implement redis guest agent, including manager, service and models.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

Inside the int_tests.py, root_actions_groups will be added to redis supported
groups in order to reuse some scenario tests with proper modification to meet
the root actions functionality of redis.

Unittests will be added to test the derived controller functionality, for
example:

* Test root-enable on single redis instance.

* Test root-enable on master instance of redis replication.

* Test root-enable on slave instance of redis replication.

* Test root-enable with is_cluster=True.

* Test root-delete in the cases of above.

Unittests will be also added to test the implemented functions inside guest-
agent including enable_root and disable_root.


Documentation Impact
====================

The documentation [2]_ should be updated to add the following features:

* Successful response examples of enabling/disabling root in redis.

* Failed response examples of enabling/disabling root in redis.

But it is not mandatory to add.

References
==========

.. [1] https://bugs.launchpad.net/trove/+bug/1708376
.. [2] https://developer.openstack.org/api-ref/database/#users-users

Appendix
========

None.
