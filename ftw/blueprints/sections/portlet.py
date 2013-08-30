from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from collective.transmogrifier.utils import traverse
from importlib import import_module
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import classProvides, implements
import logging
from zope.dottedname.resolve import resolve

class PortletHandler(object):


    def __call__(self, context, properties=None):
        properties = properties or {}
        manager = getUtility(IPortletManager, name=properties['manager'])
        assignment_mapping = getMultiAdapter(
            (context, manager), IPortletAssignmentMapping)

        # Set new portlet assignment
        name = properties['__dict__']['__name__']
        del properties['__dict__']['__name__']

        if name in assignment_mapping:
            return

        assignment_mapping[name] = self.get_assignment_object(
            properties)

    def get_assignment_object(self, properties=None):
        """Return the assignment object of the defined portlet
        """
        properties = properties or {}
        class_ = properties['class']
        if class_ == 'ftw.portlet.staticTextExtended.static.Assignment':
            class_ = 'plone.portlet.static.static.Assignment'
            del properties['__dict__']['hide']
            del properties['__dict__']['show_title']
            del properties['__dict__']['actual_context']

        assignment_class = resolve(class_)
        return assignment_class(**properties['__dict__'])

    def _get_assignment_class(self, assignment_path):
        """Try to import and return the defined assignment class
        """
        path_elements = assignment_path.split('.')

        module = import_module('.'.join(path_elements[:-1]))
        assignment_class_name = path_elements[-1]

        return getattr(module, assignment_class_name)


class ContextualPortletAdder(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.logger = logging.getLogger(options['blueprint'])

        self.pathkey = options.get('path-key', '_path')

        self.condition = Condition(options.get('condition', 'python:True'),
            transmogrifier, name, options)

        self.portlet_handler = PortletHandler()

    def __iter__(self):
        for item in self.previous:
            if not self.condition(item):
                yield item
                continue

            obj = traverse(self.context, item.get(self.pathkey, ''))

            if not obj:
                self.logger.warn(
                    "Context does not exist at %s" % item.get[self.pathkey])
                yield item
                continue
            for portlet in item['portlets']:
                self.portlet_handler(obj, portlet)

            self.logger.info(
                "Added portlet at %s" % (item[self.pathkey]))
