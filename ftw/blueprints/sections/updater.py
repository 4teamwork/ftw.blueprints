from Products.Archetypes.interfaces import IBaseObject
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import defaultMatcher
from plone.folder.default import DefaultOrdering
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides, implements
import base64
import logging
import os


class DataUpdater(object):
    classProvides(ISectionBlueprint)
    implements(ISection)
    """
    Updates base64 encoded blob data on the item
    """

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.logger = logging.getLogger(options['blueprint'])
        self.data_field = options.get('data-field')
        self.schema_field = options.get('schema-field')
        self.condition = Condition(options.get('condition', 'python:True'),
            transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:

            if not self.condition(item):
                yield item
                continue

            file_obj = self.context.unrestrictedTraverse(
                            str(item['_path']).lstrip('/'), None)

            if not file_obj and not IBaseObject.providedBy(file_obj):
                self.logger.warn(
                    "Context does not exist at %s" % item['_path'])

                yield item
                continue

            field = file_obj.Schema().get(self.schema_field)

            if not field:
                yield item
                continue

            value = item.get(self.data_field, {})

            self._update_data_field(file_obj, field, value)

            yield item

    def _update_data_field(self, obj, field, value):

        if not value.get('data'):
            return

        filename = value.get('filename')
        if not filename:
            filename = obj.getId()

        field.set(obj, base64.b64decode(value.get('data')))
        field.get(obj).filename = filename
        field.get(obj).setContentType(self.guess_mimetype(
                filename, value.get('content_type')))

        self.logger.info('Updated file data with filename: %s' % filename)

    def guess_mimetype(self, filename, default):
        # Try to guess mime type and content type
        basename, extension = os.path.splitext(filename)
        # we need only the extension without delimiter
        extension = extension[1:]
        return self.context.mimetypes_registry.extensions.get(
            extension.lower(), default)


class PositionInParentUpdater(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.positionkey = defaultMatcher(options, 'position-key', name, '_gopip')

    def __iter__(self):
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            positionkey = self.positionkey(*keys)[0]
            path = item[pathkey]
            position = item.get(positionkey)

            obj = self.context.unrestrictedTraverse(
                str(path).lstrip('/'), None)
            if obj is None:         # path doesn't exist
                yield item; continue

            self.updateObjectPosition(obj, position)

    def updateObjectPosition(self, obj, position):
        """
        Updates the position of the object and it siblings (reset position of
        all children of the parent object).
        Objects, which do not exist at the sender instance, are moved to the
        bottom.
        """
        parent = obj.aq_inner.aq_parent
        annotations = IAnnotations(parent)
        order = annotations.get(DefaultOrdering.ORDER_KEY)
        if not order:
            return
        order.remove(obj.getId())
        order.insert(position, obj.getId())

        annotations[DefaultOrdering.ORDER_KEY] = order

        pos = annotations.get(DefaultOrdering.POS_KEY)
        for n, id in enumerate(order):
            pos[id] = n

        # reindex all objects
        for id in order:
            try:
                parent.get(id).reindexObject(
                    idxs=['positionInParent', 'getObjPositionInParent'])
            except:
                print "FAILED to indec %s" % id
