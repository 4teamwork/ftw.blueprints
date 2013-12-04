from ftw.blueprints.sections import encapsulator
from ftw.blueprints.tests.base import BlueprintTestCase
from ftw.blueprints.tests.utils import TestTransmogrifier


INPUT = {
    '_path': '/bar',
    '_type': 'TextBlock',
    '_id': 'bar',
    'text': 'foo',
    '_content_type_text': 'text/plain'
    }


class TestEncapsulator(BlueprintTestCase):

    def setUp(self):
        self.klass = encapsulator.UnicodeAwareMimeEncapsulator
        self.options = {
            'blueprint': 'ftw.blueprints.unicodeawaremimeencapsulator',
            'data-key': 'text',
            'mimetype': "python:item.get('_content_type_%s' % key)",
            'field': 'key',
        }
        self.input_data = INPUT.copy()

    def test_str_encapsulating(self):
        source = self.klass(TestTransmogrifier(), 'test',
                            self.options, [self.input_data])
        output = iter(source).next()
        self.assertEqual('text/plain', output['text'].getContentType())

    def test_unicode_encapsulating(self):
        self.input_data['text'] = u'foo'

        source = self.klass(TestTransmogrifier(), 'test',
                            self.options, [self.input_data])
        output = iter(source).next()
        self.assertEqual('text/plain', output['text'].getContentType())
