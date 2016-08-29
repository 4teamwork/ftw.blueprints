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

Note: Some of the Archetypes and Dexterity example configs also reference
sections from `ftw.inflator <https://github.com/4teamwork/ftw.inflator/>`_.
If you base your config on one of these, you'll also need to install
``ftw.inflator``.


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ ``4.2``, ``4.3`` or ``5.0``.

Plone 4.2

.. image:: https://jenkins.4teamwork.ch/job/ftw.blueprints-master-test-plone-4.2.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.blueprints-master-test-plone-4.2.x.cfg

Plone 4.3

.. image:: https://jenkins.4teamwork.ch/job/ftw.blueprints-master-test-plone-4.3.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.blueprints-master-test-plone-4.3.x.cfg

Plone 5.0

.. image:: https://jenkins.4teamwork.ch/job/ftw.blueprints-master-test-plone-5.0.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.blueprints-master-test-plone-5.0.x.cfg


Blueprints provided by this package
-----------------------------------

- ftw.blueprints.fieldmapper
   - Powerful blueprint to map and change fields from the given item
     with a static value, lambda expressions, conditions and dict-mapping.

- ftw.blueprints.pathmapper
   - Map old paths to new paths. Applies the mapping recursively if required.

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
   - Alternate to the printer blueprint. Configurable logging blueprint to
     log the information given in an expression.

- ftw.blueprints.workflowmanager
   - Manages the workflow states, transitions and history

- ftw.blueprints.formmailer-fields-inserter
   - Blueprint to convert the very old PloneFormMailer fields to the new
     PloneFormGen archetype fields

- ftw.blueprints.contextualportletadder
   - Adds a portlet on a given context

- ftw.blueprints.unicodeawaremimeencapsulator
   - Unicode aware plone.app.transmogrifier.mimeencapsulator.

- ftw.blueprints.multilingual.linguaploneitemlinker
   - Create new translations with plone.app.multilingual from a source that used
     LinguaPlone.

- ftw.blueprints.positionupdater
   - A object position in parent blueprint, supporting Plone sites.

- Under construction / deprecated
   - ftw.blueprints.annotatedefaultviewpathobjects
   - ftw.blueprints.updatedefaultviewobjectpath
   - ftw.blueprints.checkisdefaultviewobject

ftw.blueprints.fieldmapper
~~~~~~~~~~~~~~~~~~~~~~~~~~

This blueprint is to map or change values on the item.

Required options:

- field-mapping
  - option to map or change fields

Using field-mapping:

  {'source-key': {option: value}}

- First, you need to define the source-key you want to modifiy.
- Then you need to define some options:

  - destination: the new name of the key.

    {'plz': {'destination':'zip'}

    Just moves the value of plz to zip

  - static_value: if you want to use a static value, you can use this
    option:

    {'plz': {'static_value':'3000'}}

    Replaces the value in plz with 3000

  - map_value: in some cases you want to change the values with a map:

    {'plz': {'map_value':{'PLZ 3000': '3000'}}}

    Tf the value of plz is PLZ 3000, it will be replaced with 3000

  - transform: transforms the value with the given function.
    As parameter, you have the item itself.

    {'plz': {'transform':lambda x: x['plz'] = x['plz'] and \
        x['plz'] or '3000'}}

    This example would replace the plz with 3000 if its value is None

  - need_src_key: in some cases you just want to do transforms if the
    source-key is available.

    {'plz': 'static_value':'3000', need_src_key: True}

    It would just set the static value if the source-key exists on the item.

The option 'need_src_key' defaults to False. So you can use the
mapper as a more powerful inserter blueprint. For example you can add
an attribute to the item which does not exist yet. If the source-key does not
exist on the item, it will be ignored by the mapper.

.. code::  python

    {'update_show_title': {
        'destination': 'showTitle',
        'transform': lambda x: x['title'] and True or False,
        }
    }

This example would set the non existing yet 'showTitle' attribute
on the item to True if the items title is not None.

Its also possible to do transforms on an attribute, after you can map it
with the map_value option.

.. code::  python

    {'title': {
        'destination': 'description',
        'transform': lambda x: x['title'].lower(),
        'map_value': {'james': 'bond', 'bud': 'spencer'}
        }
    }

First it transforms the title to lowercase. If the title contains one
of the given keys in the map_value option it will be replaced.
At the end, it put the transformed and mapped value into the description.

You can combine all this options together to do powerful mappings
on your item.

.. code::  python

    {'zip': {'static_value':'3000'},
     'client': {
         'destination': 'text',
         'transform': lambda x: x['language'] == \
         'en' and 'Customer: %s' % (x['cleint']) or \
         'Kunde: %s' % (x['client']),
         'need_src_key': True
       }
    }

First we put a static value to the zip attribute.
After we do some stuff with the client attribute. If the client-key
is available in the items-map, it fills a given
string, depending on the language of the object into the text
attribute.


Minimal configuration:

.. code:: cfg

    [fieldmapper]
    blueprint = ftw.blueprints.fieldmapper
    field-mapping = python:{}

Optional options:

There are no optional options.

ftw.blueprints.pathmapper
~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint updates the path for each item.

Required options:

- mapping

  - An iterable of mappings.

  - Each mapping-item is a tuple (regular_expression, replacement).

  - The mappings are applied exhaustively in the defined order.

  - expression, iterable

Minimal configuration:

.. code:: cfg

    [pathmapper]
    blueprint = ftw.blueprints.pathmapper
    mapping = python: (
        ('^/de/foo/bar', '/foo/bar'),
        ('^/en/foo/bar', '/foo/qux'),)

Optional options:

- path-key
  - The key-name for the path that is mapped. It defaults to _path.

- strip_prefixes
  - A list of prefixes that are stripped from each path if the paths starts with
  that prefix.

Full configuration

.. code:: cfg

    [pathmapper]
    blueprint = ftw.blueprints.pathmapper
    mapping = python: (
        ('^/de/foo/bar', '/foo/bar'),
        ('^/en/foo/bar', '/foo/qux'),)
    path-key = '_gak'
    strip-prefixes = python: (
      '/plone/www/irgendwo',)


ftw.blueprints.typefieldmapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint maps types and their fields to new types and new fields.

Required options:

- mapping

  - Nested mapping for types and their fields.

  - The first level maps types.

  - The second levels maps fields of the first level's types.

  - expression, dict

Minimal configuration:

.. code:: cfg

    [typefieldmapper]
    blueprint = ftw.blueprints.typefieldmapper
    mapping = python: {
            'OldType':  ('NewType', {'oldfield': 'newfield'}),
        }

Optional options:

- type-key
  - The key-name for the type that is mapped. It defaults to _type.

ftw.blueprints.childinserter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint inserts a new item to the pipline as a child.

The new item is not a copy of the parent-item. If you want to use metadata
of the parent-item, you need to map them with the metadata-key option

Required options:

- content-type
  - defines the contenttype of the child object
  - string

- additional-id
  - defines the new id of the child object
  - expression, string

-Minimal configuration:

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
  - expression, dict

  Using parents metadata:

    {'description': 'title'}

    will get the value of title on parent-item and put it into the description
    field on child-item

  Using new value:

    {'title': lambda x: 'Images'}

    will put 'Images' into the title field on child-item

- _interfaces
  - adds interfaces as a list to the child-item
  - expression, list

- _annotations
  - adds annotations as a dict to the child-item
  - expression, dict

Full configuration

.. code:: cfg

    [childinserter]
    blueprint = ftw.blueprints.childinserter
    content-type = ContentPage
    additional-id = python: 'downloads'
    metadata-key = python: {
        'title': lambda x: 'Images',
        'description': 'title',
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
           +--+------------------------+-----+


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
           +--+------------------------+-----+


ftw.blueprints.additionalobjectinserter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Blueprint inserts a new item to the pipline at a given path.

The new item is not a copy of the item. If you want to use metadata
of the item, you need to map them with the metadata-key option

Required options:

- new-path
  - the path including the id of the object you want create
  - expression, string

- content-type
  - defines the contenttype of the new object
  - string

- additional-id
  - defines the new id of the new object
  -expression, string

Minimal configuration:

.. code:: cfg

    [additionalobjectinserter]
    blueprint = ftw.blueprints.additionalobjectinserter
    content-type = Contact
    additional-id = python: 'downloads'
    new-path = python:'/contacts/contact-%s' % item['_id']

Please see the ftw.blueprints.childinserter section documentation for more
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
           +--+------------------------+----------+


ftw.blueprints.workflowmanager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint to manage workflows after migration

Whith this blueprint it's possible to migrate the workflowhistory and
the reviewstate.

It provides workflow-mapping, states-mapping and transition-mapping.

Required options:

- old-workflow-id
  - the name of the old workflow you want to migrate
  - String

Minimal configuration:

.. code:: cfg

    [workflowmanager]
    blueprint = ftw.blueprints.workflowmanager
    old-workflow-id = simple_publication_workflow

Optional options:

- update-history
  - default: True
  - Set it to False if you just want to update the review_state

- new-workflow-id
  - if the name of the new workflow differs to the old one.
  - String

- state-map
  - mapping for the old states to the new ones
  - expression, dict

- transition-map
  - mapping for the old transitions to the new ones
  - expression, dict

Full configuration

.. code:: cfg

    [workflowmanager]
    blueprint = ftw.blueprints.workflowmanager
    old-workflow-id = IntranetPublicationWorkflow
    new-workflow-id = intranet_secure_workflow
    state-map = python: {
        'draft': 'intranet_secure_workflow--STATUS--draft',
        'published': 'intranet_secure_workflow--STATUS--published',
        'revision': 'intranet_secure_workflow--STATUS--revision'}
    transition-map = python: {
        'publish': 'intranet_secure_workflow--TRANSITION--publish',
        'retract': 'intranet_secure_workflow--TRANSITION--retract'}


ftw.blueprints.contextualportletadder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint to insert a portlet on a given context.

Required options:

- manager-name
    - Name of the portletmanager you want to add a portlet
    - String

- assignment-path
    - Dotted name path to the portlet assignment you want to add
    - String

- portlet-id
    - ID of the portlet you want to add
    - String

Minimal configuration:

.. code:: cfg

    [contextualportletadder]
    blueprint = ftw.blueprints.contextualportletadder
    manager-name = plone.rightcolumn
    assignment-path = ftw.contentpage.portlets.news_archive_portlet.Assignment
    portlet-id = news_archive_portlet


Optional options:

- portlet-properties
    - Default properties for the portlet assignment
    - expression, dict


ftw.blueprints.formmailer-fields-inserter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Blueprint to convert the very old PloneFormMailer fields to the new
PloneFormGen archetype fields

The Problem converting the fields of the PloneFormMailer is, that they aren't
Archetype fields like in the PloneFormGen. To convert it automatically, we
use the formXML function of the Formulator package and put the exported xml-
form-representation into the item exported with collective.jsonify.

After creating the form itself trough the pipeline, we parse the xml and
convert it to a transmogrifier item with the archetypes fields.

See the example ftw.blueprints.pfm2pfg config to see how to integrate
the PloneFormMailer migration correctly into the pipeline.

Minimal configuration:

.. code:: cfg

    [formmailer-fields-inserter]
    blueprint = ftw.blueprints.formmailer-fields-inserter


ftw.blueprints.unicodeawaremimeencapsulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Makes plone.app.transmogrifier.mimeencapsulator accept unicode input data. The
configuration options don't change. See `transmogrifier documentation
<https://pypi.python.org/pypi/plone.app.transmogrifier#mime-encapsulator-section>`_.


ftw.blueprints.multilingual.linguaploneitemlinker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Links translations in the new Plone site with plone.app.multilingual. Expects
that the source has been translated with LinguaPlone. Furthermore expects that
Plone content in the new site has already been constructed when this section
runs.

Note that when you are mapping paths you should also apply the same mapping to
the reference to the canonical translation (_translationOf).

Minimal configuration:

.. code:: cfg

    [multilingual]
    blueprint = ftw.blueprints.multilingual.linguaploneitemlinker

Optional options:

- path-key
  - The key-name for the new item's path. It defaults to _path.

- canonical-key
  - The key-name for the boolean that indicates whether this item is a canonical
  translation. It defaults to _canonicalTranslation.

- translationOf
  - The key-name for the reference to the canonical translation. It defaults to
  _translationOf.


ftw.blueprints.positionupdater
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``positionupdater`` blueprint supports folders and Plone sites.
It stores the desired position of each object in its annotations,
so that we can migrate children separately but keep the position
(e.g. one FTI at a time).

.. code:: cfg

    [position]
    blueprint = ftw.blueprints.positionupdater

Optional:

- ``path-key``
  - The key-name for the new item's path. It defaults to ``_path``.

- ``position-key``
  - The key-name for the item's position. It defaults to ``_gopip``.


Links
-----

- Github: https://github.com/4teamwork/ftw.blueprints
- Issues: https://github.com/4teamwork/ftw.blueprints/issues
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.blueprints


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.blueprints`` is licensed under GNU General Public License, version 2.
