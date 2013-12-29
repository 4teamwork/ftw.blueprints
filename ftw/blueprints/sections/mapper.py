from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from collective.transmogrifier.utils import defaultMatcher
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


class PathMapper(object):
    """Maps old paths to new paths.

    Applices recursive mapping if the path at pathkey is a dict. Applies
    mapping for each element if path at pathkey is another iterable.

    All prefixes configured in strip_prefixes will be removed from the
    path.

    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.condition = Condition(options.get('condition', 'python:True'),
                                   transmogrifier, name, options)
        self.strip_prefixes = Expression(options.get('strip-prefixes',
                                                     'python: []'),
                                         transmogrifier, name, options)
        self.mapping = Expression(options['mapping'],
                                  transmogrifier, name, options)
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')

    def _apply_mapping(self, strip_prefixes, mapping, path):
        for each in strip_prefixes:
            if path.startswith(each):
                path = path.replace(each, '', 1)
        for pattern, repl in mapping:
            path = re.sub(pattern, repl, path)
        return path

    def _apply_mapping_recursively(self, strip_prefixes, mapping,
                                   item, pathkey, path):
        if isinstance(path, dict):
            for key, value in path.items():
                self._apply_mapping_recursively(strip_prefixes, mapping,
                                                path, key, value)
        elif hasattr(path, '__iter__'):
            item[pathkey] = list(self._apply_mapping(strip_prefixes,
                                                     mapping, each)
                                 for each in path)
        else:
            item[pathkey] = self._apply_mapping(strip_prefixes, mapping, path)

    def __iter__(self):
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]

            if not pathkey:
                yield item
                continue

            path = item[pathkey]
            if not self.condition(item, key=path):
                yield item
                continue

            mapping = self.mapping(item)
            strip_prefixes = self.strip_prefixes(item)
            self._apply_mapping_recursively(strip_prefixes, mapping,
                                            item, pathkey, path)
            yield item


class TypeFieldMapper(object):
    """Map types and their fields to new types and new fields.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.mapping = Expression(options['mapping'],
                                  transmogrifier, name, options)
        self.typekey = defaultMatcher(options, 'type-key', name, 'type')

    def __iter__(self):
        for item in self.previous:
            keys = item.keys()
            typekey = self.typekey(*keys)[0]

            if not typekey:
                yield item
                continue

            old_type = item[typekey]
            type_mappings = self.mapping(item)
            if old_type in type_mappings:
                new_type, field_mappings = type_mappings[old_type]
                item[typekey] = new_type

                for old_field, new_field in field_mappings.items():
                    if old_field in keys:
                        item[new_field] = item[old_field]
                        if new_field != old_field:
                            del item[old_field]

            yield item
