from ftw.blueprints.sections.position import PositionInParentUpdater
from ftw.blueprints.testing import BLUEPRINT_INTEGRATION_TESTING
from ftw.blueprints.tests.base import BlueprintTestCase
from ftw.blueprints.tests.utils import TestTransmogrifier
from ftw.builder import Builder
from ftw.builder import create
from plone.app.testing.helpers import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from Products.CMFCore.utils import getToolByName


class TestPositionInParentUpdater(BlueprintTestCase):
    layer = BLUEPRINT_INTEGRATION_TESTING
    klass = PositionInParentUpdater

    def setUp(self):
        super(TestPositionInParentUpdater, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_updating_object_position_in_folder(self):
        folder = create(Builder('folder').titled('folder'))
        create(Builder('folder').titled('three').within(folder))
        create(Builder('folder').titled('two').within(folder))
        create(Builder('folder').titled('one').within(folder))

        self.assert_obj_positions(folder, ['three', 'two', 'one'])
        self.assert_catalog_positions(folder, ['three', 'two', 'one'])

        self.run_transmogrifier([{'_path': 'folder/one', '_gopip': 11},
                                 {'_path': 'folder/two', '_gopip': 22},
                                 {'_path': 'folder/three', '_gopip': 33}])

        self.assert_obj_positions(folder, ['one', 'two', 'three'])
        self.assert_catalog_positions(folder, ['one', 'two', 'three'])

        self.run_transmogrifier([{'_path': 'folder/three', '_gopip': 33}])
        self.run_transmogrifier([{'_path': 'folder/two', '_gopip': 22}])
        self.run_transmogrifier([{'_path': 'folder/one', '_gopip': 11}])

        self.assert_obj_positions(folder, ['one', 'two', 'three'])
        self.assert_catalog_positions(folder, ['one', 'two', 'three'])

    def test_updating_object_position_in_plone_site(self):
        create(Builder('folder').titled('three'))
        create(Builder('folder').titled('two'))
        create(Builder('folder').titled('one'))

        self.assert_obj_positions(self.portal, ['three', 'two', 'one'])
        self.assert_catalog_positions(self.portal, ['three', 'two', 'one'])

        self.run_transmogrifier([{'_path': 'one', '_gopip': 11},
                                 {'_path': 'two', '_gopip': 22},
                                 {'_path': 'three', '_gopip': 33}])

        self.assert_obj_positions(self.portal, ['one', 'two', 'three'])
        self.assert_catalog_positions(self.portal, ['one', 'two', 'three'])

        self.run_transmogrifier([{'_path': 'three', '_gopip': 33}])
        self.run_transmogrifier([{'_path': 'two', '_gopip': 22}])
        self.run_transmogrifier([{'_path': 'one', '_gopip': 11}])

        self.assert_obj_positions(self.portal, ['one', 'two', 'three'])
        self.assert_catalog_positions(self.portal, ['one', 'two', 'three'])

    def run_transmogrifier(self, items):
        transmogrifier = TestTransmogrifier()
        transmogrifier.context = self.portal
        options = {'blueprint': 'ftw.blueprints.positionupdater'}
        source = self.klass(transmogrifier, 'test', options, items)
        return list(source)

    def assert_obj_positions(self, container, expected):
        got = [id_ for id_ in container.objectIds() if id_ in expected]
        self.assertEquals(expected, got)

    def assert_catalog_positions(self, container, expected):
        catalog = getToolByName(self.portal, 'portal_catalog')
        query = {'path': {'query': '/'.join(container.getPhysicalPath()),
                          'depth': 1},
                 'id': expected,
                 'sort_on': 'getObjPositionInParent'}
        got = [brain.getId for brain in catalog(query)]
        self.assertEquals(expected, got, 'Catalog indexes not up to date.')
