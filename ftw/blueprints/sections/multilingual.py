from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from plone.multilingual.interfaces import ILanguage
from plone.multilingual.interfaces import IMutableTG
from plone.multilingual.interfaces import ITranslatable
from plone.multilingual.interfaces import ITranslationManager
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility
from zope.interface import classProvides
from zope.interface import implements


class LinguaPloneItemLinker(object):
    """Link content from a page that was translated with LinguaPlone.
    The items in the pipeline are ecpected to have the following keys:

        - a boolean indicating whether they are a 'canonical' translation
        - a reference (path) to the canonical translation (points to the item
          itself when the item is a canonical translation)
        - a path

    This section expects that plone content has already been constructed. The
    new translations are then created with plone.app.multilingual.

    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.canonicalkey = defaultMatcher(options, 'canonical-key', name,
                                           'canonicalTranslation')
        self.translationkey = defaultMatcher(options, 'translation-key', name,
                                             'translationOf')
        self.uuid_generator = getUtility(IUUIDGenerator)

        self.deferred = []

    def _traverse(self, path):
        return self.context.unrestrictedTraverse(path.lstrip('/'), None)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            if not pathkey:
                yield item
                continue

            path = item[pathkey]
            if isinstance(path, unicode):
                path = path.encode('ascii')

            obj = self._traverse(path)
            if obj is None:
                yield item
                continue

            canonicalkey = self.canonicalkey(*item.keys())[0]
            translationkey = self.translationkey(*item.keys())[0]

            if not canonicalkey:
                yield item
                continue

            canonicalpath = item[translationkey]
            language = item['language']
            if ITranslatable.providedBy(obj):
                ILanguage(obj).set_language(language)
            if item[canonicalkey]:
                IMutableTG(obj).set(self.uuid_generator())
                manager = ITranslationManager(obj)
                manager.register_translation(language, obj)
            else:
                self.deferred.append((path, canonicalpath, language))
            yield item

        self._update_deferred()

    def _update_deferred(self):
        for path, canonicalpath, language in self.deferred:
            obj = self._traverse(path)
            if obj is None:
                continue
            canonical = self._traverse(canonicalpath)
            if canonical is None:
                continue

            if (ITranslatable.providedBy(obj) and
                    ITranslatable.providedBy(canonical)):
                try:
                    translation_group = IMutableTG(canonical).get()
                    IMutableTG(obj).set(translation_group)
                    manager = ITranslationManager(obj)
                    manager.register_translation(language, obj)
                except KeyError:
                    # put obj in a separate translation group when registration
                    # fails
                    IMutableTG(obj).set(self.uuid_generator())
