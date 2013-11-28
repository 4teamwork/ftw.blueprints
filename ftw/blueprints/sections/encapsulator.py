from OFS.Image import File
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from plone.app.transmogrifier.mimeencapsulator import MimeEncapsulatorSection
from zope.interface import classProvides, implements


class UnicodeAwareMimeEncapsulator(MimeEncapsulatorSection):
    """Make the default plone.app.transmogrifier.mimeencapsulator work with
    unicode fields.

    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __iter__(self):
        for item in self.previous:
            key, match = self.datakey(*item.keys())
            if not key:
                yield item
                continue

            field = self.field(item, key=key, match=match)
            mimetype = self.mimetype(item, key=key, match=match, field=field)

            if self.condition(item,
                    key=key, match=match, field=field, mimetype=mimetype):
                value = item[key]
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                item[field] = File(field, field, value, mimetype)

            yield item
