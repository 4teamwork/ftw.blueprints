from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from Products.Archetypes.interfaces import IBaseObject
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
