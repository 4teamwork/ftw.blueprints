from zope.interface import Interface
from zope.interface import Attribute


class IXMLHandler(Interface):
    """
    """

    def parse_xml_string(xml_string):
        """
        """

    def get_elements(xml, name):
        """
        """

    def get_first_element(xml, name):
        """
        """

    def get_element_value(element):
        """
        """

    def get_element_attribute_value(element, attribute):
        """
        """


class IPFM2PFGConverter(Interface):
    """
    """

    def __init__(item, xml_string):
        """
        """

    def __iter__():
        """
        """

    def end_group(xml):
        """
        """

    def begin_group(xml):
        """
        """

    def get_pfg_field(field):
        """
        """


class IFormGenField(Interface):
    """
    """
    # form_type = Attribute("""Defines the portal_type of the FormGenField""")

    def __init__(field):
        """
        """

    def fill_field():
        """
        """
