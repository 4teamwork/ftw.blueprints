from ftw.blueprints.sections import inserter
from ftw.blueprints.tests.base import BlueprintTestCase


INPUT = {
    '_path': '/foo/bar',
    '_type': 'Folder',
    '_id': 'bar',
    'title': 'test',
    }


class ObjectInserter(BlueprintTestCase):

    def setUp(self):
        self.klass = inserter.AdditionalObjectInserter
        self.input_data = INPUT

    def test_insert_object_at_a_given_path(self):

        options = {
            'content-type': 'Page',
            'additional-id': 'string:item',
            'new-path': 'python:"/foo/given/path"'
            }

        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/given/path',
             '_id': 'item',
             '_annotations': {}},
             INPUT,
        ]

        self.assert_result(options, expected)


class TestChildInserter(BlueprintTestCase):

    def setUp(self):
        self.klass = inserter.ChildInserter
        self.input_data = INPUT

    def test_blueprint_with_default_settings(self):
        expected = [
            INPUT,
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {}},
        ]

        self.assert_result(get_options(), expected)

    def test_blueprint_with_condition_false(self):
        expected = [
            INPUT,
        ]

        self.assert_result(get_options(
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

        self.assert_result(get_options(
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

        self.assert_result(get_options(
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

        self.assert_result(get_options(
            metadata='python:{"title": lambda item: item["_id"]}'), expected)


class TestParentInserter(BlueprintTestCase):

    def setUp(self):
        self.klass = inserter.ParentInserter
        self.input_data = INPUT

    def test_blueprint_with_default_settings(self):
        expected = [
            {'_interfaces': [],
             '_path': '/foo/item',
             '_type': 'Page',
             '_id': 'item',
             '_annotations': {}},
            self.get_expected_output(),
        ]

        self.assert_result(get_options(), expected)

    def test_blueprint_with_condition_false(self):
        expected = [
            INPUT,
        ]

        self.assert_result(get_options(
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

        self.assert_result(get_options(
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

        self.assert_result(get_options(
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

        self.assert_result(get_options(
            metadata='python:{"title": lambda item: item["_id"]}'), expected)

    def get_expected_output(self):
        input_ = INPUT.copy()
        input_['_path'] = '/foo/item/bar'
        return input_


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
