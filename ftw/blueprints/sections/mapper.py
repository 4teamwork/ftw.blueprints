from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from zope.interface import classProvides, implements
import re


class RegexReplacer(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    """Replaces strings with regex:

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
        """The FieldMapper Blueprint provides powerful functionality to map and
        modify values on the given item.
        """
        self.mapper = Expression(
            options['field-mapping'], transmogrifier, name, options)

        self.condition = Condition(options.get('condition', 'python:True'),
            transmogrifier, name, options)

        self.previous = previous

    def __iter__(self):
        for item in self.previous:

            if not self.condition(item):
                yield item
                continue

            mapper = self.mapper(item)
            for src, dest in mapper.items():
                dest_name = dest.get('destination', None)
                transform_value = dest.get('transform', '')
                static_value = dest.get('static_value', '')
                map_value = dest.get('map_value', '')
                src_val = item.get(src, None)
                need_src_key = dest.get('need_src_key', False)

                if need_src_key and src_val is None:
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
