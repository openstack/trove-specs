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


========================================
Eliminate trove-integration and redstack
========================================

.. sectnum::
.. contents::

In the very beginning, when Trove was integrated into OpenStack, one
of the subjects of some contention was the redstack tool, and the fact
that Trove had a somewhat non-standard structure in the form of a
trove-integration repository.

It was, I understand, one of the stipulations of the Technical
Committee at the time that this be normalized.

For a number of reasons, (which we will describe in the Problem
Description section) this structure is proving to be quite a nusiance
and it would be beneficial to the project to do this now.

The goal of this project is to eliminate the trove-integration project
and the redstack tool through a normal process of deprecation. That is
to say that existing releases, through Newton, will continue to be
driven and may (I stress, may) use the tool, but new versions from
Ocata will not.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/eliminate-trove-integration-and-redstack


Problem Description
===================

The trove-integration project was created as a place to store scripts
to create, manipulate and test DBaaS vm's, and to house the scripts
used to manage the development environment. The redstack tool was the
swiss army knife, it could provision your development environment,
make guest images, load them, and later run tests as well.

On the whole, a very useful thing, there is no doubt about that.

It did introduce several serious problems.

1. trove-integration is not versioned

It has only a master branch. Therefore all code that is version
sensitive has to accomplish that through crafty branching constructs.

2. trove-integration is a repository outside the trove repository

This brings with it dependencies on the trove repository, such as when
a new datastore needs to be added, or a new version of a datastore is
to be added. Trove 'elements' go into trove-integration but get used
by trove.

3. The CI is very painful

Since trove-integration isn't branched, we have to test each
trove-integration branch against not just master, but also stable
branches.

4. The versioning just got more complex

We now have to deal with multiple operating systems (ubuntu and
fedora), multiple versions (liberty, mitaka, newton, ocata, ...),
different versions of operating systems (trusty, and now xenial). The
code is now convoluted enough that attempting to add support for
xenial (as I had to do for SQL Server) became a nightmare.

5. There is no easy way to build images

This is the #1 problem faced by users of Trove; how do I build
images. A solution was proposed
(https://review.openstack.org/#/c/312806/) that would address this
through the creation of a trove-image-builder repository. This
solution has some merits and demerits, we choose here to propose a
different solution (see second bullet in proposed end state) that will
address that problem as well.

6. redstack is 'non-standard'

The current mode/phase approach provided by devstack is standardized
across all projects, and redstack is one of the few (if not the only)
non-standard approach. We already support the devstack plugin and
redstack (in the provisioning a stack use-case) is nothing more than a
thin veneer on devstack.

Proposed Change
===============

The proposed change is in multiple parts, and several of the sections
don't match the typical headings one expects in a blueprint that is
aimed at a new feature or function in Trove. Therefore the sections
may be marked as Not Applicable. Additional sections have been added
where required.

One thing that is important to highlight is that while this change is
highly disruptive, and moves a whole lot of code around, we are
largely talking about moving around a couple of hundred files
(elements) from one place to another, and leveraging a devstack plugin
that we already use extensively. There will be an impact on the tests
that are in trove-integration but we already do most of our testing
out of the trove repository.

Changes that have been proposed in the trove-integration repository;
which are pending review and merge will be negatively impacted. But
that will be the case no matter when we choose to make a change like
this. Most of the elements are highly parameterized and the changes
actually required to make this all work are minimal.

I feel that the best way to describe this proposed change is to begin
with a description of the proposed 'end-state'.

Proposed End State
------------------

* The elements from trove-integration will get folded into the trove
  repository

* The elements will now be versioned along with the server, they are
  in the same repository. Tagging the Ocata release will also cause
  the release of a set of elements for the release and similarly the
  tagging of the Pike release will cause the release of a set of
  elements for that release.

  A set of tools will be provided that will make this easier, more
  description of that below.

* A set of sample configuration files will be provided that will cause
  devstack to install and configure Trove. A user can copy these into
  their own localrc, or use the commands to set the right environment
  variables before invoking devstack/stack.sh

* The trove devstack plugin will have additional code in the
  stack/extra step that will build and load a set of guest images of
  the users choosing. This image or images will be built using the
  elements from the trove repository.

  This will cause the standard demo user to be used (not alt_demo).

  In running devstack, one must configure a configuration file for
  devstack and one specifies the datastore whose image is to be built
  and loaded in that configuration file. I was initially contemplating
  allowing for the specification of a comma-seperated list but a
  single datastore may be a good place to start. This datastore would
  also be set as the default.

  One devstack environment can operate with multiple datastores. Three
  commands (trove-image-builder.bash, load-trove-image.bash and
  activate-trove-image.bash) will be provided. The first will build
  the image for you. The second will load it into glance and register
  it with Trove, the third will set a specified datastore/version to
  the the default.

* The trove devstack plugin will have additional code in the
  stack/post-config phase that will configure the Trove test
  environment, add the right flavors, and do the other things that are
  required for Trove testing.

* Scenario tests that are already in the trove repository will be run
  without the use of the redstack tool.

* Releases Newton and before may continue to use trove-integration and
  redstack, releases Ocata and forward shall not use trove-integration
  and redstack. For example, new elements for Ocata and the future
  will not go into trove-integration. This means that during this
  transition (which may last for two releases) some changes may have
  to go to both trove-integration, and trove.

* The Ocata CI will have a new set of jobs that will leverage this new
  state, no longer using redstack for its provisioning, and the cross
  version testing that is going on in trove-integration will no longer
  need to be supported.

Configuration
-------------

* Some sample configuration files will be provided and these will help
  a user configure their localrc before running stack.sh. This will
  cause devstack to completely provision Trove, and additionally build
  and load guest images as instructed by the user.

How we get there
----------------

Getting to the desired end state will be a multi-step exercise.

Step 1

Take everything in the trove-integration repository at some specific
point in time and drop it into the trove repository. For convenience,
I'm going to drop it into a folder called integration.

It would be nice to do this and preserve history but that is going to
be quite a pain to accomplish. An email has been sent to the infra
mailing list requesting help with this but in the intermin, the commit
https://review.openstack.org/#/c/384195/ does what we need (sans
histories).

Step 2

Make changes to the stuff now in the trove repository and make it such
that the redstack command (which will be renamed to trovestack) can be
executed just as it used to be in the trove-integration branch. This
also includes some small amendments to the documentation.

Commit https://review.openstack.org/#/c/384746/ does this.

Step 3

Refactor the CI jobs to use trovestack in the trove tree instead of
redstack from the trove-integration tree. This means all the CI jobs
(or maybe most) will become legacy jobs and new jobs will be created
for Ocata and higher.

Step 4

There is a huge amount of cruft in trovestack that handled the fact
that redstack in trove-integration was not versioned and released with
each OpenStack version. We should do this cleanup because sooner
rather than later as we will soon have to handle the Ubuntu 16.04
transition and having that dimension in addition to the OpenStack
version dimension will be very difficult to manage.

Step 5

Take the image build aspect of trovestack (formerly redstack) and make
it an independent tool. https://review.openstack.org/#/c/374952/ began
this process and took the elements out of the place where they were
copied in from trove-integration and starts to make it a standalone
tool. We will update trovestack to use this tool and avoid the
duplication of the image building logic.

Take the image loading logic (including the setting of the default
datastore) and make that a standalone tool and modify trovestack to
use that tool.

Step 6

Refactor the CI to automatically build images for different datastores
and verify that the image build process is proper. This will be a new job.

Step 7

Refactor the integration tests into the tests directory.


Database
--------

Not applicable

Public API
----------

Not applicable

Public API Security
-------------------

Not applicable

Python API
----------

Not applicable

CLI (python-troveclient)
------------------------

Not applicable

Internal API
------------

Not applicable

Guest Agent
-----------

The guest agent is already part of the trove repository and will
remain there. It will now be in the same versioned repository as the
server code which has dependencies on it.

Alternatives
------------

There are several options that have been considered, some at great
length.

1. Do nothing

Well, we've done that for three years and it hasn't been fun. I think
we can safely say that there are strong reasons to disqualify this
option.

2. Just get the image build out of redstack, leave the rest

This was part (at least) of the approach behind setting up the
trove-image-builder repository. It would be an improvement over the
present state but still would have cross repository
dependencies. Considering that there is no clear justification for
releasing trove-image-builder at a different cadence than trove, I see
no justification in having an independent repository.

We know that there is a tight coupling, and there likely will be one
for a long time longer, between the server side of Trove and the guest
agent/images. Having two repositories just makes handling that a pain.

3. Use the trove-image-builder approach that was proposed earlier.

We could use the approach that was proposed earlier
(https://review.openstack.org/#/c/312806/) but this solution has the
same kind(s) of challenges that one faces with trove-integration. Two
repositories, releasing them in sync, etc.,

Having elements in the trove repository is a better alternative.

Dashboard Impact (UX)
=====================

No dashboard impact is expected.

The dashboard will be enabled (if the user enables the plugin). Code
already exists for that in the trove plugin.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  amrith

Dashboard assignee:
  <none>

Milestones
----------

Target Milestone for completion:
  Ocata-1

Work Items
----------

* Move elements from trove-integration to trove
* Write wrapper (trove-image-builder) script for simplicity of use
* Create sample configuration file settings
* Modify CI jobs

Upgrade Implications
====================

This change has no upgrade implications as we are talking largely
about refactoring a development infrastructure.

Dependencies
============

None

Testing
=======

We will test the creation of each of the images, and putting them
through their paces in the CI with our existing scenario tests.

Documentation Impact
====================

Internal (developer) documentation will need to be updated.


References
==========

None

Appendix
========

None
