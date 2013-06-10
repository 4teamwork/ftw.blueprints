from zope.interface import Interface


class IXMLHandler(Interface):
    """Provides useful methods to handle xml data with minidom
    """

    def parse_xml_string(xml_string):
        """Parses a xml string with minidom
        """

    def get_elements(xml, name):
        """Return the given elements
        """

    def get_first_element(xml, name):
        """Return the first found element
        """

    def get_element_value(xml, element_name):
        """Returns the value of the given element name
        """

    def get_element_attribute_value(xml, element_name, attribute_name):
        """Returns the attribute value of the given attribute name from the
        given element name
        """


class IPFM2PFGConverter(Interface):
    """Converts a old PloneFormMailer formular into a new PloneFormGen
    """

    def __init__(item, xml_string):
        """
        """

    def __iter__():
        """Returns the FormFields as a dict
        """

    def end_group(xml):
        """End of a fieldgroup
        """

    def begin_group(xml):
        """Begin of a fieldgroup
        """

    def get_pfg_field(field):
        """Returns the PloneFormGen Field as a dict
        """


class IFormGenField(Interface):
    """PloneFormGen representation dict object
    """

    def __init__(field):
        """
        """

    def fill_field():
        """Fills the dict with its values
        """
