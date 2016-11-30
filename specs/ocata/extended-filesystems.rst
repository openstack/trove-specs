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


=================================
Trove Extended Filesystem Support
=================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Trove currently only supports a single volume on a guest instance, and
that volume must be a block device.  This spec outlines a proposal for
supporting multiple volumes, both block devices and filesystems, on
the guest.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/extended-filesystems


Problem Description
===================

In the current implementation, during instance creation the
taskmanager allocates a single cinder volume and informs the guest
during the prepare phase.  The guest then formats the volume and
mounts it as a volume to hold the data for the database.

Additional functionality is required:

- Some datastores require more than a single volume
- Guests should support both block devices and preformatted filesystems


Proposed Change
===============

To support this new functionality, the taskmanager will pass to the
guest a collection of volumes, each tagged as to their type and
intended use.  The taskmanager will be responsible for configuring the
types of volumes to be attached to a guest and how those volumes will
be provisioned with Cinder or Nova; the guest will be responsible
for preparing the block device, if required, and connecting the device
to the filesystem on the guest operating system.


Configuration
-------------

Three configuration values will be used to assist in attaching volumes
to instances.

cg_volumes
//////////

The global *cg_volumes* configuration setting in the DEFAULT section
of the taskmanager.conf file will contain a list of volume_types which
support consistency groups.  In future feature development, only
volume types which support consistency groups will be available for
snapshots and backups.

.. code-block:: bash

    cg_volumes = NETAPP,SCALEIO

For Openstack allocated volumes, the values of the *cg_volumes*
setting should correspond to the *provider_type* parameters in the
sections that follow.

guest_device_type
/////////////////

The global *guest_device_type* configuration setting describes how the
guest instance should deal with devices provided to it by the taskmanager.

.. code-block:: python

    cfg.DictOpt('guest_device_type',
                help="Dictionary of device types with help",
        default={
            'block_ext4': "Block storage to be formatted and managed by guest",
            'shared': "Shared storage, typically NFS, to be mounted as is"
        }
    )

available_volume_kind
/////////////////////

The per-datastore *available_volume_kind* configuration setting configures
the volume_kinds available to a specific datastore:

.. code-block:: python

    cfg.DictOpt('available_volume_kind',
                help="Dictionary of available volume types with help",
        default={
            'data': "Storage volume for the database",
            'binlog': "Volume to hold binary logs for the database",
            'user_log': "Volume to hold user and error logs"
        }
    )

In the initial implementation, this setting will be used to prevent
spinning up a collection of instances in a cluster, only to find that
an inappropriate volume configuration was selected.

/etc/trove/guest.conf
/////////////////////

A new olso config file will be introduced on the guest.  This file is
to be installed on the guest image by the DIB elements and will
contain configuration options specific to the operating system and
database software installed on the guest.

The *device_type* configuration setting describes how the guest
instance should prepare a volume before mounting, plus any other
device specific configuration.

The *volume_mapping* configuration setting configures for each
operating system how the guest should handle the volumes provided to
it.  The most common setting here would be where in the filesystem the
device should be mounted.  The *mount_priority* option, if supplied,
is used to configure mount order in the event that devices need to be
mounted beneath each other.

This description outlines the set of options defined specifically for
extended filesystem support:

.. code-block:: python

    from oslo_config import cfg

    device_type = [
        cfg.DictOpt('block_ext4', help="Block device to be formatted by guest",
            default={
                'raw_block_device': True,
                'format_options': 'ext4',
                'mount_type': 'ext4',
                'mount_options': '-o rw'
            },
        ),
        cfg.DictOpt('shared', help="Shared filesystem (NFS) to be used as is",
            default={
                'raw_block_device': False
                'mount_type': 'nfs',
                'mount_options': '-o rw'
            },
        )
    ]

    volume_mapping = [
        cfg.DictOpt('data', help="Storage volume for the database",
            default={
                'mount_point': '/var/lib/mysql',
                'mount_priority': 1
            },
        ),
        cfg.DictOpt('binlog',
                    help="Volume to hold binary logs for the database",
            default={
                'mount_point': '/var/lib/mysql/binlog',
                'mount_priority': 2
            },
        ),
        cfg.DictOpt('user_log', help="Volume to hold user and error logs",
            default={
                'mount_point': '/var/lib/mysql/userlog'
                'mount_priority': 2
            }
        )
    ]

Database
--------

A new table *volume_config* will be created to describe the volumes to
be configured.  Each volume configuration will detail each volume to
be attached to an instance.  The *volume_config* table will have the
following columns:

=================   ======================================================
Column Name         Description
=================   ======================================================
id                  uuid identifier
name                Name of volume configuration
volume_kind         intended use - defined by datastore (data, binlog, userlog)
size                size of volume (unless overridden by user)
provider            Openstack component providing volume ("cinder", "nova")
provider_type       Volume type passed to Cinder/Nova
device_type         Indicates to guest how to prepare volume
=================   ======================================================

For example, an instance which requires its data to be stored on a
block device and its logs to be stored on a different volume would be
configured as follows:

=======  =======  ===========  ====  ========  =============  ===========
id       name     volume_kind  size  provider  provider_type  device_type
=======  =======  ===========  ====  ========  =============  ===========
<uuid0>  vc1      root         3     cinder    vtype1         root
<uuid1>  vc1      data         10    cinder    vtype1         block_ext4
<uuid2>  vc1      binlog       2     cinder    vtype1         block_ext4
=======  =======  ===========  ====  ========  =============  ===========

Instances which do not specify a volume_config to use in allocating
the instance will use the volume_config named "default".  If no such
volume_config exists, the instance will default to the current single
Cinder volume.

Each volume defined in the volume_config will have a size specified
for it.  This size can be overridden by the user, either by the
"--sysvol:<volume_kind>,size=<n>" option, or by the "--size" option
for the data volume.  This eliminates the current requirement that the
"--size" option be specified for "trove create" or "trove
cluster-create"; note that this means that should the user specify
neither volume_config nor size when no "default" volume config is
defined, the create call will fail in the taskmanager rather than the
current behaviour of catching the discrepancy in the shell.

Two volume providers will initially be supported.  If the "cinder"
provider is selected, the volume will be allocated through the Cinder
API.  If the "nova" provider is specified, root volumes will be
alloced on a root disk on the compute host and volumes with a
volume_kind other than "root" will be allocated on Ephemeral storage.
An error will be raised by Nova should the allocated volume sizes
exceed the amount of storage configured in the instance flavor
selected.  Future volume provide support may include support for
Manila volumes and/or multi-attach Cinder volumes.

A new table *instance_volumes* will be added to track the volumes
associated with an instance.  This will include both volumes created
by the taskmanager based on the datastore volume configuration and
volumes specified by the user.

=================   ======================================================
Column Name         Description
=================   ======================================================
instance_id         Id of instance to which volumes are associated
volume_kind         intended use - defined by datastore (data, binlog, userlog)
volume_id           Id of volume in Cinder or Manila (Null for ephemeral)
provider            Component providing volume ("cinder", "nova", "manila")
device_type         Indicates to guest how to prepare volume
=================   ======================================================

An instance configured as above would be represented by the following
entries in the *instance_volumes* table:

=========  ===========  ===========  ========  ===========
volume_id  instance_id  volume_kind  provider  device_type
=========  ===========  ===========  ========  ===========
<volid0>   <inst1>      root         cinder    root
<volid1>   <inst1>      data         cinder    block_ext4
<volid2>   <inst1>      binlog       cinder    block_ext4
=========  ===========  ===========  ========  ===========

For backward compatibility, instances which have no entries in the
*instance_volumes* table will be assumed to have their root volume
allocated on Nova local storage.


Public API
----------

*volume_config* and *volume_list* parameters will be added to the
 payload of the following REST APIs:

- create
- cluster create
- cluster grow

The *volume_config* parameter, if specified, will select the volume
configuration to select from the volume_config table.  If not
specified, a root volume on Nova storage and a single Cinder data
volume will be configured.

The *volume_list* will encapsulate the information from the *--sysvol*
options.  For each of these options, for backward compatibility, if
the *volume_list* parameter is not included in the API payload, it
will be computed from the *volume* parameter.  It will be an error if
both *volume* and *volume_list* (or neither) are specified.

The *resize_volume* API will be updated to include the volume_kind of
the volume to be resized.  For backwards compatibility, if no
volume_kind is specified, the "data" volume will be resized.  An error
will be returned if the provider does not support the resize operation
on the specified volume.

There will additionally be a new "GET volume_configs" API which will
return a list of available volume configurations.  These volume
configurations will be the valid values to be specified for the above
*volume_config* parameter.

Request::

    GET v1/{tenant_id}/volume_configs
    {
    }

Response::

    {
        [
            "default",
            "ora_prod"
        ]
    }

Plus a new "GET volume_configs/<config>" API which will return details
about a given volume_config.

Request::

    GET v1/{tenant_id}/volume_configs/<config>
    {
    }

Response::

    {
        "instance_id": <uuid>,
        "volume_kind": 'data',
        "volume_id": <uuid>,
        "provider": "cinder",
        "device_type": "block_ext4"
    }

Plus a new "GET instance/<instance_id>/volumes" API which will return
details about the volumes attached to a given instance.

Request::

    GET v1/{tenant_id}/instance/<instance_uuid>/volumes
    {
    }

Response::

    {
        [
            {
                'volume_id': <volid0>,
                'size': 8,
                'volume_kind': 'root',
                'provider': 'cinder',
                'device_type': 'root'
            },
            {
                'volume_id': <volid1>,
                'size': 50,
                'volume_kind': 'data',
                'provider': 'cinder',
                'device_type': 'block_ext4'
            },
            {
                'volume_id': <volid2>,
                'size': 2,
                'volume_kind': 'binlog',
                'provider': 'cinder',
                'device_type': 'block_ext4'
            }
        ]
    }

Public API Security
-------------------

No impact.

Python API
----------

*volume_config* and *volume_list* parameters will be added to the
 following python APIs:

- Instance.create
- Cluster.create
- Cluster.grow

See above for descriptions of the *volume_config* and *volume_list*
parameters.

The *volume* parameter will be deprecated in the above APIs.

The Instance.resize_volume python API will be updated to include the
volume_kind of the volume to be resized.

A new *volume_configs* object will be added to the Trove python API.
This client API will implement "list" and "show" methods.

CLI (python-troveclient)
------------------------

Three new sub-commands will be added to the trove-manage command to
support associating volumes with datastore versions:

.. code-block:: bash

    $ trove-manage volume-config-add <name> <volume_kind> \
                <provider> <provider_type> <device_type> <required>

    $ trove-manage volume-config-delete <name> <volume_kind>

    $ trove-manage volume-config-list <name>

For example, to configure a volume configuration "ora_prod" to have a data
volume and an optional binlog volume, both Cinder block devices, the
following commands would be executed:

.. code-block:: bash

    $ trove-manage volume-config-add ora_prod \
                data cinder ram_backed block_ext4 True
    $ trove-manage volume-config-volume-add ora_prod \
                binlog cinder ram_backed block_ext4 False

A new *--sysvol* option will be added to several trove CLI commands to
support the configuration of volumes created by the taskmanager.  The
*--sysvol* option may be specified multiple times to configure
multiple volumes.  Each specification will include the *volume_kind*
for which a specification is being made followed by a colon separated
list of configuration options - for the initial implementation, only
size will be supported.

.. code-block:: bash

    $ trove create mydb myflavor --datastore=foo --datastore_version=1.0 \
                --volume_config=ora_prod \
                --sysvol=data:size=5 --sysvol=binlog:size=2

For backwards compatibility, an alternative to this command would be
one which specifies the size of the data volume with the "--size"
option, though this may be deprecated in future releases:

    $ trove create mydb myflavor --datastore=foo --datastore_version=1.0 \
                --volume_config=ora_prod --size=5 --sysvol=binlog:size=2

A new option will be added to the resize-volume command to support
specifying which of the volumes attached to the instance are to be
resized:

.. code-block:: bash

    $ trove resize-volume my_inst 3 --volume_kind binlog

For backwards compatibility, if the --volume_kind option is not
specified, the volume of type "data" will be resized.

A new "trove volume-config-list" CLI command will be added to return a
list of the names of the available volume_configs.


.. code-block:: bash

    $ trove volume-config-list
    +==============+
    | VolumeConfig |
    +==============+
    | default      |
    | ora_prod     |
    +==============+

And a corresponding new "trove volume-config-show".

.. code-block:: bash

    $ trove volume-config-show ora_prod
    ===========  ====  ========  =============  ===========
    volume_kind  size  provider  provider_type  device_type
    ===========  ====  ========  =============  ===========
    root         3     cinder    vtype1         root
    data         10    cinder    vtype1         block_ext4
    binlog       2     cinder    vtype1         block_ext4
    ===========  ====  ========  =============  ===========

And of course a command to show which volumes are attached to a
specific instance.

    $ trove volumes-list <instance>
    ===========  ===========  ========  ===========  =========
    volume_kind  size         provider  device_type  volume_id
    ===========  ===========  ========  ===========  =========
    root         8            cinder    root         <volid0>
    data         50           cinder    block_ext4   <volid1>
    binlog       2            cinder    block_ext4   <volid2>
    ===========  ===========  ========  ===========  =========


Internal API
------------

The *create_instance* API will be updated to include the *volume_info*
parameter.

The *resize_volume* API will be updated to include the id and
volume_kind of the volume to be resized.


Guest Agent
-----------

A new prepare call will be implemented which replaces the device_path
and mount_point parameters with a new *device_config* list.  The
*device_config* will supply information about the number and types of
volumes to be configured on the guest:

.. code-block:: json

    [
        {
            'volume_kind': 'data',
            'device_type': 'block_ext4',
            'device_path': '/dev/vdb1'
        },
        {
            'volume_kind': 'binlog',
            'device_type': 'block_ext4',
            'device_path': '/dev/vdb2'
        },
    ]

To support backwards compatibility when the guest is upgraded before
the guestagent API, the guest agent's prepare method will take both
old and new parameters.  The correct behaviour will be deduced based
on the values of the paramaters.

It is up to each datastore to define what volumes are supported, the
meaning of each value of the volume_kind, and where each volume
will be mounted on the local filesystem.

The guestagent resize_fs API will be updated to include the
*volume_kind* parameter.  The *mount_point* parameter will be ignored
when the *volume_kind* parameter is specified.

As the parameter to the *post_upgrade* RPC endpoint is a dict, it will
be updated to remain compatible with both old and new guests,
providing both the mount point of the data volume plus the full
*device_config* context.


Alternatives
------------

Not available.


Dashboard Impact (UX)
=====================

The dashboard would be changed to allow the user to specify the
volume_config on the instance.create, cluster.create, and cluster.grow
functions.  A volume.configs.list method will be added to the Python
API to facilite this functionality.

A new panel/action will be added to the instance panel to show the
volumes configured for a particular instance.

The volume_resize functionality will be updated to allow the user to
specify the volume_kind that they wish to resize.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  6-morgan

Dashboard assignee:
  <launchpad-id or None>

Milestones
----------

Target Milestone for completion:
  post ocata

Work Items
----------

- implement taskmanager changes
- implement base guestagent and guestagent.api changes
- adapt  datastores to new APIs
- develop unit tests


Upgrade Implications
====================

Backward compatibility for this feature will be dependent on the new
RPC versioning feature.


Dependencies
============

na


Testing
=======

An int-test should be developed to test adding multiple volumes for at
least one datastore.


Documentation Impact
====================

This feature will affect the following documents:

- Installation
- API
- CLI
- Building Guest Images for Openstack Trove


References
==========

na

Appendix
========

Any additional technical information and data.
