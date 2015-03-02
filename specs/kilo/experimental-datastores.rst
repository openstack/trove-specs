..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

===========================================
Datastore maturity, experimental datastores
===========================================

https://blueprints.launchpad.net/trove/+spec/experimental-datastores

Hitherto, Trove has not made a clear distinction of which datastores are considered to be "experimental" and which are considered to be "suitable for general use". At the mid-cycle in Seattle (Kilo release) we discussed the possibility of introducing a clear definition of what an "experimental" datastore would be and how one could migrate a datastore from "experimental" to "suitable for general use".

Problem description
===================

When code for a datastore is submitted to Trove, there is no clear indication whether that datastore is in a state that would be sufficient for general use. For example, while a single instance datastore of MySQL is perfectly usable for some development and test use cases but a single instance datastore of (say) Cassandra is much less useful. A datastore that supports backup and restore is more useful than one that does not.

As a community we wish to be welcoming of changes but no all change sets are made equal. Some include extensive capabilities and test coverage while others are more basic. In an effort to make it clear what we, as a community, believe is the "readiness" of a datastore, we believe that a classification of datastores is a good improvement.

Proposed change
===============

Introduce a classification of datastores
----------------------------------------

It is proposed that we create three groups of datastores as described in detail below. This classification will mean that any datastore could be considered to be either (a) "experimental", (b) "technical preview", or (c) "stable".

In each release, beginning with the Kilo release, each datastore will be given a classification that will be one of the values listed above based strictly on its adherence to the requirements for each of those classifications.

The classifications will be inclusive; i.e. a datastore that meets the "technical preview" requirements must also meet all the requirements for "experimental", and a datastore taht meets the "stable" requirements must also meet all the requirements for "technical preview".

Introduce a classification of strategies
----------------------------------------

In a similar vein, we will also assign a classification to each strategy. Some strategies may be more throughly vetted and tested (for example) than others. While (purely for purposes of illustration) mysql_binlog may be considered "stable", one could have a different replication strategy that was considered "experimental".

Configuration
-------------

At the very least, this change will impact the trove-guestagent.conf file as it lists the datastore registry by providing the path to the implementation (manager.py)

Any similar location either in a configuraiton file (or for that matter, in the code) that calls out a location of an implementation will have to change.

Database
--------

This should have no database changes.

Public API
----------

This change has no impact on the Public API.

Public API Security
-------------------

Not applicable.

Internal API
------------

No changes to the internal API.

Guest Agent
-----------

It does not change the behavior of the guest agent, merely the location of the code.


Initial Classifications
-----------------------

As part of this change, it is proposed that the following assignments be made.

Stable: MySQL
Technical Preview: Cassandra and MongoDB
Experimental: All others

Requirements
------------

- Experimental

  A datastore will be considered for merging in the experimental stage if it includes the following items.

  * implementation of a basic subset of the trove API including create and delete

  * guest agent "elements" that will allow a user to create a guest agent

  * a definition of supported operating systems

  * basic unit tests that will verify the operation of the guest agent and test suite that is non-voting

  A strategy will be considered experimental if an implementation is provided and includes basic unit tests to verify operation of the strategy. A passing, and non-voting test suite should also be provided.

- Technical Preview

  A datastore will be considered for "Technical Preview" if it meets the requirements of "Experimental" and further

  * implements API's required to implement the capabilities of the datastore as defined in the datastore compatibility matrix that is at [https://wiki.openstack.org/wiki/Trove/DatastoreCompatibilityMatrix]

  Note that it is not required that the datastore implement all features (resize, backup, replication, clustering, ...) to meet this classification.

  It is also required that non-voting gate tests for all capabilities and a mechanism to build a guest image that will allow a user to exercise these capabilities is provided.

  A strategy will not (normally) be considered for Technical Preview classification.

- Stable

  A datastore will be considered "Stable" if it meets the requirements of "Technical Preview" and a stable voting test suite is part of the gate.

  A strategy will be considered "Stable" if it meets the requirements of "Experimental" and also has stable voting tests as part of the gate.

Details of Change
-----------------

The plan is to edit all files required to reflect the change in location of some datastores and strategies.

Alternatives
------------

The only other alternative is to have a webpage that lists this information without actually reorganizing the code.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
   amrith
   slicknik


Milestones
----------
   kilo-3

Work Items
----------

- Determine which datastores are in each of the proposed classifications.

- Determine which strategies are in each of the proposed classifications

- Implement the change to relocate code into the appropriate directory structure

- Implement changes in trove-integration to match this (redstack) if appropriate

Dependencies
============

- None


Testing
=======

Each datastore will have to be launched and verified for proper operation.

Documentation Impact
====================

This will have a documentation impact and a bug will be opened for this.


References
==========

* This was discussed at the mid-cycle. The etherpad is [https://etherpad.openstack.org/p/trove-kilo-sprint-state-of-ci]
