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


==================================
Percona XtraDB Cluster Root Enable
==================================

.. contents::

For the Percona XtraDB Cluster (PXC) datastore we need the ability to enable
root for a cluster to be able to manage the datastore with a privileged user.
For example, in order to integrate a PXC datastore cluster with Cloud Foundry
it requires a root user to automatically manage the database users and
databases on the cluster. This will add root enable to the PXC solution
we currently have.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/pxc-root-enable


Problem Description
===================

PXC is lacking support for root enable cluster. This will allow a user to
create a root user and either give a new random password or set the given
password for the root user across the cluster.

Proposed Change
===============

PXC will use the existing root enable API call. This change will allow the
cluster to enable root within a cluster. The call will apply the root
user and password to a single node in the cluster and since the cluster
replicates to the other nodes they will get the same root user and password
set.

Requirements for root enable:

- A root enable api to a cluster resource shall apply the root credentials
  to the cluster.
- A user shall be able to connect to any instance in the cluster with the root
  user and password to manage the datastore.

PXC will need to extend the existing root enable calls into its clustered
datastore implementation because currently the root enable calls raise an
exception if root enable is called with a cluster since most datastores do not
support this feature. This will require a configuration change for the
guestagent and will be outlined below.

This change only involves adding the existing feature to the PXC datastore not
changing the existing functionality of other datastores. This will not add root
enabled at cluster create time because that functionality does not currently
exist in the api for cluster create.

Configuration
-------------

In order to allow a PXC cluster to enable root we need to update the
guestagent api to support this call. After looking over the other cluster
enabled datastores the only other cluster datastore that supports this feature
is Vertica. Much of this code can easily be reused and applied to PXC as well.
We will pull the majority of this code into a common location that can be used
by other datastores in the future as well as the PXC datastore today. The
Vertica datastore can extend this class with the additional changes it needs
specific to its datastore.

The PXC configuration change will be with the ``root_controller`` configuration
parameter where it uses the DefaultRootController today and instead point to
the new class called ``ClusterRootController``.


Database
--------

None


Public API
----------

The following public API calls will be made available to the PXC datastore.

* Cluster root enable - The existing call payload will not be changed.
  Implementing the root enable of a cluster resource will allow a user to
  enable root across all instances in the cluster, as well as allow the user
  to specify a password that will be used to enable root on the cluster.

Public API Security
-------------------

None


Python API
----------

None


CLI (python-troveclient)
------------------------

Support for the following existing CLI calls.

* ``root-enable`` with or without the --root_password given by user

No changes should be necessary to accomplish these actions.


Internal API
------------

The Vertica datastore already has this feature and much of the code is reusable
so we can move this code to a common location and build off of it.

* Move the ``trove.extensions.vertica.models.VerticaRoot`` class to
  ``trove.extensions.common.models.ClusterRoot``
* Move the ``trove.extensions.vertica.service.VericaRootController`` class to
  ``trove.extensions.common.service.ClusterRootController``
* Make the ``trove.extensions.vertica.service.VericaRootController`` class
  extend the ``trove.extensions.common.service.ClusterRootController`` with
  small change Vertica needs.


Guest Agent
-----------

The PXC guest agent will need the methods to enable root as well with or
without a password. Since this feature didn't exist prior to now we only need
the ``enable_root_with_password`` and not the ``enable_root`` method in the
manager for PXC. The ``enable_root_with_password`` method is the new version of
the root enable call. The old version that did not have a password was left for
backward compatibility.

* Add the enable_root_with_password method to the pxc manager.

No calls will be deprecated in order to complete this.

Alternatives
------------

Not to support root enable of a PXC cluster.


Dashboard Impact (UX)
=====================

The dashboard will need an update for this to be enabled for a PXC cluster.
This change will need to apply for only a cluster of datastore type pxc as
other datastores do not have this ability.

Need a new option on a cluster dropdown to allow a user to enable root for a
given cluster. Greyed out if the cluster is not of datastore type pxc.

There should be a dialog that allows the user to enter a password that they
would like to use for the root user or allow the system to randomly gererate a
password and display the password to them once so that they can copy and paste
it to what ever application needs root access.


Implementation
==============

Assignee(s)
-----------

+---------------+--------------+---------+--------------------+
+ Name          + Launchpad Id + IRC     + Email              +
+===============+==============+=========+====================+
+ Craig Vyvial  + cp16net      + cp16net + cp16net@gmail.com  +
+---------------+--------------+---------+--------------------+


Milestones
----------

Targeting this for milestone:
Mitaka-3


Work Items
----------

- Enable root for a PXC cluster
- UX changes needed for root enable of a PXC cluster.


Upgrade Implications
====================

Just the common updates since this is a new feature the guestagent will need to
be updated.


Dependencies
============

None

Testing
=======

There will be unit tests that test the new calls for the strategy.

There will be integration tests added to the scenario tests that will test
enabling root on a cluster.


Documentation Impact
====================

We need to update the docs to show support for root enable on PXC clusters.


References
==========

None


Appendix
========

None
