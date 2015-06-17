from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from simplelayout.base.interfaces import IBlockConfig
from simplelayout.base.interfaces import ISimpleLayoutBlock
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides, implements


class SimplelayoutSettings(object):
    """Baseclass to add an item to the transmogrifier pipeline.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:
            obj = self.context.restrictedTraverse('/'.join(self.context.getPhysicalPath()) + item['_path'])
            if ISimpleLayoutBlock.providedBy(obj) and item.get('imageLayout'):
                anno = IAnnotations(obj)
                anno['imageLayout'] = item['imageLayout']

            if ISimpleLayoutBlock.providedBy(obj) and 'blockconf' in item:
                blockconf = IBlockConfig(obj)
                blockconf.block_height = item['blockconf']['block_height']
                blockconf.image_layout = item['blockconf']['image_layout']
                blockconf.viewlet_manager = item['blockconf']['viewlet_manager']
                blockconf.viewname = item['blockconf']['viewname']
            yield item
