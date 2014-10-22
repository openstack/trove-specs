..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================
Guest RPC Ping Pong
===================

Blueprint:

https://blueprints.launchpad.net/trove/+spec/guest-rpc-ping-pong

The proposal is to introduce a new Management API route that facilitates a
lightweight ping/pong mechanism for determining whether RPC communication is
working as expected.

Problem Description
===================

Today, the only means of ascertaining whether direct or indirect RPC
connectivity between the control-plane and the guest is functioning, via an
API, is by using the 'show' operation in the Management API.

Although mgmt-show indirectly answers the question of "is the guest
reachable?", it is a relatively heavyweight call.  Beyond consulting the
filesystem for rudimentary information, mgmt-show sends 'show' requests to
Nova and Cinder.

Use Cases
----------

* As a deployer, I want to be able to determine whether RPC connectivity
  between the control-plane and a specific guest is broken.

Proposed change
===============

**Introduce**::

  GET HOST:8779/v1.0/<tenant_id>/mgmt/instances/<instance_id>/rpc_ping

**Behavior**

The request::

  GET HOST:8779/v1.0/<tenant_id>/mgmt/instances/<instance_id>/rpc_ping

will result in the following if it's successful::

  HTTP/1.1 204 No Content
  Content-Length: 0
  Content-Type: application/json
  Date: Thu, 02 Oct 2014 23:32:26 GMT

on the other hand, if trove-guest is shutdown, or the guest is generally
not responding, the following will be returned::

  HTTP/1.1 400 Bad Request
  Content-Length: 237
  Content-Type: application/json; charset=UTF-8
  Date: Thu, 02 Oct 2014 23:32:59 GMT

  {"badRequest": {"message": "An error occurred communicating
   with the guest: Timeout while waiting on RPC response -
   topic: \"guestagent.1e4099f1-7f8d-4564-bd83-0b9f66aa35b9\",
   RPC method: \"rpc_ping\" info: \"<unknown>\".", "code": 400}}

Configuration
-------------

No Configuration changes.

Database
--------

No Database changes.

Public API
----------

No public API changes.


Management API
--------------

Introduces::

  GET HOST:8779/v1.0/<tenant_id>/mgmt/instances/<instance_id>/rpc_ping

Internal API
------------

No internal API changes.

Guest Agent
-----------

No Guest Agent changes.


Alternatives
------------

The current alternative is mgmt-show, but it's too heavyweight of a call,
and can fail to return meaningful information if the underlying compute
and/or volume are unhealthy.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Auston McReynolds (amcrn)

Milestones
----------

Kilo-1

Work Items
----------

See https://review.openstack.org/#/c/125819/

Dependencies
============

No dependencies.


Testing
=======

Standard.


Documentation Impact
====================

If the Management API is documented (which I don't believe it is), then
the addition of the 'rpc_ping' route is relevant.


References
==========

None.
