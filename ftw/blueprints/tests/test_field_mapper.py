from ftw.blueprints.sections import mapper
from ftw.blueprints.tests.base import BlueprintTestCase


INPUT = {
    '_path': '/foo/bar',
    '_type': 'Folder',
    '_id': 'bar',
    'title': 'test',
    }


class TestFieldMapper(BlueprintTestCase):

    def setUp(self):
        self.klass = mapper.FieldMapper
        self.input_data = INPUT

    def test_do_no_changes(self):
        expected = self._get_expected()
        self.assert_result({'field-mapping': "python:{}"}, expected)

    def test_change_destination_name(self):
        expected = self._get_expected({'new-title': INPUT.get('title')})

        options = {
            'field-mapping': "python:{'title' :{'destination': 'new-title'}}"}

        self.assert_result(options, expected)

    def test_transform_value(self):
        expected = self._get_expected({'_id': 'test1'})

        options = {'field-mapping':
            "python:{'_id': {'transform': lambda x: '%s1' % x['title']}}"
            }

        self.assert_result(options, expected)

    def test_add_static_value(self):
        expected = self._get_expected({'_id': 'static_id'})

        options = {'field-mapping':
            "python:{'_id': {'static_value': 'static_id'}}"
            }

        self.assert_result(options, expected)

    def test_map_value(self):
        expected = self._get_expected({'title': 'mapped_title'})

        options = {'field-mapping':
            "python:{'title': {'map_value': {'test': 'mapped_title'}}}"
            }

        self.assert_result(options, expected)

    def test_add_new_item_without_src_key(self):
        expected = self._get_expected({'james': 'bond'})

        options = {'field-mapping':
            "python:{'xxx': {'destination': 'james', 'static_value': 'bond',}}"
            }

        self.assert_result(options, expected)

    def test_no_changes_on_item_when_need_src_key(self):
        expected = self._get_expected()

        options = {'field-mapping':
            "python:{'xxx': {'destination': 'james', " + \
            "'static_value': 'bond', 'need_src_key': True}}"
            }

        self.assert_result(options, expected)

    def test_change_destination_do_transform_and_map_value_on_same_item(self):
        expected = self._get_expected({'james': 'bond'})

        options = {'field-mapping':
            "python:{'xxx': {'destination': 'james', " + \
            "'transform': lambda x: x['_id'], 'map_value': {'bar': 'bond'}}}"
            }

        self.assert_result(options, expected)

    def test_multiple_changes_on_item(self):
        expected = self._get_expected({
            'title': 'static_title',
            '_id': 'bond',
            'reference': INPUT.get('_path'),
            })

        options = {'field-mapping':
            "python:{'title': {'static_value': 'static_title'}, " + \
            "'_id': {'map_value': {'bar': 'bond'}}, " + \
            "'_path': {'destination': 'reference'}}"
            }

        self.assert_result(options, expected)

    def test_do_no_changes_if_condition_is_false(self):
        expected = self._get_expected()

        options = {
            'field-mapping':
            "python:{'_id': {'static_value': 'static_id'}}",
            'condition': 'python:False'
            }

        self.assert_result(options, expected)
