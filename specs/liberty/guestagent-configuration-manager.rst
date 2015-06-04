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


================================
Guestagent Configuration Manager
================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/guestagent-configuration-manager


Problem Description
===================

Each datastore currently has to implement a strategy for maintaining its
configuration files including functionality for parsing, updating
properties, saving and managing overrides.
With increasing number of supported datastores this approach leads to a
significant duplication in the production and testing codebase.

Proposed Change
===============

Facilitate code reuse by implementing a manager class that could be used by all
guestagents to manage their configuration files and overrides.

The patch set will consist of four main features.

   1. Codecs for serialization and deserialization of configuration files.

      These would be responsible for parsing a Python structure (dict)
      into an appropriate serialized form (see the simple example below).

      An INI-style file (serialized form):

      .. code-block:: bash

         [section_1]
         key1 = value1
         key2 = value2
         ...

         [section_2]
         key1 = value1
         key2 = value2
         ...

      Dict representation of the above contents (deserialized form):

      .. code-block:: bash

         {'section_1': {'key1': 'value1', 'key2': 'value2', ...},
          'section_2': {'key1': 'value1', 'key2': 'value2', ...}
          ...
         }

      Codecs for common configuration formats currently present in Trove
      will be implemented.

      These include:
         - INI-style format: see the example above
         - YAML format: see http://pyyaml.org/wiki/PyYAMLDocumentation
           for examples of Python representation.
         - Properties format:

               Serialized form:

               .. code-block:: bash

                  key1 k1arg1 k1arg2 ... k1argN
                  key2 k2arg1 k2arg2 ... k2argN
                  key3 k3arg1 k3arg2 ...
                  key3 k3arg3 k3arg4 ...

               Dict representation of the above contents (deserialized form):

               .. code-block:: bash

                  {'key1': [k1arg1, k1arg2 ... k1argN],
                   'key2': [k2arg1, k2arg2 ... k2argN],
                   'key3': [[k3arg1, k3arg2, ...], [k3arg3, k3arg4, ...]]}

   2. Functions for reading and writing using a given codec.

      A 'write' function saves a serialized form of a given dict into a file.
      A 'read' function applied on the file produces the same dict
      structure that was written in the previous step.
      The write function will write a file with superuser privileges when
      provided an optional 'as_root' keyword. This will be implemented by
      writing a temporary file first moving it to place using the existing
      operating system calls.

   3. The configuration manager.

      ConfigurationManager will be responsible for management of datastore
      configuration files.
      Its base functionality will include reading and writing configuration
      files and updating or retrieving current values.
      It will be also responsible for validating user inputs and requests.
      When supplied an override strategy (below) it allows the user to manage
      configuration overrides as well.

      The configuration manager will be responsible for enforcing the limit on
      the number of applied overrides (there can currently be only one
      override applied to an instance at any given time).

   4. Common override strategies.

      An override strategy object responsible for management of overrides
      in the configuration manager (when provided).

      It will implement functions to:

         - *apply* updated values on the current revision of the configuration
           file.
         - *remove* the last applied overrides and effectively restoring the
           previous version of the configuration file.

      The strategies provided with this patch set will be:

         - Rolling Override Strategy:

           A strategy suitable for applications that do not support includes
           in their configuration files. It applies updates to the
           configuration file while maintaining a backup of the previous
           version that can be restored when the overrides get removed.

           Apply procedure:

              * Save a backup copy of the current configuration file to a known
                configurable location.
              * Load and parse the current configuration file into a
                dict (using an appropriate codec).
              * Update the dict with the overridden values.
              * Overwrite the configuration file with the serialized form
                of the dict (using the same codec).

           Remove procedure:

                * Move the appropriate backup revision over the current
                  configuration file.

         - Import Override Strategy:

           A strategy useful for datastores that support imports in their
           configuration files (like MySQL).
           The overrides are stored in a known configurable directory which
           is then imported by the base configuration file which itself remains
           intact.

           Apply procedure:

           * Store a serialized form (using an appropriate codec) of the
             overrides dict in an imported location.

           Remove procedure:

           * Remove the appropriate file from the imported location.


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

Python API
----------

None

CLI (python-troveclient)
------------------------

None

Internal API
------------

None

Guest Agent
-----------

The affected files would include:

   - guestagent/common/operating_system.py: I/O functions
   - common/stream_codecs.py: Implementations of codecs.
   - common/configurations.py: Reuse the codecs in configuration parsers.
   - guestagent/common/configuration.py: Implementations of the configuration
     manager and override strategies.

Alternatives
------------

None

Implementation
==============

Assignee(s)
-----------

Petr Malik <pmalik@tesora.com>

Milestones
----------

Liberty-1

Work Items
----------

- Implement codecs for serialization and deserialization of common
  configuration files.
- Implement functions for reading and writing files using a given codec.
- Implement the configuration manager.
- Implement common override strategies.
- Add unit tests for the above functionality.


Upgrade Implications
====================

None

Dependencies
============

The current implementation works around limitations of the ConfigParser
in Python 2.6. OpenStack no longer supports this version of Python
and Trove gate tests run against Python 2.7
We can therefore remove the compatibility requirement and make full use of
the ConfigParser in Python 2.7 in the existing code base.

Testing
=======

Unit tests will be added to cover non-trivial code paths.

Documentation Impact
====================

None

References
==========

None
