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


=================
Title of the Spec
=================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Introduction paragraph -- what is the motivation for the spec/blueprint?

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/name-of-blueprint


Problem Description
===================

A detailed description of the problem.


Proposed Change
===============

Here is where you cover the change you propose to make in detail. How do you
propose to solve this problem?

If this is one part of a larger effort make it clear where this piece ends. In
other words, what's the scope of this effort?

If your specification proposes any changes to the Trove REST API such
as changing parameters which can be returned or accepted, or even
the semantics of what happens when a client calls into the API, then
you should add the APIImpact flag to the commit message. Specifications with
the APIImpact flag can be found with the following query:

https://review.openstack.org/#/q/status:open+project:openstack/trove-specs+message:apiimpact,n,z


Configuration
-------------

Does this impact any configuration files? If so, which ones?

Database
--------

Does this impact any existing tables? If so, which ones?
Are the changes forward and backward compatible?
Be sure to include the expected migration process

Public API
----------

Does this change any API that an end-user has access to?
Are there any exceptions in terms of consistency with other APIs?

Public API Security
-------------------

If this change proposes a new API, or if this change relates to
security on an existing API, provide details here.

What are the expectations of, and implications to security on the
Public API.

Python API
----------

Does this change the Python API? If anything was removed, has it
been properly marked as deprecated?

CLI (python-troveclient)
------------------------

Will the Trove CLI need to be modified?  If the CLI will just implement
the changes mentioned in the Python API section, it may be enough to
just mention it here.

Internal API
------------

Does this change any internal messages between API and Task Manager or Task
Manager to Guest?

Guest Agent
-----------

Does this change behavior on the Guest Agent? If so, is it backwards compatible
with API and Task Manager?

Alternatives
------------

This is an optional section, where it does apply we'd just like a demonstration
that some thought has been put into why the proposed approach is the best one.


Implementation
==============

Assignee(s)
-----------

Who is leading the writing of the code? Or is this a spec where you're throwing
it out there to see who picks it up?

If more than one person is working on the implementation, please designate the
primary author and contact.

Primary assignee:
  <launchpad-id or None>

Can list additional ids if they intend on doing substantial implementation work
on this spec.

Milestones
----------

Target Milestone for completion:
  eg. Liberty-1

Work Items
----------

Work items or tasks -- break the feature up into the things that need to be
done to implement it. Those parts might end up being done by different people,
but we're mostly trying to understand the timeline for implementation.


Upgrade Implications
====================

In this section, describe the upgrade implications (if any) of the
proposed change. This could include such details as:

* changes to location of files, or layout of the source tree if this
  impacts configuration files,

* invalidates old backups,

* changes the CLI in a manner that could impact existing scripting,

* eliminates or adds new notifications (events),

* any changes that an operator or user must perform as part of the
  upgrade.

If the change has upgrade implications, also remember to:

* add the DocImpact keyword to the commit, and

* provide sufficient information in the commit message or in the
  documentation bug that gets created.

For more information about the DocImpact keyword, refer to
https://wiki.openstack.org/wiki/Documentation/DocImpact


Dependencies
============

- Include specific references to specs and/or blueprints in Trove, or in other
  projects, that this one either depends on or is related to.

- Does this feature require any new library dependencies or code otherwise not
  included in OpenStack? Or does it depend on a specific version of library?


Testing
=======

Please discuss how the change will be tested. We especially want to know what
int tests and tempest tests will be added. It is assumed that unit
test coverage will be added so that doesn't need to be mentioned
explicitly, but discussion of why you think unit tests are sufficient
and we don't need to add more tempest tests would need to be included.


Documentation Impact
====================

What is the impact on the docs team of this change? Some changes might require
donating resources to the docs team to have the documentation updated. Don't
repeat details discussed above, but please reference them here.


References
==========

Please add any useful references here. You are not required to have any
references. Moreover, this specification should still make sense when your
references are unavailable. Examples of what you could include are:

* Links to mailing list or IRC discussions

* Links to notes from a summit session

* Links to relevant research, if appropriate

* Anything else you feel it is worthwhile to refer to
