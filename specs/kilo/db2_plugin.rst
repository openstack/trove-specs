..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

http://creativecommons.org/licenses/by/3.0/legalcode
..

=====================================
DB2 Express-C guest agent for Trove
=====================================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/db2-plugin-for-trove

Problem Description
==============================

The aim of this blueprint is to enable Trove to support a new datastore type - DB2,
in addition to the other SQL databases supported by Trove. For the first release, we
will be using DB2 Express-C v10.5.4(on Ubuntu) which is the free version of DB2 available
for enterprises.

The following features will be implemented: Launch, Reboot, Terminate, Resize and Users.

Proposed Change
==============================
To add support for this new datastore, we need to implement the following:

- Add a new diskimage-builder element for DB2 Express-C on Ubuntu
- Implement the various datastore features like:

    - Launch
    - Reboot
    - Terminate
    - Resize
    - Users

Configuration
--------------
A new configuration group for DB2 and the different configuration options specific to it
will be defined in /trove/common/cfg.py.

Some of the examples for the configuration options are:

- tcp_ports
- udp_ports
- backup_strategy
- backup_incremental_strategy
- mount_point
- volume_support
- device_path
- backup_namespace
- restore_namespace
- cluster_support
- replication_strategy

Database
------------
None

Public API
------------
None

Internal API
-------------
None

Guest Agent
------------
This requires implementing the various datastore features(API) for DB2 like Launch,
Reboot, Terminate, Backup, Restore, Resize and Users. This will include adding
the following new files specific to DB2 under the guestagent module:

- manager.py
- service.py
- system.py

These changes wont affect the behavior of the guestagent or its interaction with
other components.

Disk-Image-Builder Elements
---------------------------
DB2 Express-C is the free version of IBM DB2 database available for download. Inorder
to download the packages for DB2 Express-C, user needs to go through a free registration
process.

Unlike other datastores supported by Trove, DB2 Express-C cannot be downloaded from a
public repository. Hence the recommendation for creating DIB elements for DB2 Express-C is
to have users go through the registration process and download the DB2 Express-C packages
from the link provided in Reference Section [1]. The downloaded packages can be made
available to Trove by storing it in a private repository or on the local filesystem.
Create an extra-data.d element to then copy the package to the image. Use the environment
variable, DATASTORE_PKG_LOCATION to specify the location of the package.


Implementation
==============================

Assignee(s)
-----------
- mariamj@us.ibm.com (Primary Assignee)
- Susan Malaika (DB2 Contact)

Milestones
----------
Kilo


Dependencies
============
None

Testing
=======
- Add new unit tests for the DB2 Express-C guestAgent
- Add integration tests for end-to-end feature testing:

    - create/delete instance
    - create/delete/list databases
    - create/delete/list users

Documentation Impact
====================
The DB2 Express-C packages can be downloaded from the link provided in Reference Section
[1]. Click on the link "DB2 Express-C for Linux 64-bit". New users can either get an
IBM ID or click on the "Proceed without an IBM ID". Users will have to register first
inorder to download the packages. After downloading the packages, users can make it
accessible to Trove for building guest images by:

  - storing it in a private repository and defining the variable 'DATASTORE_PKG_LOCATION'
    to be the base url of the private repository
  - storing it on the local filesystem in a directory accessible to the DB2 DIB element
    and setting the 'DATASTORE_PKG_LOCATION' to point to this directory.

For example, DATASTORE_PKG_LOCATION can be set as follows:

  - export DATASTORE_PKG_LOCATION='/home/stack/db2'
  - export DATASTORE_PKG_LOCATION='http://www.foo.com/pkgs/db2'

References
==========
[1] DB2 Download Link: http://www-01.ibm.com/software/data/db2/express-c/download.html
