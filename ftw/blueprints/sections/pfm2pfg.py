from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from Products.CMFCore.utils import getToolByName
from ftw.blueprints.sections.inserter import AdditionalObjectInserter

from zope.component import getUtility
from zope.interface import Interface
from xml.dom import minidom


class IFormGenField(Interface):
    """
    """


class FormGenField(dict):
    """
    """
    classProvides(IFormGenField)

    form_type = None

    def __init__(self, field_xml, item):

        self.field_xml = field_xml
        self.item = item
        self.id_ = self.field_xml.getElementsByTagName(
            'id')[0].childNodes[0].data

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()


    def get_path(self):
        self['_path'] = '%s/%s' % (self.item['_path'], self.id_)

    def get_id(self):
        self['_id'] = self.id_

    def get_type(self):
        self['_type'] = self.form_type

    def get_title(self):
        self['title'] = self.field_xml.getElementsByTagName(
            'title')[0].childNodes[0].data

class FormStringField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormStringField'


class FormTextField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormTextField'


class FormPasswordField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormPasswordField'


class FormRichLabelField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormRichLabelField'


class FormIntegerField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormIntegerField'


class FormFixedPointField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormFixedPointField'

class FormDateField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormDateField'


class FormFileField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormFileField'


class FormLinesField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormLinesField'


class FormBooleanField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormBooleanField'


class FormStringFieldEmail(FormStringField):
    """
    """
    classProvides(IFormGenField)

    def get_fgStringValidator(self):
        self['fgStringValidator'] = 'isEmail'


class FormStringFieldURL(FormStringField):
    """
    """
    classProvides(IFormGenField)

    def get_fgStringValidator(self):
        self['fgStringValidator'] = 'isURL'


class FormSelectionField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormSelectionField'


class FormSelectionFieldSelect(FormSelectionField):
    """
    """
    classProvides(IFormGenField)

    def get_fgFormat(self):
        self['fgFormat'] = 'select'


class FormSelectionFieldRadio(FormSelectionField):
    """
    """
    classProvides(IFormGenField)

    def get_fgFormat(self):
        self['fgFormat'] = 'radio'


class FormMultiSelectionField(FormGenField):
    """
    """
    classProvides(IFormGenField)

    form_type = 'FormMultiSelectionField'


class FormMultiSelectionFieldSelect(FormMultiSelectionField):
    """
    """
    classProvides(IFormGenField)

    def get_fgFormat(self):
        self['fgFormat'] = 'select'


class FormMultiSelectionFieldRadio(FormMultiSelectionField):
    """
    """
    classProvides(IFormGenField)

    def get_fgFormat(self):
        self['fgFormat'] = 'radio'


class FormMailerFieldsInserter(object):
    classProvides(ISectionBlueprint)
    implements(ISection)


    def __init__(self, transmogrifier, name, options, previous):
        self.context = transmogrifier.context
        self.previous = previous

    def __iter__(self):

        for item in self.previous:

            form_data = item.get('form_data')

            if not form_data:
                yield item
                continue

            if isinstance(form_data, unicode):
                form_data = form_data.encode('utf-8')

            xml = minidom.parseString(form_data)
            fields = xml.getElementsByTagName('field')

            items = []

            for field in fields:
                field_id = field.getElementsByTagName(
                    'type')[0].childNodes[0].data

                formgenfield = getUtility(
                    IFormGenField,
                    'ftw.blueprints.pfm2pfg.%s' % field_id)

                items.append(formgenfield(field, item))
            import pdb; pdb.set_trace( )
            yield item
            for item in items:
                yield item