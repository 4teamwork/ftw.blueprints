from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.base.interfaces import ISimpleLayoutCapable
from simplelayout.base.interfaces import ISlotA
from simplelayout.base.interfaces import ISlotB
from zope.interface import classProvides, implements
from zope.interface import directlyProvides, noLongerProvides
from simplelayout.base.interfaces import ISimplelayoutTwoColumnView
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
            if ISimpleLayoutCapable.providedBy(obj):
                if item['two_columns']:
                    directlyProvides(obj, ISimplelayoutTwoColumnView)
            elif ISimpleLayoutBlock.providedBy(obj):
                if item['imageLayout']:
                    anno = IAnnotations(obj)
                    anno['imageLayout'] = item['imageLayout']
                if item['right_slot']:
                    noLongerProvides(obj, ISlotA)
                    directlyProvides(obj, ISlotB)
            yield item
