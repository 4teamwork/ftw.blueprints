from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from zope.interface import classProvides, implements
import logging


class SLBlockCreator(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.logger = logging.getLogger(options['blueprint'])
        self.condition = Condition(
            options.get('condition'), transmogrifier, name, options)
        self.block_type = options.get('block-type')
        self._id = options.get('id', 'portlet')
        self.path_key = options.get('path-key', '_path')
        self.id_key = options.get('id-key', 'id')
        self.interfaces = Expression(
            options['_interfaces'], transmogrifier, name, options)
        self.annotations = Expression(
            options['_annotations'], transmogrifier, name, options)
        self.metadata = Expression(
            options['metadata-key'], transmogrifier, name, options)
        self.insert_as_parent = Condition(
            options['insert-as-parent'], transmogrifier, name, options)
        self.no_duplicates = Condition(
            options['no-duplicates'], transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:

            if self.condition(item):
                block = item.copy()

                # generate path
                if self.insert_as_parent(item):
                    # replace the id of the item () with the block id
                    item_path = item.get(self.path_key)
                    block_path = '%s/%s' % (
                        '/'.join(item_path.split('/')[:-1]), self._id)
                else:
                    block_path = '%s/%s' % (item.get(self.path_key), self._id)

                block = {
                    '_type': self.block_type,
                    '_path': block_path,
                    '_interfaces': self.interfaces(item),
                    '_annotations': self.annotations(item)}

                # extend with metadata
                for key, value_key in self.metadata(item).items():
                    # It 's possible to map a field to a callable function
                    # instead of an allready existing key
                    # per example:
                    # -- lambda item: item.get('title', '')
                    if callable(value_key):
                        block[key] = value_key(item)

                    elif item.get(value_key) is not None:
                        block[key] = item.get(value_key)

                # yield item and new block
                if self.insert_as_parent(item):
                    if self.no_duplicates(item):
                        if not self.allready_exist(block['_path']):
                            yield block
                    else:
                        yield block

                    # 'move' the object in to the block
                    item[self.path_key] = '%s/%s' % (
                        block.get('_path'), item.get(self.id_key))
                    yield item
                else:
                    yield item
                    if self.no_duplicates(item):
                        if not self.allready_exist(block['_path']):
                            yield block
                    else:
                        yield block

            else:
                yield item

    def allready_exist(self, path):
        obj = self.context.unrestrictedTraverse(path.lstrip('/'), None)
        if obj:
            if path == '/'.join(obj.getPhysicalPath()):
                return True
        return False