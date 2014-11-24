..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode
..

============================================
Move the Trove Guest Agent to its own module
============================================

https://blueprints.launchpad.net/trove/+spec/moving-trove-guestagent

Currently the guestagent code is part of the trove package. This
blueprint's goal is to refactor the guestagent and common functions into
new top level packages, so that the guestagent can be deployed onto
instances independently.

Note: Splitting the guestagent into its own repo was a requirement in
the original specification. However, it was determined at the Kilo Mid
Cycle that doing so would introduce dependencies between trove
components that is difficult to maintain.

For example, commits for AMQP / API message changes between trove core
and guestagent would need to be manually coordinated if trove and the
guestagent were in separate repos.

Since the overhead of such coordination outweighs the benefit of
splitting the guestagent into its own repo, we'll proceed with the
splitting at the directory level, but defer the repo splitting until
further discussions.


Problem description
===================

This blueprint will bring upon the following improvements:

* Simplify installation of the guestagent on instances.
* Reduce the amount of code that is deployed on instances.
* Lower the memory footprint of the guestagent by not importing
  unnecessary code from Trove core.


Proposed change
===============

Configuration
-------------

* A new top level oslo.cfg for the troveguest will be added. (This
  should be a small subset of the values in trove.common.cfg)
* The values in trove.common.cfg that are specifically for the guest
  will be removed.
* It is possible that some configuration values will need to be added.

Database
--------

None

Public API
----------

None

Internal API
------------

None

Guest Agent
-----------

1) The guestagent code will be moved to a top level module in the
existing trove repository called 'troveguest'.

2) The import statements will be changed from 'trove.guestagent' to
'troveguest'

3) Imports for common functions will be updated. See the "Common Code"
section below for details.

4) The code that currently rsyncs the code over to instances in
development will be changed to just include the 'troveguest' and common
function modules. (It is possible that another delivery method will be
used, however that should probably be done in its own blueprint)


Common Code
-----------
The guestagent currently uses a large amount of common code in
trove.common (/opt/stack/trove/trove/common) and trove.openstack.common
(/opt/stack/trove/trove/openstack/common).

Code under the "trove.common" module will be moved up to a "common"
module:

/opt/stack/trove/trove/common
-> /opt/stack/trove/common

All import statements will be changed from 'trove.common'to 'common'

Code under the "trove.openstack.common" module will be moved up to a
"common.openstack" module:

/opt/stack/trove/trove/openstack/common
-> /opt/stack/trove/common/openstack

All import statements will be changed from 'trove.openstack.common'to
'common.openstack'

Splitting the common modules out of trove allows the guestagent and the
common module to be deployed onto an instance independently. We'll no
longer need to deploy the whole trove code tree onto the guest instance
just because the guestagent needs to use some common functions.

Alternatives
------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:

* Robert Myers (robertmyers)
* Simon Chang (schang)

Milestones
----------

Target Milestone for completion:
  Kilo

Work Items
----------

Stage 1
^^^^^^^
https://review.openstack.org/#/c/119425/

Add a new package to the [files] section of setup.cfg::

    [files]
    packages =
        trove
        troveguest

Move the trove/guestagent module up one level, and name it "troveguest".
All references of "trove.guestagent" will be changed to "troveguest".

The new module layout will look like the following::

    trove/
        ...
        doc/
        etc/
        tools/
        trove/
        troveguest/   < --- new module
        setup.py
        setup.cfg
        ...

Stage 2
^^^^^^^
Move the "trove.common" module up one level to "common", and the
"trove.openstack.common" into "common.openstack". See the "Common Code"
section for detail. Rename imports.

The new module layout will look like the following::

    trove/
        ...
        common/   < --- moved from /opt/stack/trove/trove/common
        common/openstack   < --- /opt/stack/trove/trove/openstack/common
        doc/
        etc/
        tools/
        trove/
        troveguest/
        setup.py
        setup.cfg
        ...

Dependencies
============

None


Testing
=======

The guestagent tests need to be split out from the trove.tests modules,
then we need to make sure the tests are discovered properly.

Possibly modify tox.ini::

    [testenv:cover]
    basepython = python2.7
    commands =
        {envpython} run_tests.py --group=does_not_exist
        coverage erase
        python setup.py testr --coverage
        coverage run -a run_tests.py
        coverage run -a troveguest/run_tests.py
        coverage html
        coverage report


Documentation Impact
====================

Any docs or config file content that reference the old trove.guestagent
and common module paths will need to be updated. For example:

* The trove-guestagent section of this wiki:
  https://wiki.openstack.org/wiki/Trove
* This sample config file:
  <trove_dir>/etc/trove/trove-guestagent.conf.sample


References
==========

Kilo mid cycle discussion notes:
https://etherpad.openstack.org/p/trove-kilo-sprint-blueprints-bugs
