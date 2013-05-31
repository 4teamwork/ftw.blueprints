ftw.blueprints
==============

``ftw.blueprints`` provides some useful blueprints and includes example cfgs
for archetypes and dexterity.

For more informations about creating blueprints and how to use them see:

- https://github.com/collective/collective.jsonmigrator
- https://pypi.python.org/pypi/collective.transmogrifier

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

- ftw.blueprints.childinserter
    - Inserts a child for the given item

- ftw.blueprints.parentinserter
    - Inserts a parent for the given item

- ftw.blueprints.additionalobjectinserter
    - Inserts an object at the given path

- ftw.blueprints.dataupdater
    - Updates blob data.

- ftw.blueprints.regexreplacer
    - Replaces values with regex

- ftw.blueprints.logger
    - Alternate to the printer blueprint. It just logging some useful
      informations about the item in the pipeline and not the whole item.

- ftw.blueprints.workflowmapper
    - Map your old workflows with new ones.

- ftw.blueprints.parentworkflowmapper
    - assume the parents workflowstate for the item

<!-- Under construction - deprecated -->


- ftw.blueprints.annotatedefaultviewpathobjects
- ftw.blueprints.updatedefaultviewobjectpath
- ftw.blueprints.checkisdefaultviewobject
- ftw.blueprints.workflowupdater

ftw.blueprints.childinserter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint inserts a new item to the pipline as a child.

THe new item is not a copy of the parent-item. If you want to use metadata
of the parent-item, you need to map them with the metadata-key option

Required options:

- content-type
  - defines the contenttype of the child object

- additional-id
  - defines the new id of the child object

Minimal configuration:

.. code:: cfg

    [childinserter]
    blueprint = ftw.blueprints.childinserter
    content-type = ContentPage
    additional-id = python: 'downloads'


Optional options:

- metadata-key
  - metadatamapping for the child as a dict.
  you can provide metadata from the parent item for the child or you can
  use lambda expressions to set a new value.

  Using parents metadata:

    {'description', 'title'}

    will get the value of title on parent-item and put it into the description
    field on child-item

  Using new value:

    {'title', lambda x: 'Images'}

    will put 'Images' into the title field on child-item

- _interfaces
  - adds interfaces as a list to the child-item

- _annotations
  - adds annotations as a dict to the child-item

Full configuration

.. code:: cfg

    [childinserter]
    blueprint = ftw.blueprints.childinserter
    content-type = ContentPage
    additional-id = python: 'downloads'
    metadata-key = python: {
        'title', lambda x: 'Images',
        'description', 'title',
        }
    _interfaces = python: [
        "simplelayout.portlet.dropzone.interfaces.ISlotBlock",
        "remove:simplelayout.base.interfaces.ISlotA"
        ]
    _annotations = {'viewname': 'portlet'}

Visual example:

 * A = item in pipeline
 * A' = item in pipeline after blueprint
 * B = child in pipeline after the item

.. code::

                +-------------------+
                | _path: /foo       |
                | _id: album        | (A)
                | _type: Folder     |
                +---------+---------+
                          |
                          | 1.0
                          |
           +--------------+------------------+
           |           BLUEPRINT             |
           |   content-type = Image          |
           |   additional-id = python: 'bar' |
           |                                 |
           +--+------------------------+-----+
              |                        |
              |                        | 1.2
              |                  +-----+-------------+
              | 1.1              | _path: /foo/bar   |
              |                  | _id: bar          | (B)
              |                  | _type: Image      |
              |                  +-----+-------------+
    +---------+---------+              |
    | _path: /foo       |              |
    | _id: album        | (A')         |
    | _type: Folder     |              |
    +---------+---------+              |
              |                        |
              | 1.1.1                  | 1.2.1
              |                        |
           +--+-----------+------------+-----+


ftw.blueprints.parentinserter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint inserts a new item to the pipline as a parent.

The new item is not a copy of the child-item. If you want to use metadata
of the child-item, you need to map them with the metadata-key option

Pleas see the ftw.blueprints.childinserter section documentation for how to
use.

Visual Example:

 * A = item in pipeline
 * A' = item in pipeline after blueprint
 * B = parent in pipeline after the item

.. code::

                +-------------------+
                | _path: /foo       |
                | _id: album        | (A)
                | _type: Image      |
                +---------+---------+
                          |
                          | 1.0
                          |
           +--------------+------------------+
           |           BLUEPRINT             |
           |   content-type = Folder         |
           |   additional-id = python: 'bar' |
           |                                 |
           +--+------------------------+-----+
              |                        |
              |                        | 1.2
              |                  +-----+-------------+
              | 1.1              | _path: /bar/foo   |
              |                  | _id: album        | (A')
              |                  | _type: Image      |
              |                  +-----+-------------+
    +---------+---------+              |
    | _path: /bar       |              |
    | _id: bar          | (B)          |
    | _type: Folder     |              |
    +---------+---------+              |
              |                        |
              | 1.1.1                  | 1.2.1
              |                        |
           +--+-----------+------------+-----+


ftw.blueprints.additionalobjectinserter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint inserts a new item to the pipline at a given path.

The new item is not a copy of the item. If you want to use metadata
of the item, you need to map them with the metadata-key option

Required options:

- new-path
  - the path including the id of the object you want create

- content-type
  - defines the contenttype of the child object

- additional-id
  - defines the new id of the child object

Minimal configuration:

.. code:: cfg

    [additionalobjectinserter]
    blueprint = ftw.blueprints.childinserter
    content-type = Contact
    additional-id = python: 'downloads'
    new-path = python:'/contacts/contact-%s' % item['_id']

Pleas see the ftw.blueprints.childinserter section documentation for more
informations about optional options.

Visual Example:

 * A = item in pipeline
 * A' = item in pipeline after blueprint
 * B = parent in pipeline after the item

.. code::

                +-------------------+
                | _path: /foo       |
                | _id: album        | (A)
                | _type: Image      |
                +---------+---------+
                          |
                          | 1.0
                          |
           +--------------+-----------------------+
           |           BLUEPRINT                  |
           |   content-type = Contact             |
           |   additional-id = python: 'bar'      |
           |   new-path = python:'/contacts/james |
           |                                      |
           +--+------------------------+----------+
              |                        |
              |                        | 1.2
              |                  +-----+-------------+
              | 1.1              | _path: /foo       |
              |                  | _id: album        | (A')
              |                  | _type: Image      |
              |                  +-----+-------------+
    +---------+----------------+       |
    | _path: /contacts/james   |       |
    | _id: bar                 | (B)   |
    | _type: Contact           |       |
    +---------+----------------+       |
              |                        |
              | 1.1.1                  | 1.2.1
              |                        |
           +--+-----------+------------+----------+

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
