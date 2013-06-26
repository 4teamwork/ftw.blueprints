from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from ftw.blueprints.sections import mapper
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


INPUT = {
    '_path': '/foo/bar',
    '_type': 'Folder',
    '_id': 'bar',
    'title': 'test',
    }


class TestFieldMapper(TestCase):

    def setUp(self):
        self.klass = mapper.FieldMapper

    def test_implements_interface(self):
        check_implements_on_class(self, self.klass, ISection)
        check_provides_on_class(self, self.klass, ISectionBlueprint)

    def test_do_no_changes(self):

        expected = INPUT.copy()
        assert_result(
            self,
            self.klass,
            {'field-mapping': "python:{}"},
            expected)

    def test_change_destination_name(self):

        expected = INPUT.copy()
        expected.update({'new-title': INPUT.get('title')})

        options = {
            'field-mapping': "python:{'title' :{'destination': 'new-title'}}"}

        assert_result(self, self.klass, options, expected)

    def test_transform_value(self):

        expected = INPUT.copy()
        expected.update({'_id': 'test1'})

        options = {'field-mapping':
            "python:{'_id': {'transform': lambda x: '%s1' % x['title']}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_add_static_value(self):

        expected = INPUT.copy()
        expected.update({'_id': 'static_id'})

        options = {'field-mapping':
            "python:{'_id': {'static_value': 'static_id'}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_map_value(self):

        expected = INPUT.copy()
        expected.update({'title': 'mapped_title'})

        options = {'field-mapping':
            "python:{'title': {'map_value': {'test': 'mapped_title'}}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_add_new_item_without_src_key(self):

        expected = INPUT.copy()
        expected.update({'james': 'bond'})

        options = {'field-mapping':
            "python:{'xxx': {'destination': 'james', 'static_value': 'bond',}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_no_changes_on_item_when_need_src_key(self):

        expected = INPUT.copy()

        options = {'field-mapping':
            "python:{'xxx': {'destination': 'james', " + \
            "'static_value': 'bond', 'need_src_key': True}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_change_destination_do_transform_and_map_value_on_same_item(self):

        expected = INPUT.copy()
        expected.update({'james': 'bond'})

        options = {'field-mapping':
            "python:{'xxx': {'destination': 'james', " + \
            "'transform': lambda x: x['_id'], 'map_value': {'bar': 'bond'}}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_multiple_changes_on_item(self):

        expected = INPUT.copy()
        expected.update({
            'title': 'static_title',
            '_id': 'bond',
            'reference': INPUT.get('_path'),
            })

        options = {'field-mapping':
            "python:{'title': {'static_value': 'static_title'}, " + \
            "'_id': {'map_value': {'bar': 'bond'}}, " + \
            "'_path': {'destination': 'reference'}}"
            }

        assert_result(self, self.klass, options, expected)

    def test_do_no_changes_if_condition_is_false(self):
        expected = INPUT.copy()

        options = {
            'field-mapping':
            "python:{'_id': {'static_value': 'static_id'}}",
            'condition': 'python:False'
            }

        assert_result(self, self.klass, options, expected)


def check_implements_on_class(context, klass, interface):

    context.assertTrue(interface.implementedBy(klass),
                    'Class %s does not implement %s.' % (
                        str(klass), str(interface)))

    verifyClass(interface, klass)


def check_provides_on_class(context, klass, interface):

    context.assertTrue(interface.providedBy(klass),
                    'Class %s does not provide %s.' % (
                        str(klass), str(interface)))

    verifyObject(interface, klass)


def assert_result(context, inserter, options, expected):

    source = inserter(None, 'test', options, [INPUT.copy()])
    output = list(source)

    context.maxDiff = None
    context.assertEqual(output, [expected])

