..
  This work is licensed under a Creative Commons Attribution 3.0
  Unported License.

  http://creativecommons.org/licenses/by/3.0/legalcode

=========================
Example Snippet Generator
=========================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/example-snippet-generator




Problem Description
===================

Trove has ssome really nice documentation featuring snippets showing the
what the JSON looks like for the standard REST calls and response. The only
issue is these docs are not validated, meaning if the API changes in ways big
or small its possible they will not match what a present day user of Trove
will see.


Proposed Change
===============

This blueprint proposes we fix this by automatically generating these examples
and validating them in Trove.

The fix will involve actually making calls against the real Trove code and
capturing the bodies of the requests and responses then writing them to the
text files used by the docs. We can do this quickly by utilizing the same "fake
mode" test doubles that are used by the tests already run in Tox. The beauty
is all of the API code that determines what the request and responses look like
will get run just the same as if the tests had executed against a fully stood
up Trove environment, with the advantage that certain UUIDs can be altered to
avoid them changing with every test run.

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

Internal API
------------

None

Guest Agent
-----------

None


Data Model Impact
-----------------
None.

REST API Impact
---------------
None, except that it will be tested even better than before.

Security Impact
---------------
None.

Notifications Impact
--------------------
None.

Other End User Impact
---------------------
None.

Performance Impact
------------------
The snippet generation will run in mere seconds as part of Tox. There will be
no noticable impact on the developers of Trove.

Other Deployer Impact
---------------------
None.

Developer Impact
----------------
The generation will run fast enough to be invisible to most developers. However
developers will be aware if they inadvertently change anything in the request
or response payload and will have to argue for the changes to the API, even
if they're merely additions.

Community Impact
----------------
The generation of snippets will usher in a new golden era of devs and doc
writers working together. Maybe sometimes devs will be doc writers, or doc
writers will be devs. It isn't a stretch to suggest it will be a utopia.

Alternatives
------------
We could continue the implied agreement that devs are always constantly reading
the docs and treating that as a contract, and that with each change they
rabidly run integration tests but also manually run tests and inspect the
output, making sure the snippets shown in the docs are accurate. Unfortunately
since many of the current snippets *are* inaccurate I don't think this will
work.

Implementation
==============

Assignee(s)
-----------
Primary assignee:
    Tim Simpson

Milestones
----------

Target Milestone for completion:
    Kilo-1

Work Items
----------
* Implement the snippets generator.

Dependencies
============
None.

Testing
=======
NA

Tempest Tests
-------------
NA

Functional Tests
----------------
NA

API Tests
---------
NA

Documentation Impact
====================
We will need to change the snippets at least initially as they have changed
so much since when they were originally authored.

User Documentation
------------------
None.

Developer Documentation
-----------------------
We will need to document how this works in the Tox file.

References
==========
