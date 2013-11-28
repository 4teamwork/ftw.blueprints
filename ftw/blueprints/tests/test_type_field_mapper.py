from ftw.blueprints.sections import mapper
from ftw.blueprints.tests.base import BlueprintTestCase


INPUT = {
    '_path': '/foo/bar',
    '_type': 'Folder',
    '_id': 'bar',
    'title': 'test',
    }


class TestTypeFieldMapper(BlueprintTestCase):

    def setUp(self):
        self.klass = mapper.TypeFieldMapper
        self.input_data = INPUT

    def _get_options(self, additional_options=None):
        options = {'blueprint': 'ftw.blueprints.typefieldmapper'}
        if additional_options:
            options.update(additional_options)
        return options

    def test_map_value(self):
        expected = self._get_expected({'_type': 'QuxFolder'})

        options = self._get_options({
            'mapping': "python: {'Folder':  ('QuxFolder', {}),}",
        })
        self.assert_result(options, expected)

    def test_map_attribute(self):
        expected = INPUT.copy()
        expected['_type'] = 'QuxFolder'
        expected['ho'] = expected['title']
        del expected['title']

        options = self._get_options({
            'mapping': "python: {'Folder':  ('QuxFolder', {'title': 'ho'}),}",
        })
        self.assert_result(options, [expected])
