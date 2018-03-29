..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..


===========================================
Adapt to file injection deprecation in nova
===========================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Trove currently uses `--personality` to inject files while booting an instance
via Nova api. Unfortunately, this parameter is deprecated from Queens release,
nova microversion 2.57. As bp `Deprecate file injection` [1]_ mentioned,
the code to support it would remain, but having a microversion boundary would
give Nova the ability to eventually remove the code in the future. In
this spec, we try to adapt to file injection deprecation and implement another
way to inject files into instance.


Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/adapt-to-file-injection-deprecation-in-nova


Problem Description
===================

Nova deprecates file injection by popping out `--personality` parameter in
request schema of microversion 2.57, then no value of `--personality` would
be passed to Nova api service. It's the current way using this parameter to
inject files in Trove. We're facing the risk that it would break Trove
completely.


Proposed Change
===============

Using `--user-data` is one of the alternatives to inject files while booting
an instance.

Here is what we are going to do:

* Reorganize function ``trove.instance.models.BaseInstance#get_injected_files``
  to get the files contents, injected path, owner and permission, then build an
  ``InjectedFile`` object. In case of injecting multiple files into instance,
  we should build and return an ``InjectedFile`` object list.

* Change ``trove.taskmanager.models.FreshInstanceTasks#_prepare_userdata``.
  Build cloud-config scripts based on ``InjectedFile`` object list. If there is
  a `<datastore_manager>.cloudinit` script, e.g, mysql.cloudinit, we should
  detect the format of the script, and then convert it alongside with
  `cloud-config scripts` [2]_ into a mime multi part file [3]_ in case that
  we have to pass more than one type of data to cloud-init. So here should be
  two main helpers, one for organizing cloud-config scripts which looks like
  below:

  .. code-block:: yaml

      #cloud-config
      write_files:
      -   encoding: b64
          content: CiMgVGhpcyBmaWxlIGNvbnRyb2xzIHRoZSBzdGF0ZSBvZiBTRUxpbnV4...
          owner: trove:trove
          path: /etc/trove/trove.conf

  the other one for generating mime messages if there is any `*.cloudinit`
  scripts.

  .. note::

     Noted that currently we're going to support **ONLY** two formats for
     `*.cloudinit` file, cloud-config and user-data script [4]_. It may be
     difficult for us to organize one user-data scripts based on one
     mime multi-part file or gzip compressed content, and other formats
     may not be used a lot. As for formats reference, please see [5]_ .

* Use `--user-data` to pass the parameter we build above while booting an
  instance, then we can inject files into instance's specified location,
  with proper owner and permission. One thing to clarify here is that
  according to configuration item:

  .. code-block:: python

     cfg.BoolOpt('use_nova_server_config_drive', default=True,
                 help='Use config drive for file injection when booting '
                 'instance.'),

  we enable `--config-drive` when calling novaclient to create
  a server by default.

* Remove unused and deprecated codes.


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

Primary assignee:
  Fan Zhang <zh.f@outlook.com>

Milestones
----------

Target Milestone for completion:
  Rocky-R2


Work Items
----------

* Add new `InjectedFile` object.

* Add new helper functions.

* Modify current code, including deprecating files parameter and changing
  to user-data.

* Modify related code which uses `--personality` parameter to boot an instance.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

* Current functional tests should cover the creating instance scenario.

* Would need some new unit tests.


Documentation Impact
====================

Docs needed for new configuration item usage.

References
==========

.. [1] https://specs.openstack.org/openstack/nova-specs/specs/queens/implemented/deprecate-file-injection.html
.. [2] http://cloudinit.readthedocs.io/en/latest/topics/format.html#cloud-config-data
.. [3] http://cloudinit.readthedocs.io/en/latest/topics/format.html#mime-multi-part-archive
.. [4] http://cloudinit.readthedocs.io/en/latest/topics/format.html#user-data-script
.. [5] http://cloudinit.readthedocs.io/en/latest/topics/format.html#formats

Appendix
========

None.
