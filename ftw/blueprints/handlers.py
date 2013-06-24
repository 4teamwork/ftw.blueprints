from ftw.blueprints.interfaces import IXMLHandler
from zope.interface import implements
from xml.dom import minidom


class XMLHandler(object):
    implements(IXMLHandler)

    def parse_xml_string(self, xml_string):

        if isinstance(xml_string, unicode):
            xml_string = xml_string.encode('utf-8')

        return minidom.parseString(xml_string)

    def get_elements(self, xml, name):
        return xml.getElementsByTagName(name)

    def get_first_element(self, xml, name):
        elements = self.get_elements(xml, name)

        if elements:
            return elements[0]
        return None

    def get_element_value(self, xml, element_name):

        element = self.get_first_element(xml, element_name)

        if not element:
            return ''

        children = element.childNodes

        if not children:
            return ''

        return children[0].data

    def get_element_attribute_value(self, xml, element_name, attribute_name):

        element = self.get_first_element(xml, element_name)

        if not element:
            return ''

        return element.getAttribute(attribute_name)
