from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from DateTime import DateTime
from xml.dom import minidom
from zope.component import queryUtility
from zope.interface import classProvides, implements
from zope.interface import Interface


class PfmXMLHandler(object):

    def __init__(self, item, xml_string):
        """
        """

        if isinstance(xml_string, unicode):
            xml_string = xml_string.encode('utf-8')

        self.item = item
        self.xml = minidom.parseString(xml_string)
        self.groups = self.get_elements('group', self.xml)
        # self.fields = self.get_elements('field', self.xml)
        self.field = None

    def __iter__(self):

        for group in self.groups:

            yield self.begin_group(group)

            for field in self.get_elements('field', group):

                self.field = field

                field_utility = self.get_field_utility(field)
                if not field_utility:
                    raise

                yield field_utility(self)

            yield self.end_group(group)

    def end_group(self, xml):

        item = {}

        title = self.get_element_value('title', xml)

        if title == 'Default':
            return item

        item['_id'] = '%s-end' % self.get_element_value('title', xml)
        item['_type'] = 'FieldsetEnd'
        item['_path'] = '%s/%s-stop' % (
                self.item['_path'], self.get_element_value('title', xml))

        return item

    def begin_group(self, xml):

        item = {}

        title = self.get_element_value('title', xml)

        if title == 'Default':
            return item

        item['_id'] = '%s-start' % self.get_element_value('title', xml)
        item['_type'] = 'FieldsetStart'
        item['_path'] = '%s/%s-start' % (
                self.item['_path'], self.get_element_value('title', xml))
        item['title'] = title
        import pdb; pdb.set_trace( )
        return item

    def get_elements(self, name, xml):
        return xml.getElementsByTagName(name)

    def get_first_element(self, name, xml):
        elements = self.get_elements(name, xml)

        if elements:
            return elements[0]
        return None

    def get_element_value(self, name, xml):
        value = self._get_element_value(name, xml)
        return self._filter_element_value(name, value, xml)

    def get_element_attribute(self, name, attribute, xml):
        element = self.get_first_element(name, xml)

        if not element:
            return ''

        return element.getAttribute(attribute)

    def _get_element_value(self, name, xml):

        element = self.get_first_element(name, xml)

        if not element:
            return ''

        childs = element.childNodes

        if not childs:
            return ''

        return childs[0].data

    def _filter_element_value(self, name, value, xml):

        type_ = self.get_element_attribute(name, 'type', xml)

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

    def get_field_utility(self, field):
        """Returns the assosiated utility for pfg fields
        """

        return queryUtility(
            IFormGenField,
            'ftw.blueprints.pfm2pfg.%s' % self.get_element_value(
                'type', self.field))


class IFormGenField(Interface):
    """
    """


class FormGenField(dict):
    """
    """
    classProvides(IFormGenField)

    form_type = None

    def __init__(self, pfmxmlhandler):

        self.handler = pfmxmlhandler
        self.field = self.handler.field

        for method in dir(self):
            if method.startswith('get_'):
                getattr(self, method)()

    def get_path(self):
        self['_path'] = '%s/%s' % (
            self.handler.item['_path'], self.handler.get_element_value('id', self.field))

    def get_id(self):
        self['_id'] = self.handler.get_element_value('id', self.field)

    def get_type(self):
        self['_type'] = self.form_type

    def get_title(self):
        self['title'] = self.handler.get_element_value('title', self.field)

    def get_required(self):
        self['required'] = self.handler.get_element_value('required', self.field)

    def get_description(self):
        self['description'] = self.handler.get_element_value('description', self.field)

    def get_hidden(self):
        self['hidden'] = self.handler.get_element_value('hidden', self.field)

    def get_default(self):
        self['fgDefault'] = self.handler.get_element_value('default', self.field)


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
        value = self.handler.get_element_value('items', self.field)
        self['fgVocabulary'] = [key for key, val in value]

    def get_default(self):
        value = self.handler.get_element_value('default', self.field)

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

            pfmxmlhandler = PfmXMLHandler(item, form_data)

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