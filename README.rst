ftw.blueprints
==============

``ftw.blueprints`` provides some useful blueprints and includes example cfgs
for archetypes and dexterity.

.. contents:: Table of Contents


Installation
------------

- Add ``ftw.blueprints`` to your buildout configuration:

.. code:: rst

    [instance]
    eggs +=
        ftw.blueprints

- Open view @@jsonmigrator and chose your configuration file


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.1`, `4.2` or `4.3`.


Blueprints provided by this package
-----------------------------------

- ftw.blueprints.fieldmapper
    - Powerful blueprint to map and change fields from the given item
    with a static value, lambda expressions, conditions and dict-mapping.

- ftw.blueprints.regexreplacer
    - Replaces values with regex

- ftw.blueprints.logger
    - Alternate to the printer blueprint. It just logging some useful
    informations about the item in the pipeline and not the whole item.

- ftw.blueprints.workflowmapper
    - Map your old workflows with new ones.

- ftw.blueprints.parentworkflowmapper
    - assume the parents workflowstate for the item

- ftw.blueprints.childinserter
    - Inserts a child for the given item

- ftw.blueprints.parentinserter
    - Inserts a parent for the given item

- ftw.blueprints.dataupdater
    - Updates blob data.


<!-- Under construction - deprecated -->


- ftw.blueprints.annotatedefaultviewpathobjects
- ftw.blueprints.updatedefaultviewobjectpath
- ftw.blueprints.checkisdefaultviewobject
- ftw.blueprints.workflowupdater


Links
-----

- Main github project repository: https://github.com/4teamwork/ftw.blueprints
- Issue tracker: https://github.com/4teamwork/ftw.blueprints/issues
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.blueprints


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.blueprints`` is licensed under GNU General Public License, version 2.

.. _collective.deletepermission: https://github.com/4teamwork/collective.deletepermission

.. image:: https://cruel-carlota.pagodabox.com/ef218e7bdb19163396b77d70f31e984e
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.blueprints
