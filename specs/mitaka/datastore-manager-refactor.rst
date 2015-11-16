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


==============================
Refactor the Datastore Manager
==============================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

There is a large amount of boiler-plate and/or copy-and-paste code in each
datastore manager.  As more managers are added, the time involved in
maintaining all this code will continue to grow. To alleviate this and the bugs
it promotes, a base manager class needs to be created where all common code can
reside.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/datastore-manager-refactor


Problem Description
===================

When bugs are discovered and fixed in the manager code of one datastore, these
changes are seldom transferred to all the other datastores.  This causes a
'drift' in the stability of each experimental datastore as currently there are
no third-party CI's.  In addition, when 'new improved' ways to solve a problem
are implemented they are done differently across each manager, if at all.  It
is also difficult to transfer features (and coding knowledge) from one
datastore to another, and the problem is exacerbated as code is
copied-and-pasted when a new datastore manager is implemented.

A current example of this problem is the issue where instances flip from BUILD
to ACTIVE and back again [1]_, or from BUILD->SHUTDOWN->ACTIVE. [2]_  Fixing
this means changing how prepare works, and currently this change would be
required to be made in each datastore manager.  Implementing this in a uniform
way would be almost impossible with the current architecture of the manager
code base.


Proposed Change
===============

A new 'Manager' class will be created that will be the base class for all
datastore managers.  In order to keep the scope reasonable, only the barest
minimum of functionality will be pulled back into the base class in the initial
implementation - this will include methods that are currently 'boiler-plate'
code (such as the response to the rpc_ping and get_fileststem_stats calls, and
the periodic task, update_status).

A mechanism for encapsulating functionality will also be needed in order for
the base manager to be able to execute datastore-specific instructions.  This
will be accomplished through the use of properties that can be overridden by
each descendant.  Some required ones (such as the 'status' object) will be
declared abstract and must be present; others (such as the new configuration
manager, and potentially a future dictionary of strategies) will be optional.

The new Manager class will reside in the datastore module:

.. code-block:: bash

    trove/guestagent/datastore/manager.py

This is alongside the existing service.py file (which contains the existing
BaseDbStatus class).  The directory structure of the MySQL derived classes will
also be tidied a bit and will end up looking like the following:

.. code-block:: bash

    trove
    +-- guestagent
        +-- datastore
            +-- __init__.py
            +-- manager.py          <-- new 'base' manager
            +-- service.py
            +-- experimental
             +-- __init__.py
             +-- cassandra
              +-- __init__.py
              +-- manager.py
              +-- service.py
              +-- system.py

            <other experimental datastore modules>

             +-- redis
              +-- __init__.py
              +-- manager.py
              +-- service.py
              +-- system.py
             +-- vertica
                 +-- __init__.py
                 +-- manager.py
                 +-- service.py
                 +-- system.py
            +-- mysql_common        <-- new module
             +-- __init__.py
             +-- manager.py      <-- renamed from mysql/manager_base.py
             +-- service.py      <-- renamed from mysql/service_base.py
            +-- mysql
             +-- __init__.py
             +-- manager.py
             +-- service.py
            +-- technical-preview
                +-- __init__.py


Within the context of this refactor (as a proof-of-concept), the issue with
having instances flip in-and-out of BUILD state will be addressed properly.
The prepare method will be moved into the base class, which will
seamlessly implement the code required to ensure that no notifications are
sent until it is guaranteed that prepare has finished successfully.  The
existing prepare methods will be renamed 'do_prepare' and will be called from
within the base prepare method.

This manner of determining whether prepare has finished will be accomplished by
having the manager write a file at the start and at the successful conclusion
of the prepare operation.  Any errors (exceptions) will be trapped and logged
and the instance set into the FAILED state.

A sample of what this will look like in the base manager is as follows,
although additional properties may be defined as they are deemed necessary (and
others can be added in future cleanup work):

.. code-block:: python

    class Manager(periodic_task.PeriodicTasks):
        """This is the base class for all datastore managers.  Over time, common
        functionality should be pulled back here from the existing managers.
        """

        def __init__(self, manager_name):

            super(Manager, self).__init__(CONF)

            # Manager properties
            self.__manager_name = manager_name
            self.__manager = None
            self.__prepare_error = False

        @property
        def manager_name(self):
            """This returns the passed-in name of the manager."""
            return self.__manager_name

        @property
        def manager(self):
            """This returns the name of the manager."""
            if not self.__manager:
                self.__manager = CONF.datastore_manager or self.__manager_name
            return self.__manager

        @property
        def prepare_error(self):
            return self.__prepare_error

        @prepare_error.setter
        def prepare_error(self, prepare_error):
            self.__prepare_error = prepare_error

        @property
        def configuration_manager(self):
            """If the datastore supports the new-style configuration manager,
            it should override this to return it.
            """
            return None

        @abc.abstractproperty
        def status(self):
            """This should return an instance of a status class that has been
            inherited from datastore.service.BaseDbStatus.  Each datastore
            must implement this property.
            """
            return None

        ################
        # Status related
        ################
        @periodic_task.periodic_task
        def update_status(self, context):
            """Update the status of the trove instance. It is decorated with
            perodic_task so it is called automatically.
            """
            LOG.debug("Update status called.")
            self.status.update()

        def rpc_ping(self, context):
            LOG.debug("Responding to RPC ping.")
            return True

        #################
        # Prepare related
        #################
        def prepare(self, context, packages, databases, memory_mb, users,
                    device_path=None, mount_point=None, backup_info=None,
                    config_contents=None, root_password=None, overrides=None,
                    cluster_config=None, snapshot=None):
            """Set up datastore on a Guest Instance."""
            LOG.info(_("Starting datastore prepare for '%s'.") % self.manager)
            self.status.begin_install()
            post_processing = True if cluster_config else False
            try:
                self.do_prepare(context, packages, databases, memory_mb,
                                users, device_path, mount_point, backup_info,
                                config_contents, root_password, overrides,
                                cluster_config, snapshot)
            except Exception as ex:
                self.prepare_error = True
                LOG.exception(_("An error occurred preparing datastore: %s") %
                              ex.message)
                raise
            finally:
                LOG.info(_("Ending datastore prepare for '%s'.") % self.manager)
                self.status.end_install(error_occurred=self.prepare_error,
                                        post_processing=post_processing)
            # At this point critical 'prepare' work is done and the instance
            # is now in the correct 'ACTIVE' 'INSTANCE_READY' or 'ERROR' state.
            # Of cource if an error has occurred, none of the code that follows
            # will run.
            LOG.info(_('Completed setup of datastore successfully.'))

            # We only create databases and users automatically for non-cluster
            # instances.
            if not cluster_config:
                try:
                    if databases:
                        LOG.debug('Calling add databases.')
                        self.create_database(context, databases)
                    if users:
                        LOG.debug('Calling add users.')
                        self.create_user(context, users)
                except Exception as ex:
                    LOG.exception(_("An error occurred creating databases/users: "
                                    "%s") % ex.message)
                    raise

            try:
                LOG.debug('Calling post_prepare.')
                self.post_prepare(context, packages, databases, memory_mb,
                                  users, device_path, mount_point, backup_info,
                                  config_contents, root_password, overrides,
                                  cluster_config, snapshot)
            except Exception as ex:
                LOG.exception(_("An error occurred in post prepare: %s") %
                              ex.message)
                raise

        @abc.abstractmethod
        def do_prepare(self, context, packages, databases, memory_mb, users,
                       device_path, mount_point, backup_info, config_contents,
                       root_password, overrides, cluster_config, snapshot):
            """This is called from prepare when the Trove instance first comes
            online.  'Prepare' is the first rpc message passed from the
            task manager.  do_prepare handles all the base configuration of
            the instance and is where the actual work is done.  Once this method
            completes, the datastore is considered either 'ready' for use (or
            for final connections to other datastores) or in an 'error' state,
            and the status is changed accordingly.  Each datastore must
            implement this method.
            """
            pass

        def post_prepare(self, context, packages, databases, memory_mb, users,
                         device_path, mount_point, backup_info, config_contents,
                         root_password, overrides, cluster_config, snapshot):
            """This is called after prepare has completed successfully.
            Processing done here should be limited to things that will not
            affect the actual 'running' status of the datastore (for example,
            creating databases and users, although these are now handled
            automatically).  Any exceptions are caught, logged and rethrown,
            however no status changes are made and the end-user will not be
            informed of the error.
            """
            LOG.debug('No post_prepare work has been defined.')
            pass

        #####################
        # File System related
        #####################
        def get_filesystem_stats(self, context, fs_path):
            """Gets the filesystem stats for the path given."""
            # TODO(peterstac) - note that fs_path is not used in this method.
            mount_point = CONF.get(self.manager).mount_point
            LOG.debug("Getting file system stats for '%s'" % mount_point)
            return dbaas.get_filesystem_volume_stats(mount_point)

        #################
        # Cluster related
        #################
        def cluster_complete(self, context):
            LOG.debug("Cluster creation complete, starting status checks.")
            self.status.end_install()


The base service class will be enhanced to contain the necessary methods to
set a flag denoting whether prepare has finished of not.  This will look
something like the following (only new code is shown):

.. code-block:: python

    class BaseDbStatus(object):

        GUESTAGENT_DIR = '~'
        PREPARE_START_FILENAME = '.guestagent.prepare.start'
        PREPARE_END_FILENAME = '.guestagent.prepare.end'

        def __init__(self):
            self._prepare_completed = None

        @property
        def prepare_completed(self):
            if self._prepare_completed is None:
                # Force the file check
                self.prepare_completed = None
            return self._prepare_completed

        @prepare_completed.setter
        def prepare_completed(self, value):
            # Set the value based on the existence of the file; 'value' is
            # ignored
            # This is required as the value of prepare_completed is cached,
            # so this must be referenced any time the existence of the
            # file changes
            self._prepare_completed = os.path.isfile(
                guestagent_utils.build_file_path(
                    self.GUESTAGENT_DIR, self.PREPARE_END_FILENAME))

        def begin_install(self):
            """Called right before DB is prepared."""
            prepare_start_file = guestagent_utils.build_file_path(
                self.GUESTAGENT_DIR, self.PREPARE_START_FILENAME)
            operating_system.write_file(prepare_start_file, '')
            self.prepare_completed = False

            self.set_status(instance.ServiceStatuses.BUILDING, True)

        def end_install(self, error_occurred=False, post_processing=False):
            """Called after prepare completes."""

            # Set the "we're done" flag if there's no error and
            # no post_processing is necessary
            if not (error_occurred or post_processing):
                prepare_end_file = guestagent_utils.build_file_path(
                    self.GUESTAGENT_DIR, self.PREPARE_END_FILENAME)
                operating_system.write_file(prepare_end_file, '')
                self.prepare_completed = True

            final_status = None
            if error_occurred:
                final_status = instance.ServiceStatuses.FAILED
            elif post_processing:
                final_status = instance.ServiceStatuses.INSTANCE_READY

            if final_status:
                LOG.info(_("Set final status to %s.") % final_status)
                self.set_status(final_status, force=True)
            else:
                self._end_install_or_restart(True)

        def end_restart(self):
            self.restart_mode = False
            LOG.info(_("Ending restart."))
            self._end_install_or_restart(False)

        def _end_install_or_restart(self, force):
            """Called after DB is installed or restarted.
            Updates the database with the actual DB server status.
            """
            real_status = self._get_actual_db_status()
            LOG.info(_("Current database status is '%s'.") % real_status)
            self.set_status(real_status, force=force)

        @property
        def is_installed(self):
            """This is for compatibility - it may be removed during further
            cleanup.
            """
            return self.prepare_completed

        def set_status(self, status, force=False):
            """Use conductor to update the DB app status."""

            if force or self.is_installed:
                LOG.debug("Casting set_status message to conductor "
                          "(status is '%s')." % status.description)
                context = trove_context.TroveContext()

                heartbeat = {'service_status': status.description}
                conductor_api.API(context).heartbeat(
                    CONF.guest_id, heartbeat, sent=timeutils.float_utcnow())
                LOG.debug("Successfully cast set_status.")
                self.status = status
            else:
                LOG.debug("Prepare has not completed yet, skipping heartbeat.")


Configuration
-------------

No configuration changes are anticipated.


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

The ServiceStatuses.BUILD_PENDING state has been renamed to
ServiceStatuses.INSTANCE_READY to better reflect the instance's actual state.
The value displayed will remain 'BUILD' so that there should be no outward
differences and thus backwards compatibility will be maintained.


Guest Agent
-----------

This change should not affect any behavior on the Guest Agent.  The current
tests should be adequate to ensure that the change is fully compatible with the
rest of the code base.


Alternatives
------------

One suggestion as to how to fix the prepare issue was to use Nova metadata,
which is available on the guest instance.  If it is decided that this would be
useful, it could be added in addition to the proposed method as a means of
notification only.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <peterstac>


Milestones
----------

Target Milestone for completion:
  eg. Mitaka-1


Work Items
----------

All changes will be done in the context of a single task.


Upgrade Implications
====================

None are anticipated.


Dependencies
============

None


Testing
=======

The unittests will be modified as necessary, however minimal changes will be
made in this regard as well.  In order to keep the changes as small as
possible, refactoring the tests will also be done in stages with only the bare
minimum done to start and the remainder being left to a future date.  The
future work would include testing the base class thoroughly and then removing
all the corresponding tests from the derived classes.

The int-tests should continue to run as always, and will be used to determine
that no fundamental changes have been made to the implementation, with the
exception of the bug fixes (and they should just lead to greater stability in
the test infrastructure).


Documentation Impact
====================

Since all the changes are implementation related, no documentation changes are
foreseen.


References
==========

.. [1] https://bugs.launchpad.net/trove/+bug/1482795

.. [2] https://bugs.launchpad.net/trove/+bug/1487233

Appendix
========

None
