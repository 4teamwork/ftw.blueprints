from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from DateTime import DateTime
from zope.component import queryUtility
from zope.interface import classProvides, implements
from ftw.blueprints.interfaces import IFormGenField
from ftw.blueprints.interfaces import IPFM2PFGConverter
from ftw.blueprints.handlers import XMLHandler


class PFM2PFGConverter(object):
    implements(IPFM2PFGConverter)


    def __init__(self, item, xml_string):
        """
        """
        self.handler = XMLHandler()
        self.item = item
        self.xml_string = xml_string

    def __iter__(self):
        """
        """
        for group in self.handler.get_elements(
            self.handler.parse_xml_string(self.xml_string),
            'group'):

            yield self.begin_group(group)

            for field in self.handler.get_elements(group, 'field'):

                yield self.get_pfg_field(field)

            yield self.end_group(group)

    def get_pfg_field(self, field):
        """
        """
        pfm_type = self.handler.get_element_value(field, 'type')

        field_utility = self.get_field_utility(pfm_type)
        if not field_utility:
            raise

        return field_utility(field, self.item)

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

        item['_id'] = '%s-end' % title
        item['_type'] = 'FieldsetEnd'
        item['_path'] = '%s/%s-stop' % (self.item['_path'], title)

        return item

    def begin_group(self, xml):

        item = {}

        title = self.handler.get_element_value(xml, 'title')

        if title == 'Default':
            return item

        item['_id'] = '%s-start' % title
        item['_type'] = 'FieldsetStart'
        item['_path'] = '%s/%s-start' % (self.item['_path'], title)
        item['title'] = title

        return item


class FormGenField(dict):
    """
    """
    implements(IFormGenField)

    form_type = None

    def __init__(self, field, item):

        self.handler = XMLHandler()
        self.field = field
        self.item = item

        self.fill_field

    @property
    def fill_field(self):

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def _get_filtered_element_value(self, name):

        value = self.handler.get_element_value(self.field, name)
        type_ = self.handler.get_element_attribute_value(self.field, name, 'type')

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

        return value

    def get_path(self):
        self['_path'] = '%s/%s' % (
            self.item['_path'], self._get_filtered_element_value('id'))

    def get_id(self):
        self['_id'] = self._get_filtered_element_value('id')

    def get_type(self):
        self['_type'] = self.form_type

    def get_title(self):
        self['title'] = self._get_filtered_element_value('title')

    def get_required(self):
        self['required'] = self._get_filtered_element_value('required')

    def get_description(self):
        self['description'] = self._get_filtered_element_value('description')

    def get_hidden(self):
        self['hidden'] = self._get_filtered_element_value('hidden')

    def get_default(self):
        self['fgDefault'] = self._get_filtered_element_value('default')


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

    def get_fgVocabulary(self):
        value = self._get_filtered_element_value('items')
        self['fgVocabulary'] = [key for key, val in value]

    def get_default(self):
        value = self._get_filtered_element_value('default')

        if value:
            self['fgDefault'] = value

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


class FormMultiSelectionField(FormSelectionField):
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


class FormMultiSelectionFieldCheckbox(FormMultiSelectionField):
    """
    """
    classProvides(IFormGenField)

    def get_fgFormat(self):
        self['fgFormat'] = 'checkbox'


class FormMailerFieldsInserter(object):
    classProvides(ISectionBlueprint)
    implements(ISection)


    def __init__(self, transmogrifier, name, options, previous):
        self.context = transmogrifier.context
        self.previous = previous

    def __iter__(self):

        # Save item-paths for cleanups after migration
        item_paths = []

        for item in self.previous:

            item_paths.append(item['_path'])

            # Returns the FormFolder
            yield item

            # After we handle the form fields
            form_data = item.get('form_data')

            if not form_data:
                yield item
                continue

            pfmxmlhandler = PFM2PFGConverter(item, form_data)

            for field in pfmxmlhandler:
                yield field

        for path in item_paths:
            folder = self.context.unrestrictedTraverse(
                            str(path).lstrip('/'), None)

            if not folder:
                continue

            folder._delObject('replyto')
            folder._delObject('topic')
            folder._delObject('comments')
            folder.reindexObject()
            import transaction
            transaction.commit()