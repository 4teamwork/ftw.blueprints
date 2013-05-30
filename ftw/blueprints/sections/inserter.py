from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from zope.interface import classProvides, implements
import os


class AdditionalObjectInserter(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    insert_as_parent = False

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.condition = Condition(options.get('condition', 'python:True'),
            transmogrifier, name, options)
        self.content_type = options.get('content-type')
        self.additional_id = options.get('additional-id')
        self.interfaces = Expression(
            options.get('_interfaces', 'python:[]'), transmogrifier, name, options)
        self.annotations = Expression(
            options.get('_annotations', 'python:{}'), transmogrifier, name, options)
        self.metadata = Expression(
            options.get('metadata-key', 'python:{}'), transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:

            if not self.condition(item):
                yield item
                continue

            additional_item = self.create_additional_item(item)

            if self.insert_as_parent:
                parent, child = additional_item, item
                self.rename_item(parent, self.additional_id)
            else:
                parent, child = item, additional_item
                self.rename_item(child, self.additional_id)

            self.move_item_into_container(child, parent)

            yield parent
            yield child

    def rename_item(self, item, new_id):
        item['_path'] = os.path.join(os.path.dirname(item['_path']), new_id)

    def move_item_into_container(self, item, container):
        item_id = os.path.basename(item['_path'])
        item['_path'] = os.path.join(container['_path'], item_id)

    def create_additional_item(self, item):

        additional_item = {
                '_type': self.content_type,
                '_interfaces': self.interfaces(item),
                '_annotations': self.annotations(item),
                '_id': self.additional_id,
                '_path': item['_path']
                }

        self.extend_metadata(item, additional_item, self.metadata(item))

        return additional_item

    def extend_metadata(self, item, additional_item, metadata):
        """Extends the new item with additinoal metadata
        """

        for key, value_key in metadata.items():
            # It 's possible to map a field to a callable function
            # instead of an allready existing key
            # per example:
            # -- lambda item: item.get('title', '')
            if callable(value_key):
                additional_item[key] = value_key(item)

            elif item.get(value_key) is not None:
                additional_item[key] = item.get(value_key)


class ChildInserter(AdditionalObjectInserter):
    """Inserts a new item into the transmogrifier pipeline as a child
    """
    classProvides(ISectionBlueprint)
    implements(ISection)


class ParentInserter(AdditionalObjectInserter):
    """Inserts a new item into the transmogrifier pipeline as a parent
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    insert_as_parent = True
