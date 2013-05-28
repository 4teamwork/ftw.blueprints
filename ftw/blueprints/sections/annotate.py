from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides, implements


MIGR_KEY = "migr_has_default_view_object"


class AnnotateDefaultViewPathObjects(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:

            properties = item['_properties']
            for prop in properties:

                if not prop[0] == 'default_page':
                    yield item
                    continue

                obj = self.context.unrestrictedTraverse(
                    str(item['_path']).lstrip('/'), None)

                # Hack to know in an other migration if the object is
                # a default view object.
                IAnnotations(obj)[MIGR_KEY] = '%s/%s' % (
                    item['_path'], prop[1])

            yield item


class CheckIsDefaultViewObject(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:

            parent_path = item['_path'].lstrip('/').split('/')[:-1]

            if not parent_path:
                yield item
                continue

            parent = self.context.unrestrictedTraverse(
                str('/'.join(parent_path)), None)

            object_path = IAnnotations(parent).get(MIGR_KEY)

            if not object_path:
                yield item
                continue

            if object_path == item['_path']:
                item['is_default_view_object'] = True

            yield item


class UpdateDefaultViewObjectPath(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def __iter__(self):
        for item in self.previous:
            if item.get('is_default_view_object', False):
                path = '/'.join(item['_path'].split('/')[:-1])
                item['_path'] = path

            yield item
