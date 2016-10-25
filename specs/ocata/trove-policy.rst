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


====================
Trove Policy Support
====================

Trove needs to provide users with more fine-grained control over which
users/roles can access which APIs.
The Oslo Policy library provides support for RBAC policy enforcement across all
OpenStack services.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/trove-policy


Problem Description
===================

Trove currently does not have a unified way of role-based access control.
It needs to provide users with more fine-grained control over which
users/roles can access which APIs.


Proposed Change
===============

Add Oslo policy check calls on all user-facing APIs. [1]_
Also see `Appendix`_ for the list of proposed rules.

The checks will be implemented by means of Oslo policy 'enforce' call
at the beginning of each Trove API.

The call will be given extra information, parent 'tenant_id' (AKA the owner),
on the target object (e.g. deleted instance in trove-delete API,
updated configuration group in configuration-patch API).
This will allow users to use this information within their rules.

Actions that do not have a particular target (e.g. trove-create, trove-list)
will get the tenant itself as the target.

Actions that involve multiple rules will check all of them simultaneously.
One good example of this is trove-create. If the policy does not allow creating
users or applying modules the end user should not be allowed to create a
new instance with initial users and modules applied either.

The Policy engine used will be >= 1.9.0 which supports new registered policy
rules. While being fully backwards-compatible the registered rules allow for
more robust development.

Configuration
-------------

None

Database
--------

None

Public API
----------

All API calls may rise 'PolicyNotAuthorized' (HTTP 403) if the request
is not authorized by the policy framework.
The default access rules will be set to mimic the current behavior
(i.e. users can freely execute operations on their own tenant).

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

Work will be delivered in a single patch set.


Upgrade Implications
====================

None


Dependencies
============

Python library 'oslo.policy>=1.9.0' will be required.


Testing
=======

Unittests will be added to cover the policy framework.
Scenario tests will be testing the default behavior
(matching the existing behavior).


Documentation Impact
====================

The exposed policy rules and policy.json file should be documented
(see `Appendix`_).


References
==========

.. [1] Information on the rule engine and policy.json file http://docs.openstack.org/mitaka/config-reference/policy-json-file.html


Appendix
========

Proposed contents of 'policy.json'
(Note: datastore and flavor APIs are unrestricted by default):

.. code-block:: python

   {
       "admin_or_owner":  "role:admin or is_admin:True or tenant:%(tenant)s",
       "default": "rule: admin_or_owner",

       "instance:create": "rule:admin_or_owner",
       "instance:delete": "rule:admin_or_owner",
       "instance:index": "rule:admin_or_owner",
       "instance:show": "rule:admin_or_owner",
       "instance:update": "rule:admin_or_owner",
       "instance:edit": "rule:admin_or_owner",
       "instance:restart": "rule:admin_or_owner",
       "instance:resize_volume": "rule:admin_or_owner",
       "instance:resize_flavor": "rule:admin_or_owner",
       "instance:reset_password": "rule:admin_or_owner",
       "instance:promote_to_replica_source": "rule:admin_or_owner",
       "instance:eject_replica_source": "rule:admin_or_owner",
       "instance:configuration": "rule:admin_or_owner",
       "instance:guest_log_list": "rule:admin_or_owner",
       "instance:backups": "rule:admin_or_owner",
       "instance:module_list": "rule:admin_or_owner",
       "instance:module_apply": "rule:admin_or_owner",
       "instance:module_remove": "rule:admin_or_owner",

       "instance:extension:root:create": "rule:admin_or_owner",
       "instance:extension:root:delete": "rule:admin_or_owner",
       "instance:extension:root:index": "rule:admin_or_owner",

       "instance:extension:user:create": "rule:admin_or_owner",
       "instance:extension:user:delete": "rule:admin_or_owner",
       "instance:extension:user:index": "rule:admin_or_owner",
       "instance:extension:user:show": "rule:admin_or_owner",
       "instance:extension:user:update": "rule:admin_or_owner",
       "instance:extension:user:update_all": "rule:admin_or_owner",

       "instance:extension:user_access:update": "rule:admin_or_owner",
       "instance:extension:user_access:delete": "rule:admin_or_owner",
       "instance:extension:user_access:index": "rule:admin_or_owner",

       "instance:extension:database:create": "rule:admin_or_owner",
       "instance:extension:database:delete": "rule:admin_or_owner",
       "instance:extension:database:index": "rule:admin_or_owner",
       "instance:extension:database:show": "rule:admin_or_owner",

       "cluster:create": "rule:admin_or_owner",
       "cluster:delete": "rule:admin_or_owner",
       "cluster:index": "rule:admin_or_owner",
       "cluster:show": "rule:admin_or_owner",
       "cluster:show_instance": "rule:admin_or_owner",
       "cluster:action": "rule:admin_or_owner",

       "cluster:extension:root:create": "rule:admin_or_owner",
       "cluster:extension:root:delete": "rule:admin_or_owner",
       "cluster:extension:root:index": "rule:admin_or_owner",

       "backup:create": "rule:admin_or_owner",
       "backup:delete": "rule:admin_or_owner",
       "backup:index": "rule:admin_or_owner",
       "backup:show": "rule:admin_or_owner",

       "configuration:create": "rule:admin_or_owner",
       "configuration:delete": "rule:admin_or_owner",
       "configuration:index": "rule:admin_or_owner",
       "configuration:show": "rule:admin_or_owner",
       "configuration:instances": "rule:admin_or_owner",
       "configuration:update": "rule:admin_or_owner",
       "configuration:edit": "rule:admin_or_owner",

       "configuration-parameter:index": "rule:admin_or_owner",
       "configuration-parameter:show": "rule:admin_or_owner",
       "configuration-parameter:index_by_version": "rule:admin_or_owner",
       "configuration-parameter:show_by_version": "rule:admin_or_owner",

       "datastore:index": "",
       "datastore:show": "",
       "datastore:version_show": "",
       "datastore:version_show_by_uuid": "",
       "datastore:version_index": "",
       "datastore:list_associated_flavors": "",
       "datastore:list_associated_volume_types": "",

       "flavor:index": "",
       "flavor:show": "",

       "limits:index": "rule:admin_or_owner",

       "module:create": "rule:admin_or_owner",
       "module:delete": "rule:admin_or_owner",
       "module:index": "rule:admin_or_owner",
       "module:show": "rule:admin_or_owner",
       "module:instances": "rule:admin_or_owner",
       "module:update": "rule:admin_or_owner"
   }
