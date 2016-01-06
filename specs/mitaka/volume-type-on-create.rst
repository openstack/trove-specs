..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


==============================================
Add 'volume_type' parameter to instance create
==============================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Cinder allows for multiple storage backends.
When creating a volume, the 'volume_type' parameter will be used in
determining which type of backend to send to. [1]_
The user should be allowed to specify the backends for Trove volumes on
instance/cluster creation.


Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/volume-type-on-create


Problem Description
===================

Trove operators would like to expose different types of storage to their Trove
users to provide more flexibility in the types of configurations they can use
for their database instances and database clusters


Proposed Change
===============

An optional 'volume_type' property will be added to the volume information
accepted by the API for instance and cluster create API calls.
This property will be passed to the Cinder client when a new Trove volume gets
created. Default configuration value will be used if no volume_type is
specified by the user.


Configuration
-------------

None

Database
--------

None

Public API
----------

An optional 'volume_type' property will be added to the volume information
structure accepted by the instance and cluster create API calls.

API payload defining a volume of size '1' and Cinder volume type 'my-type-1':

.. code-block:: json

    'volume': {'size': '1', 'type': 'my-type-1'}

API payload defining a volume of size '1' and no Cinder volume type:

.. code-block:: json

    'volume': {'size': '1', 'type': None}
    'volume': {'size': '1'}

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

The volume_type value is a string name of the volume type as returned by
the 'cinder type-list' command. The value won't be validated on the client
site.

For instance creation an optional '--volume_type' argument will be added.
The volume type will be appended to the volume size in the volume
information structure. If volume support is disabled or '--size' argument
is not specified on instance create the 'volume_type' argument will be ignored.

.. code-block:: bash

    trove create ... --size 1 --volume_type my-type-1 ...


For cluster creation the '--instance' argument will be extended with a
'volume_type' option. If volume support is not enabled or volume size is not
specified the 'volume_type' option will be ignored.

.. code-block:: bash

    trove cluster-create ... --instance volume=1,volume_type=my-type-1 ...

Internal API
------------

A new 'volume_type' argument will be added where necessary.

Guest Agent
-----------

None

Alternatives
------------

None


Dashboard Impact (UX)
=====================

TBD (section added after approval)


Implementation
==============

Assignee(s)
-----------

<pmalik>

Milestones
----------

Mitaka-1

Work Items
----------

This work will consist of updates to the Trove client and server
code.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

The existing Trove tests will be extended to test the 'volume_type' argument.
New client tests will be added to cover the added arguments.


Documentation Impact
====================

The new 'volume_type' arguments on instance and cluster create commands need
to be documented.


References
==========

.. [1] https://wiki.openstack.org/wiki/Cinder-multi-backend


Appendix
========

None
