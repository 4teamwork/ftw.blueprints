from ftw.blueprints.sections import mapper
from ftw.blueprints.tests.base import BlueprintTestCase


INPUT = {
    '_path': '/foo/bar',
    '_type': 'Folder',
    '_id': 'bar',
    'title': 'test',
    }


class TestPathMapper(BlueprintTestCase):

    def setUp(self):
        self.klass = mapper.PathMapper
        self.input_data = INPUT

    def _get_options(self, additional_options=None):
        options = {'blueprint': 'ftw.blueprints.pathmapper'}
        if additional_options:
            options.update(additional_options)
        return options

    def test_map_value(self):
        expected = self._get_expected({'_path': '/qux/bar'})

        options = self._get_options(
            {'mapping': "python:( ('^/foo', '/qux'), )"}
        )
        self.assert_result(options, expected)

    def test_strip_prefixes(self):
        input_data = self.input_data.copy()
        input_data['_path'] = '/nininini' + input_data['_path']
        expected = self._get_expected({'_path': '/qux/bar'})

        options = self._get_options(
            {'mapping': 'python:( ("^/foo", "/qux"), )',
             'strip-prefixes': 'python: ["/nininini"]'}
        )
        self.assert_result(options, expected, input_data=input_data)

    def test_recursive_strip_prefixes(self):
        input_data = self.input_data.copy()
        input_data['_refs'] = {'one': '/prefix/foo/bar',
                               'two': '/prefix/foo/qux'}

        expected = self._get_expected({'_refs': {'one': '/qux/bar',
                                                 'two': '/qux/qux'}})

        options = self._get_options({
            'mapping': "python:( ('^/foo', '/qux'), )",
            'strip-prefixes': 'python: ["/prefix"]',
            'path-key': '_refs',
        })
        self.assert_result(options, expected, input_data=input_data)

    def test_map_order(self):
        expected = self._get_expected({'_path': '/qux/bar'})

        options = self._get_options(
            {'mapping': "python:("
                "('^/foo', '/qux'),"
                "('^/foo/bar', '/nix/nax'),"
             ")"}
        )
        self.assert_result(options, expected)

    def test_map_condition(self):
        expected = self._get_expected()

        options = self._get_options({
            'mapping': "python:( ('^/foo', '/qux'), )",
            'condition': 'python: False',
        })
        self.assert_result(options, expected)

    def test_recursive_path_mapping_list(self):
        input_data = self.input_data.copy()
        input_data['_refs'] = ['/foo/bar', '/foo/qux']

        expected = self._get_expected({'_refs': ['/qux/bar', '/qux/qux']})

        options = self._get_options({
            'mapping': "python:( ('^/foo', '/qux'), )",
            'path-key': '_refs',
        })
        self.assert_result(options, expected, input_data=input_data)

    def test_recursive_path_mapping_dict(self):
        input_data = self.input_data.copy()
        input_data['_refs'] = {'one': '/foo/bar', 'two': '/foo/qux'}

        expected = self._get_expected({'_refs': {'one': '/qux/bar',
                                                 'two': '/qux/qux'}})

        options = self._get_options({
            'mapping': "python:( ('^/foo', '/qux'), )",
            'path-key': '_refs',
        })
        self.assert_result(options, expected, input_data=input_data)

    def test_recursive_path_mapping_nested_list_in_dict(self):
        input_data = self.input_data.copy()
        input_data['_refs'] = {'hehe': ['/foo/bar', '/foo/hehe'],
                               'two': '/foo/qux'}

        expected = self._get_expected({'_refs': {'hehe': ['/qux/bar',
                                                          '/qux/hehe'],
                                                 'two': '/qux/qux'}})

        options = self._get_options({
            'mapping': "python:( ('^/foo', '/qux'), )",
            'path-key': '_refs',
        })
        self.assert_result(options, expected, input_data=input_data)
