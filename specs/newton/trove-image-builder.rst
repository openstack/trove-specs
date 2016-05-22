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


===================
Trove Image Builder
===================

.. contents::

The development and user community needs a consistent and automated means of
generating Trove guest database images (simply "images") for different
platforms and databases using an open source tool.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove-image-builder/+spec/trove-image-build-repo


Problem Description
===================

Trove users (new and experienced) typically run into problems in the last leg
of a datastore setup, that is the generation and loading of a compatible image
including the database and the Trove guestagent. There are significant
variations among the GNU/Linux distros, their native database packages, vendor
packages and assumptions built into the current Trove codebase. These
differences can together conspire to provide unusable Trove guest database
instances. An instance launched from an incorrectly assembled Trove image will
not properly prepare and register with the Trove control plane, potentially
remaining in BUILD state indefinitely, and the novice user will have little
information to go on.


Proposed Change
===============

This specification proposes to create a new Trove repository that will contain
source code artifacts for an image generation tool. The new tool will support
image generation for the same set of distros currently available from
"redstack kick-start". However, a key difference here is that the new repo
will have a clear separation of concern from the trove-integration project:
no devstack nor test wrappers, just image building.

The artifacts will essentially be a BASH script main driver which potentially
loads distro-specific argument parsing, settings, and functions. The driver
script will ultimately invoke DIB (diskimage-builder) [0]_ with arguments to
apply DIB file elements to:

- install database packages
- install Trove guestagent code from one of several sources: Github tip of
  master or stable release, distribution packages if applicable, community
  packages such as RDO, or local file system.
- apply any required database configuration path changes
- systemd or init.d service enablement
- set SELinux labels or AppArmor profiles
- perform RHEL subscription registration and attachment
- optionally install SSH keys for debugging development and test images

Another parameterized option (e.g., command-line argument) should be whether
the script gets a base cloud image from the Internet, uses a cached version
(like redstack), or is simply pointed at an existing image on the local
filesystem.

Other artifacts in the repository could include:

- external repository files for loading packages
- systemd scripts or other init files
- cloud-init datasource specification

This change proposes to start with existing DIB elements derived from the
trove-integration project. These currently comprise Ubuntu and Fedora (F22 or
higher). Work is underway to convert the existing Fedora elements to CentOS 7.
Proposed supported datastores (specific versions omitted since these will
change over time):

==========  ======  ========
datastore   Ubuntu  CentOS 7
----------  ------  --------
Cassandra   Yes       Yes
Couchbase   Yes       Yes
CouchDB     Yes       TBD
DB2         Yes       TBD
MariaDB     Yes       Yes
MongoDB     Yes       Yes
MySQL       Yes       Yes
Percona     Yes       Yes
PostgreSQL  Yes       Yes
PXC         Yes       Yes
Redis       Yes       TBD
Vertica     Yes       TBD
==========  ======  ========

NB: Datastores marked TBD for CentOS 7 currently lack public community yum
repos for install.

The image build process should be independent of any specific OpenStack python
or other dependencies save for the DIB tool. Ideally, this new repo would not
be branched with OpenStack releases, just the same as trove-integration is not
branched today. However, trove-integration does rely on per-release
requirements files for pip. These are essentially trimmed down requirements to
service a pip install of the guestagent code. Some possible solutions:

- fetch the existing trove-integration requirement files when doing a pip
  install in the new builder
- going forward, have trove incorporate those files formally instead of
  maintaining them externally (under a separate blueprint)

Although this project could eventually be integrated with the redstack script
for use in development and testing, it should have no dependency on it nor
the trove or python-troveclient projects for execution, notwithstanding
inclusion of the existing guest requirement files.

Although this proposal will be initially organized around the incumbent DIB
tool, it will not preclude additions and enhancements to support other image
build technologies as recognized by the OpenStack community. [1]_ For example,
a libguestfs [2]_ approach could be integrated into this same repository if
the community reviews and deems that technology to be advantageous at some
point in the future.


Configuration
-------------

None, this tool doesn't make use of the configuration options used by the Trove
controller. In other words, it will not parse or otherwise attempt to make use
of Trove controller configuration settings for its image generation execution.

Database
--------

None, images created from this tool will be loaded into Glance and registered
as a Trove datastore the same as today.

Public API
----------

None, image generation is not part of the Trove API.

Public API Security
-------------------

None, see above

Python API
----------

None, image generation is not part of the Python API.

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
- Use other image image build and manipulation tools as recognized by OpenStack
  governance [1]_, such as libguestfs. [2]_ However, there are concerns about
  the ability to successfully adopt these tools in areas such as gate checks
  where DIB is currently used.
- Rely on the limited image options provided by the trove-integration project
  via the redstack tool. However, these images are specifically generated for
  development testing and not appropriate for other environments.
- Manually follow the DIB-based procedure described in the existing
  "Building Guest Images" document [3]_.
- Use downstream providers which likely incurs a business relationship for
  access and use of their proprietary tested images.

Dashboard Impact (UX)
=====================

None

Implementation
==============

Assignee(s)
-----------

============================= ============== ======== ===================
Name                          Launchpad Id   IRC      Email
----------------------------- -------------- -------- -------------------
Victoria Martinez de la Cruz  vkmc           vkmc     vimartin@redhat.com
Peter MacKinnon               pmackinn       pmackinn pmackinn@redhat.com
============================= ============== ======== ===================


Milestones
----------

Newton-1


Work Items
----------

- Have PTL create new project repository for image creation tool and supporting
  data files.
- Develop and install artifacts into repository.
- Update existing docs to guide users to new image creation tool.


Upgrade Implications
====================

None

Dependencies
============

DIB (diskimage-builder) [0]_

Testing
=======

Autonomous testing of the image builder likely involves inventory of installed
packages, file paths, etc. This could be done using other image tools such
as guestfish, virt-ls, and virt-cat. [2]_ For integration testing, we could
investigate configurable changes in redstack where instead of generating an
image, redstack invokes the new tool. A new CI job (likely initially a
non-voting job) could run devstack with trove, run the image generation,
configure the generated image and the related datastore, and run integration
tests and/or tempest. When the job is deemed stable by the community, it
could be considered for voting.

Documentation Impact
====================

References to the new project should be added to the existing "Building Guest
Images" document [3]_.


References
==========

.. [0] https://github.com/openstack/diskimage-builder
.. [1] http://docs.openstack.org/image-guide/modify-images.html
.. [2] http://libguestfs.org/
.. [3] https://github.com/openstack/trove/blob/master/doc/source/dev/building_guest_images.rst


Appendix
========

None

