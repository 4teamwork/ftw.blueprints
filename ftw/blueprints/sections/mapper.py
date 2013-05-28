from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from zope.interface import classProvides, implements
import re


class RegexReplacer(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    """
    Replaces strings with regex:

    [insert-table-class]
    blueprint = ftw.blueprints.regexreplacer
    key = string:text
    pattern = python: r'<table[^>]*>'
    repl = python: '<table class="listing">'
    condition = python: item.get('_type') == 'TextBlock'
    """
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.key = Expression(options['key'], transmogrifier, name, options)
        self.pattern = Expression(
            options['pattern'], transmogrifier, name, options)
        self.repl = Expression(options['repl'], transmogrifier, name, options)
        self.condition = Condition(options.get('condition', 'python:True'),
                                   transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:
            if self.condition(item):
                key = self.key(item)
                if item.get(key):
                    item[key] = re.sub(
                        self.pattern(item), self.repl(item), item.get(key))

            yield item


class FieldMapper(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        """
        The FieldMapper Blueprint provides basic functionality to map and
        modify values on the given item.

        - First, you need to define the source-id you want to modifiy.
        - Then you need to define some options:

          - destination: the new name of the key.
              {'plz': {'destination':'zip'}
            just moves the value of plz to zip

          - static_value: if you want to use a static value, you can use this
            option:
              {'plz': {'static_value':'3000'}}
            replaces the value in plz with 3000

          - map_value: in some cases you want to change the values with a map:
              {'plz': {'map_value':{'PLZ 3000': '3000'}}}
            if the value of plz is PLZ 3000, it will be replaced with 3000

          - transform: transforms the value with the given function.
            As parameter, you have the item itself.
              {'plz': {'transform':lambda x: x['plz'] = x['plz'] and \
                  x['plz'] or '3000'}}
            this example would replace the plz with 3000 if its value is None

          - need_src_key: in some cases you just want to do transforms if the
            source-key is available.
              {'plz': 'static_value':'3000', need_src_key: True}
            it would just set the static value if the source-key already
            exists.

        You can combine all this options together to do powerful mappings
        on your item.

        	{
            'plz': {'static_value':'3000'},
            'client': {
        		'destination': 'text',
                'transform': lambda x: x['language'] == \
                'en' and 'Customer: %s' % (x['cleint']) or \
                'Kunde: %s' % (x['client']),
        		'need_src_val': True}
            }
            If the client-key is available in the items-map, it fills a given
            string, depending on the language of the object into the text
            attribute.
        """
        self.mapper = Expression(
            options['field-mapping'], transmogrifier, name, options)

        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:
            mapper = self.mapper(item)
            for src, dest in mapper.items():
                dest_name = dest.get('destination', None)
                transform_value = dest.get('transform', '')
                static_value = dest.get('static_value', '')
                map_value = dest.get('map_value', '')
                src_val = item.get(src, '')
                need_src_key = dest.get('need_src_key', False)

                if need_src_key and not src_val:
                    continue

                if not dest_name:
                    dest_name = src

                if static_value:
                    item[dest_name] = static_value
                    continue

                if transform_value:
                    if callable(transform_value):
                        src_val = transform_value(item)

                if map_value:
                    src_val = map_value.get(src_val, src_val)

                item[dest_name] = src_val

            yield item
