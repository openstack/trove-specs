..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/template.rst

..


================
Instance Upgrade
================

Trove needs to address how guest instances will update their database
software, the Trove guest agent, and the underlying operating system.
This blueprint proposes a technique which will allow guest instances
to be updated by migrating the data volume to a new instance based on
an updated guest image.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/instance-upgrade


Problem Description
===================

Trove creates a database instance by creating a nova instance from a
provided operating system image and attaching a volume to the instance
to hold the user's data.  By using a known image with the database
software preconfigured, an operator can ensure that the user will
receive a known version of database software, configured with an
operating system certified to work with that version of database
software.  This technique eliminates many of the ambiguities of
provisioning applications, allowing an operator to provide a published
level of service to the database user.

Unfortunately, running database instances aren't static over their
lifetimes.  Over time, it may be necessary for an instance to be
upgraded with security patches, new database software, or updates to
the Trove guest agent.  The cloud operator and the end user must be
provided with a way to migrate their databases to new operating
environments.

In summary, there are a number of changes that a database instance
might be subjected to over time, and this spec addresses applying
these types of changes.  These include (but are not necessarily
limited to):

* operating system security patches
* database security patches
* database version upgrades
* Trove guest agent upgrades
* OpenStack version upgrades
* operating system upgrades


Proposed Change
===============

The traditional approach to system upgrades is to simply execute
system utilities such as "apt-get upgrade" to upgrade all or parts of a
running system.  For large installations, this technique could be
automated by tools such as Ansible or Salt to apply the changes
to many systems.  This approach isn't ideal for
database-as-a-service as there is little control over which components
are upgraded, and to which version; an update could leave a database
instance in a state where the database does not operate properly, or
could even cause the data itself to become corrupted.

It is crucial that Trove develop a method to update instances which
provides a high probability of leaving the database in a safe,
consistent, and usable state.

To ensure a safe, consistent state, this blueprint proposes a
technique for upgrading an instance which transitions it from one
known image to a new known image running updated software.  The full
state of each instance state will be known.  At its core, this
technique will involve detaching the volume containing the
database data and attaching it to a new instance based on a different
(updated) image.

The bulk of the "variable" data on a Trove instance exists on the
attached volume where the database stores its data.  There is also
some operating system state which must be preserved during this
transition, consisting primarily of networking data (the instance name
and ip address), some Trove configuration data (guest_info.conf and
trove-guestagent.conf), and the database configuration data (such as
/etc/mysql).

The core of this technique will be based on the rebuild API provided
by Nova.  The Nova rebuild function upgrades a running instance to a
new image, ensuring that the networking configuration is applied to
the new instance.  The newly created instance will come up with the
same network configuration (ip, hostname, and Neutron configuration)
as the instance from which it was created.  Trove guest functionality
will be added to allow the guest to capture additional state about the
instance (primarily database configuration), and re-apply that state
to the system after rebuild.  The result will be a running,
connectable database provisioned on a new instance running updated
software.

The selection of image to upgrade to will be based on the current
datastore_version mechanism.  Essentially, the user will be allowed to
upgrade an instance to a newer datastore_version of its datastore.
Safeguards will be put in place to ensure that the user is selecting
an appropriate datastore_version to upgrade to; for example, the user
would only be allowed to upgrade a mysql instance from
datastore_version 5.5 to 5.6, not to 5.0 or 6.7.


Configuration
-------------

No configuration changes are planned.

Database
--------

A future blueprint will outline the changes necessary to support the
upgrade constraints on datastore_versions; this specification will
be limited to implementing the upgrade functionality without the
constraints.

Public API
----------

A new REST API call will be added in support of this functionality.

REST API: PATCH /instances/<instance id>
REST body:

.. code-block:: json

    {
        "instance": {
            "datastore_version": "<datastore_version_uuid>"
        }
    }

REST result:

.. code-block:: json

    {}

REST return codes:

    202 - Accepted.
    400 - BadRequest. Server could not understand request.
    404 - Not Found. <datastore_version_id> not found.

Public API Security
-------------------

There are no envisioned security implications.

Python API
----------

A new method will be implemented in the trove API.  This method will
upgrade a instance to the image specified by the provided
datastore_version.

.. code-block:: python

    upgrade(instance, datastore_version)

:instance: the instance to upgrade
:datastore_version: the datastore version, or its id, to which the
                    trove instance will be upgraded


CLI (python-troveclient)
------------------------

A new CLI call will be implemented.  This new call will upgrade a
instance to the image specified by the provided datastore_version.

.. code-block:: bash

    trove upgrade <instance> <datastore_version>

:instance: the instance to upgrade
:datastore_version: the datastore version to which the instance will
                    be upgraded

Internal API
------------

A new method will be added in support of this functionality.

.. code-block:: python

    def upgrade(self, instance_id, datastore_version_id):
        LOG.debug("Making async call to upgrade guest to %s "
                  % datastore_version_id)

        cctxt = self.client.prepare(version=self.version_cap)
        cctxt.cast(self.context, "upgrade", instance_id=instance_id,
                   datastore_version_id=datastore_version_id)


Guest Agent
-----------

Two new operations will be implemented in the guest agent API.  It is
expected that each datastore will (optionally) override these methods
to implement any needed functionality before and after the image
upgrade proceeds.  Mysql, for example, would use these methods to copy
its configuration data from /etc/mysql to the data volume before the
image upgrade, copying them back and restarting the mysql server after
the image upgrade.

It is expected that the pre_upgrade method will validate that it is
possible to perform the requested upgrade; for example, there may be a
configuration override specified for an instance which is not
compatible with the new datastore_version.  In the event that an
upgrade cannot be performed, the pre_upgrade method will raise an
exception - any exception will cause the taskmanager to abort the
upgrade process for that instance.

.. code-block:: python

    def pre_upgrade(self):
        """Prepare the guest for upgrade."""
        LOG.debug("Sending the call to prepare the guest for upgrade.")
        return self._call("pre_upgrade", AGENT_HIGH_TIMEOUT, self.version_cap)

    def post_upgrade(self, upgrade_info):
        """Recover the guest after upgrading the guest's image."""
        LOG.debug("Recover the guest after upgrading the guest's image.")
        self._call("post_upgrade", AGENT_HIGH_TIMEOUT, self.version_cap)

Two mechanisms are available for the pre_upgrade to communicate
information to the post_upgrade.  First, the value returned from the
pre_upgrade step is passed to the post_upgrade step as the
*upgrade_info* parameter; the guest is free to use this value as it
sees fit, though it would typically be used to exchange a dictionary
of configuration data.  The second mechanism the guest will use to
pass information beween phases is by storing configuration data on the
data volume; this would typically be used for large configuration
files.

It is expected that if the Nova rebuild command does not return an
exception before beginning the rebuild process, the rebuild will
succeed.  Should the rebuild fail, the instance will be moved to an
ERROR state and no attempt will be made to recover the instance;
operator intervention will be required.  Should the post_upgrade
return an exception, the instance will be transitioned to an ERROR
state.


Alternatives
------------

The alternative to upgrading images is to upgrade via apt-get or yum
in the running instance.  While this is the normal procedure for
upgrading instances, it has undesired implications for Trove.  Trove
aims to provide a known service level, but upgrading a running
instance has the potential to leave an instance in an unknown state.
There could also be issues around installations which don't allow
trove instances to access the internet directly as trove would have to
provide some mechanism for delivering all of the deb/rpm packages
required to update an instance.


Dashboard Impact (UX)
=====================

TBD


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

This feature has been already been prototyped.  The work required to
bring the prototype in line with this spec is:

* The prototype uses image id rather than datastore_version
* add trove.upgrade.start/end/error notifications
* implement unit tests
* investigate if int-tests need to be updated for this feature
* document the upgrade procedure

Upgrade Implications
====================


Dependencies
============

n/a


Testing
=======

Unit tests will be added as appropriate.

An int-test will be added that tests upgrading an instance to the
image that it is already running.



Documentation Impact
====================

The "trove upgrade" command, and its corresponding python API, will
need to be documented.


References
==========

n/a

Appendix
========

n/a
