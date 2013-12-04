from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from ftw.blueprints.tests.utils import TestTransmogrifier


class BlueprintTestCase(TestCase):

    klass = None
    input_data = None

    def _get_expected(self, changes=None):
        expected = self.input_data.copy()
        if changes:
            expected.update(changes)
        return [expected]

    def test_implements_interface(self):
        # skip if not inherited
        if self.__class__ == BlueprintTestCase:
            return

        self.assertIsNotNone(self.klass, 'please configure a klass')
        self.assert_class_implements(self.klass, ISection)
        self.assert_class_provides(self.klass, ISectionBlueprint)

    def assert_class_implements(self, klass, interface):
        self.assertTrue(interface.implementedBy(klass),
                        'Class %s does not implement %s.' % (
                            str(klass), str(interface)))

        verifyClass(interface, klass)

    def assert_class_provides(self, klass, interface):
        self.assertTrue(interface.providedBy(klass),
                        'Class %s does not provide %s.' % (
                            str(klass), str(interface)))

        verifyObject(interface, klass)

    def assert_result(self, options, expected, input_data=None, klass=None):
        inserter = klass or self.klass
        input_data = input_data or self.input_data
        input_data = [input_data.copy()]
        source = inserter(TestTransmogrifier(), 'test', options, input_data)
        output = list(source)

        self.maxDiff = None
        self.assertEqual(output, expected)
