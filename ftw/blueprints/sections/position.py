from Acquisition import aq_inner
from Acquisition import aq_parent
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from operator import itemgetter
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides, implements


ANNOTATION_KEY = 'ftw.blueprints-position'


class PositionInParentUpdater(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.positionkey = defaultMatcher(options, 'position-key', name, 'gopip')

    def __iter__(self):
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            positionkey = self.positionkey(*keys)[0]
            path = item[pathkey]
            position = item.get(positionkey)

            obj = self.context.unrestrictedTraverse(
                str(path).lstrip('/'), None)
            if obj is not None:
                self.updateObjectPosition(obj, position)

            yield item

    def updateObjectPosition(self, obj, position):
        """Store the position we want on the object and order all children
        of the parent according to their stored positions.

        This allows to partially migrate different types in a folder in different
        steps and will reorder already migrated siblings correctly because we
        have stored the position from the source installation.
        """

        if position is not None:
            self.store_position_for_obj(obj, position)
        parent = aq_parent(aq_inner(obj))
        self.reorder_children(parent)

    def store_position_for_obj(self, obj, position):
        IAnnotations(obj)[ANNOTATION_KEY] = position

    def reorder_children(self, obj):
        ordered_sibling_ids = self.get_ordered_children_ids_from_annotations(obj)
        obj.moveObjectsByDelta(ordered_sibling_ids, - len(ordered_sibling_ids))

    def get_ordered_children_ids_from_annotations(self, container):
        def get_position_from_annotations(item):
            id_, obj = item
            try:
                return IAnnotations(obj)[ANNOTATION_KEY]
            except (TypeError, KeyError):
                return 10000

        ordered_children = sorted(container.objectItems(), key=get_position_from_annotations)
        return map(itemgetter(0), ordered_children)
