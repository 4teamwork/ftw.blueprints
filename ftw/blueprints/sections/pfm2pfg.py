from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from DateTime import DateTime
from ftw.blueprints.handlers import XMLHandler
from ftw.blueprints.interfaces import IFormGenField
from ftw.blueprints.interfaces import IPFM2PFGConverter
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import classProvides, implements


class PFM2PFGConverter(object):
    implements(IPFM2PFGConverter)

    def __init__(self, item, xml_string):

        self.handler = XMLHandler()
        self.item = item
        self.xml_string = xml_string
        self.normalizer = getUtility(IIDNormalizer)

    def __iter__(self):

        xml = self.handler.parse_xml_string(self.xml_string)

        for group in self.handler.get_elements(xml, 'group'):

            yield self.begin_group(group)

            for field in self.handler.get_elements(group, 'field'):

                yield self.get_pfg_field(field)

            yield self.end_group(group)

    def get_pfg_field(self, field):

        pfm_type = self.handler.get_element_value(field, 'type')

        field_utility = self.get_field_utility(pfm_type)
        if not field_utility:
            raise

        pfg_field = field_utility(field, self.item)
        pfg_field.fill_field()

        return pfg_field

    def get_field_utility(self, type_):
        """Returns the assosiated utility for pfg fields
        """

        return queryUtility(
            IFormGenField,
            'ftw.blueprints.pfm2pfg.%s' % type_)

    def end_group(self, xml):

        item = {}

        title = self.handler.get_element_value(xml, 'title')

        if title == 'Default':
            return item

        title = self.normalizer.normalize(title)

        item['_id'] = '%s-end' % title
        item['_type'] = 'FieldsetEnd'
        item['_path'] = '%s/%s-stop' % (self.item['_path'], title)

        return item

    def begin_group(self, xml):

        item = {}

        title = self.handler.get_element_value(xml, 'title')

        if title == 'Default':
            return item

        item['title'] = title

        title = self.normalizer.normalize(title)

        item['_id'] = '%s-start' % title
        item['_type'] = 'FieldsetStart'
        item['_path'] = '%s/%s-start' % (self.item['_path'], title)

        return item


class FormGenField(dict):
    implements(IFormGenField)

    form_type = None

    def __init__(self, field, item):

        self.handler = XMLHandler()
        self.field = field
        self.item = item

    def fill_field(self):

        for method in dir(self):
            if method.startswith('set_'):
                getattr(self, method)()

    def _get_filtered_element_value(self, name):

        value = self.handler.get_element_value(self.field, name)
        type_ = self.handler.get_element_attribute_value(
            self.field, name, 'type')

        if type_ == 'float':
            return float(value)

        elif type_ == 'int':
            if name in ['enabled', 'required', 'hidden']:
                return bool(int(value))
            return int(value)

        elif type_ == 'list':
            return eval(value)

        elif type_ == 'datetime':
            return DateTime(value)

        if isinstance(value, unicode):
            return value.encode('utf-8')
        else:
            return value

    def set_path(self):
        self['_path'] = '%s/%s' % (
            self.item['_path'], self._get_filtered_element_value('id'))

    def set_id(self):
        self['_id'] = self._get_filtered_element_value('id')

    def set_type(self):
        self['_type'] = self.form_type

    def set_title(self):
        self['title'] = self._get_filtered_element_value('title')

    def set_required(self):
        self['required'] = self._get_filtered_element_value('required')

    def set_description(self):
        self['description'] = self._get_filtered_element_value('description')

    def set_hidden(self):
        self['hidden'] = self._get_filtered_element_value('hidden')

    def set_default(self):
        self['fgDefault'] = self._get_filtered_element_value('default')


class FormStringField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormStringField'


class FormTextField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormTextField'


class FormPasswordField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormPasswordField'


class FormRichLabelField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormRichLabelField'


class FormIntegerField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormIntegerField'


class FormFixedPointField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormFixedPointField'


class FormDateField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormDateField'


class FormFileField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormFileField'


class FormLinesField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormLinesField'


class FormBooleanField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormBooleanField'


class FormStringFieldEmail(FormStringField):
    classProvides(IFormGenField)

    def set_fg_string_validator(self):
        self['fgStringValidator'] = 'isEmail'


class FormStringFieldURL(FormStringField):
    classProvides(IFormGenField)

    def set_fg_string_validator(self):
        self['fgStringValidator'] = 'isURL'


class FormSelectionField(FormGenField):
    classProvides(IFormGenField)

    form_type = 'FormSelectionField'

    def set_fg_vocabulary(self):
        value = self._get_filtered_element_value('items')
        self['fgVocabulary'] = [key for key, val in value]

    def set_default(self):
        value = self._get_filtered_element_value('default')

        if value:
            self['fgDefault'] = value


class FormSelectionFieldSelect(FormSelectionField):
    classProvides(IFormGenField)

    def set_fg_format(self):
        self['fgFormat'] = 'select'


class FormSelectionFieldRadio(FormSelectionField):
    classProvides(IFormGenField)

    def set_fg_format(self):
        self['fgFormat'] = 'radio'


class FormMultiSelectionField(FormSelectionField):
    classProvides(IFormGenField)

    form_type = 'FormMultiSelectionField'


class FormMultiSelectionFieldSelect(FormMultiSelectionField):
    classProvides(IFormGenField)

    def set_fg_format(self):
        self['fgFormat'] = 'select'


class FormMultiSelectionFieldCheckbox(FormMultiSelectionField):
    classProvides(IFormGenField)

    def set_fg_format(self):
        self['fgFormat'] = 'checkbox'


class FormMailerFieldsInserter(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.context = transmogrifier.context
        self.previous = previous

    def __iter__(self):

        for item in self.previous:

            # Returns the FormFolder
            yield item

            # Cleanup the auto-created fields before adding the fields
            self.cleanup(item['_path'])

            # After cleanup, we handle the form fields
            form_data = item.get('form_data')

            if not form_data:
                yield item
                continue

            converter = PFM2PFGConverter(item, form_data)

            for field in converter:
                yield field

    def cleanup(self, path):

        to_remove = ['replyto', 'topic', 'comments']

        folder = self.context.unrestrictedTraverse(
                            str(path).lstrip('/'), None)

        if not folder:
            return

        for field in to_remove:
            if not hasattr(folder, field):
                continue

            folder._delObject(field)

        folder.reindexObject()
