..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode
..

===============================
Add Vertica datastore for Trove
===============================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/vertica-db-support

Problem Description
===============================

The aim of this blueprint is to enable Trove to support a new datastore type -
HP Vertica 7.1 CE on Ubuntu.

Proposed Change
===============================
To add support for this new datastore, we need to implement the following:

- Add a new diskimage-builder element for Vertica

- Implement the various datastore features like::

    - Launch
    - Reboot
    - Terminate
    - Resize

Configuration
---------------
A new configuration group for Vertica and the different configuration options specific
to Vertica in trove/common/cfg.py.

Some of the examples for the configuration options are::

    - tcp_ports
    - udp_ports
    - backup_strategy
    - backup_incremental_strategy
    - replication_strategy
    - backup_namespace
    - restore_namespace
    - root_on_create
    - mount_point
    - volume_support
    - device_path

Database
------------
None

Public API
------------
None

Internal API
------------
None

Guest Agent
------------
- This requires implementing the various datastore feature for Vertica like Launch, Reboot, Terminate, Resize.
- This will include adding the following files specific to Vertica under the guestagent/datastore module::

    - manager.py
    - service.py
    - system.py

These changes will not affect the behavior of the guestagent or its interaction with other components.

Disk-Image-Builder Elements
---------------------------
- Disk-Image-Building would be a 2-step process, basically::

    - Download the Vertica package.
    - Execute the image-builder

- CE is the free edition of HP Vertica database available at www.vertica.com
- One needs to go through a free registration process, which enables a user to download the Vertica package.

- Image-building elements would expect user to copy $VERTICA_PACKAGE_FILE at $VERTICA_SOURCE.
- It would be then the job of DIB elements to::

    - Copy $VERTICA_PACKAGE_FILE from $VERTICA_SOURCE and host in the guest-image.
    - Install the essential requisite packages.
    - Install the Vertica package to guest-image.
    - Create the Vertica dba user named as "dbadmin", with desired group and path & time-zone settings setup to profile.
    - Create a base location to host database files.

Implementation
===============================

Assignee(s)
-----------
- sushil.kumar3@hp.com (Primary Assignee)
- saurabh.surana@hp.com
- jonathan.halterman@hp.com

Milestones
----------
"Kilo-3"

Dependencies
============
None

Testing
=======
- Vertica datastore would be tested using a 3rd party CI hosted by HP.
- New unit tests would be added for the Vertica guestagent.
- Integration tests needs to be added for end-to-end feature testing::

    - create/delete instance
    - resize instance

Documentation Impact
====================
- Documentation would need the update on::

    - HP Vertica being added as new datastore.
    - Capabilities of Trove for HP Vertica datastore.
    - How to build the guest-image required for hosting HP Vertica guest.

References
==========
[1] https://my.vertica.com/docs/7.1.x/HTML/index.htm

[2] https://my.vertica.com/download-community-edition/#EE

[3] https://my.vertica.com/hp-vertica-community-edition-software-license-agreement/
