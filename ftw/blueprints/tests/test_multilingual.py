from ftw.blueprints.sections.multilingual import LinguaPloneItemLinker
from ftw.blueprints.testing import BLUEPRINT_FUNCTIONAL_TESTING
from ftw.blueprints.tests.base import BlueprintTestCase
from ftw.blueprints.tests.utils import TestTransmogrifier
from ftw.builder import Builder
from ftw.builder import create
from plone.app.testing import applyProfile
from plone.app.testing.helpers import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from plone.multilingual.interfaces import ITranslationManager
from plone.multilingual.interfaces import ILanguage


ITEMS = [{
    '_path': '/en',
    '_canonicalTranslation': False,
    '_translationOf': '/de',
    'language': 'en',
    }, {
    '_path': '/de',
    '_canonicalTranslation': True,
    '_translationOf': '/de',
    'language': 'de',
    }, {
    '_path': '/en/file',
    '_canonicalTranslation': False,
    '_translationOf': '/de/file',
    'language': 'en',
    }, {
    '_path': '/de/file',
    '_canonicalTranslation': True,
    '_translationOf': '/de/file',
    'language': 'de',
    },
]


class TestMultilingual(BlueprintTestCase):

    layer = BLUEPRINT_FUNCTIONAL_TESTING
    klass = LinguaPloneItemLinker

    def setUp(self):
        super(TestMultilingual, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        applyProfile(self.portal, 'plone.app.multilingual:default')

        self._setup_content()
        self._run_transmogrifier()

    def _setup_content(self):
        self.folder_de = create(Builder('folder').titled('de'))
        self.folder_en = create(Builder('folder').titled('en'))

        self.file_de = create(Builder('file')
                              .within(self.folder_de)
                              .with_dummy_content())
        self.file_en = create(Builder('file')
                              .within(self.folder_en)
                              .with_dummy_content())

    def _run_transmogrifier(self):
        transmogrifier = TestTransmogrifier()
        transmogrifier.context = self.portal
        options = {'blueprint':
                   'ftw.blueprints.linguaploneitemtranslationlinker'}
        source = self.klass(transmogrifier, 'test', options, ITEMS)
        list(source)

    def test_language_is_set(self):
        self.assertEqual('de', ILanguage(self.folder_de).get_language())
        self.assertEqual('en', ILanguage(self.folder_en).get_language())

        self.assertEqual('de', ILanguage(self.file_de).get_language())
        self.assertEqual('en', ILanguage(self.file_en).get_language())

    def test_content_is_linked(self):
        manager = ITranslationManager(self.folder_en)
        self.assertEqual(self.folder_de, manager.get_translation('de'),
                          'English and German content should be linked.')
        self.assertEqual(2, len(manager.get_translations()))

        manager = ITranslationManager(self.file_de)
        self.assertEqual(self.file_en, manager.get_translation('en'),
                          'English and German content should be linked.')
        self.assertEqual(2, len(manager.get_translations()))
