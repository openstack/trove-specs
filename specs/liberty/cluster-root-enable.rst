..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode
..

===================
Cluster root enable
===================

This spec is intended to add root enable support for clusters.

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/vertica-cluster-user-features


Problem Description
===================

Trove's cluster API currently does not support root enable.


Proposed Change
===============

Add support for root-enable for clusters, with optional user-provided
passwords. User supplied passwords are necessary to create a good user
experience in Horizon where enabling a root user should allow user input
rather than requiring the user to wait for a password to popup on a response
dialog.


Configuration
-------------

None

Database
--------

None

Public API
----------

This change will add a new /clusters/<cluster_id>/root resource which is
similar to the /root resource on instances with the addition of an optional
password.

Request::

  {
    "password": "secretsecret"
  }

- POST /v1.0/​[account-id]/clusters/<cluster_id>/root

Response::

  {
    "username": "root",
    "password": "secretsecret"
  }

- GET /v1.0/​<tenant_id>/clusters/<cluster_id>/root
- DELETE /v1.0/​​<tenant_id>/clusters/<cluster_id>/root

Public API Security
-------------------

The security of this API will be handled in the same manner as existing
implementations.

Python API
----------

None

CLI (python-troveclient)
------------------------

New cluster-root-enable and cluster-root-show commands will be added

Changes will effect:

troveclient/v1/root.py
troveclient/v1/shell.py
troveclient/v1/clusters.py

Internal API
------------

Root enablement support should be added for clusters. Changes include:

trove/extensions/routes/mysql.py
trove/extensions/mysql/service.py
trove/extensions/mysql/models.py
trove/guestagent/api.py

Guest Agent
-----------

The guestagent API will get a new enable_root(self, password) function
which allows optionally provided passwords to be supplied to a guest
agent. This function will be in addition to the existing function, allowing
for backwards compatibility with existing images.

Additionally, each guest agent datastore impl will need to implement
the enable_root(password) function.

Alternatives
------------

None


Implementation
==============

Assignee(s)
-----------

- jonathan.halterman@hp.com
- sharika.pongubala@hp.com

Milestones
----------

Liberty

Work Items
----------

- API changes
- Guest agent changes
- CLI changes
- Internal API changes


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

New unit and scenario tests will be added to assert that root enablement
works as expected at the cluster level


Documentation Impact
====================
The API changes to the clusters resource and the addition of the new
cluster root resource need to be documented.

References
==========

None