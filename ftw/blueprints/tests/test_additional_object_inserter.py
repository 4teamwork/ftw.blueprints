from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from ftw.blueprints.sections import inserter
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


INPUT = {
    '_path': '/foo/bar',
    '_type': 'Folder',
    '_id': 'bar',
    'title': 'test',
    }


class ObjectInserter(TestCase):

    def setUp(self):
        self.klass = inserter.AdditionalObjectInserter

    def test_implements_interface(self):
        check_implements_on_class(self, self.klass, ISection)
        check_provides_on_class(self, self.klass, ISectionBlueprint)

    def test_insert_object_at_a_given_path(self):

        options = {
            'content-type': 'Page',
            'additional-id': 'string:item',
            'new-path':'python:"/foo/given/path"'
            }

        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/given/path',
             '_id': 'item',
             '_annotations': {}},
             INPUT,
        ]

        assert_result(self, self.klass, options, expected)

class TestChildInserter(TestCase):

    def setUp(self):
        self.klass = inserter.ChildInserter

    def test_implements_interface(self):
        check_implements_on_class(self, self.klass, ISection)
        check_provides_on_class(self, self.klass, ISectionBlueprint)

    def test_blueprint_with_default_settings(self):
        expected = [
            INPUT,
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {}},
        ]

        assert_result(self, self.klass, get_options(), expected)

    def test_blueprint_with_condition_false(self):
        expected = [
            INPUT,
        ]

        assert_result(self, self.klass, get_options(
            condition='python:False'), expected)

    def test_blueprint_with_additional_interfaces(self):
        expected = [
            INPUT,
            {'_interfaces': ["ITest1", "ITest2"],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {}},
        ]

        assert_result(self, self.klass, get_options(
            interfaces='python:["ITest1", "ITest2"]'), expected)

    def test_blueprint_with_additional_annotations(self):
        expected = [
            INPUT,
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {"viewname": "portlet"}},
        ]

        assert_result(self, self.klass, get_options(
                annotations='python:{"viewname": "portlet"}'), expected)

    def test_blueprint_with_additional_metadata(self):
        expected = [
            INPUT,
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_annotations': {},
             '_id': 'item',
             'title': 'bar'},
        ]

        assert_result(self, self.klass, get_options(
            metadata='python:{"title": lambda item: item["_id"]}'), expected)


class TestParentInserter(TestCase):

    def setUp(self):
        self.klass = inserter.ParentInserter

    def test_implements_interface(self):

        check_implements_on_class(self, self.klass, ISection)
        check_provides_on_class(self, self.klass, ISectionBlueprint)

    def test_blueprint_with_default_settings(self):
        expected = [
            {'_interfaces': [],
             '_path': '/foo/item',
             '_type': 'Page',
             '_id': 'item',
             '_annotations': {}},
            self.get_expected_output(),
        ]

        assert_result(self, self.klass, get_options(), expected)

    def test_blueprint_with_condition_false(self):
        expected = [
            INPUT,
        ]

        assert_result(self, self.klass, get_options(
            condition='python:False'), expected)

    def test_blueprint_with_additional_interfaces(self):
        expected = [
            {'_interfaces': ["ITest1", "ITest2"],
             '_path': '/foo/item',
             '_type': 'Page',
             '_id': 'item',
             '_annotations': {}},
            self.get_expected_output(),
        ]

        assert_result(self, self.klass, get_options(
            interfaces='python:["ITest1", "ITest2"]'), expected)

    def test_blueprint_with_additional_annotations(self):
        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/item',
             '_id': 'item',
             '_annotations': {"viewname": "portlet"}},
            self.get_expected_output(),
        ]

        assert_result(self, self.klass, get_options(
                annotations='python:{"viewname": "portlet"}'), expected)

    def test_blueprint_with_additional_metadata(self):
        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/item',
             '_annotations': {},
             '_id': 'item',
             'title': 'bar'},
            self.get_expected_output(),
        ]

        assert_result(self, self.klass, get_options(
            metadata='python:{"title": lambda item: item["_id"]}'), expected)

    def get_expected_output(self):
        input_ = INPUT.copy()
        input_['_path'] = '/foo/item/bar'
        return input_


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
    context.assertEqual(output, expected)


def get_options(
    content_type="Page",
    additional_id="string:item",
    condition=None,
    interfaces=None,
    annotations=None,
    metadata=None):

    options = {
        'content-type': content_type,
        'additional-id': additional_id,
        }

    if condition:
        options.update({'condition': condition})

    if interfaces:
        options.update({'_interfaces': interfaces})

    if annotations:
        options.update({'_annotations': annotations})

    if metadata:
        options.update({'metadata-key': metadata})

    return options
