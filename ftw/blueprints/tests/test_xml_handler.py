from ftw.blueprints.handlers import XMLHandler
from ftw.blueprints.interfaces import IXMLHandler
from unittest2 import TestCase
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from zope.interface.verify import verifyClass


TEST_XML = minidom.parseString("""
        <xml>
            <james>
                <bond title='\xc3\xa4gent'>007</bond>
            </james>
            <asterix>
                <bond title='hero'>Other \xc3\xa4gent</bond>
            </asterix>
        </xml>
    """)


class TestXMLHandlerClass(TestCase):

    def test_class_implements_ixmlhandler_interface(self):
        self.assertTrue(IXMLHandler.implementedBy(XMLHandler),
                        'Class %s does not implement %s.' % (
                            str(XMLHandler), str(IXMLHandler)))

        verifyClass(IXMLHandler, XMLHandler)


class TestParseXMLString(TestCase):

    def setUp(self):
        self.handler = XMLHandler()

    def test_returns_minidom_object(self):
        xml = self.handler.parse_xml_string('<james></james>')
        self.assertEquals(xml.__class__.__name__, 'Document')

    def test_functionality_with_unicode(self):
        xml = self.handler.parse_xml_string(u'<j\xe4mes></j\xe4mes>')

        self.assertIn(u'j\xe4mes', xml.firstChild.tagName)

    def test_functionality_with_utf_8(self):

        xml = self.handler.parse_xml_string(
            '<j\xc3\xa4mes></j\xc3\xa4mes>')

        self.assertIn(u'j\xe4mes', xml.firstChild.tagName)

    def test_error_message_with_invalid_xml_string(self):
        with self.assertRaises(ExpatError) as err:
            self.handler.parse_xml_string('bad_xml')
        self.assertIn('syntax error', str(err.exception))


class TestGetElements(TestCase):

    def setUp(self):
        self.handler = XMLHandler()

    def test_get_two_bond_elements_as_list(self):
        elements = self.handler.get_elements(TEST_XML, 'bond')
        self.assertIs(2, len(elements))

    def test_get_no_elements_in_empty_list(self):
        elements = self.handler.get_elements(TEST_XML, 'austin')
        self.assertIs(0, len(elements))


class TestGetFirstElement(TestCase):

    def setUp(self):
        self.handler = XMLHandler()

    def test_get_one_bond_element(self):
        element = self.handler.get_first_element(TEST_XML, 'bond')
        self.assertEquals('bond', element.tagName)

    def test_get_no_elements(self):
        element = self.handler.get_first_element(TEST_XML, 'austin')
        self.assertIs(None, element)


class TestGetElementValue(TestCase):

    def setUp(self):
        self.handler = XMLHandler()

    def test_get_007_when_asking_for_bond_tag(self):
        value = self.handler.get_element_value(TEST_XML, 'bond')
        self.assertEquals('007', value)

    def test_get_other_agent_when_asking_for_bond_tag_with_specified_xml(self):
        xml = self.handler.get_first_element(TEST_XML, 'asterix')
        value = self.handler.get_element_value(xml, 'bond')
        self.assertEquals(u'Other \xe4gent', value)

    def test_empty_string_when_no_elements_with_value(self):
        value = self.handler.get_element_value(TEST_XML, 'austin')
        self.assertEquals('', value)


class TestGetElementAttribute(TestCase):

    def setUp(self):
        self.handler = XMLHandler()

    def test_get_agent_when_asking_for_bond_title(self):
        value = self.handler.get_element_attribute_value(
            TEST_XML, 'bond', 'title')

        self.assertEquals(u'\xe4gent', value)

    def test_get_hero_when_asking_for_bond_tag_with_specified_xml(self):
        xml = self.handler.get_first_element(TEST_XML, 'asterix')
        value = self.handler.get_element_attribute_value(xml, 'bond', 'title')

        self.assertEquals('hero', value)

    def test_empty_string_when_attribute_doesnt_exist(self):
        value = self.handler.get_element_attribute_value(
            TEST_XML, 'bond', 'nothing')
        self.assertEquals('', value)

    def test_empty_string_when_element_doenst_exist(self):
        value = self.handler.get_element_attribute_value(
            TEST_XML, 'austin', 'title')
        self.assertEquals('', value)
