from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.interface import classProvides, implements
from zope.annotation.interfaces import IAnnotations

class SimplelayoutSettings(object):
    """Baseclass to add an item to the transmogrifier pipeline.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.sitepath = options['sitepath']

    def __iter__(self):
        for item in self.previous:
            obj = self.context.restrictedTraverse('/'.join(self.context.getPhysicalPath()) + item['_path'])
            if ISimpleLayoutBlock.providedBy(obj) and item.get('imageLayout'):
                anno = IAnnotations(obj)
                anno['imageLayout'] = item['imageLayout']
            yield item
