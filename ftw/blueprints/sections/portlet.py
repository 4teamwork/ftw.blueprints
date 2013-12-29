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


class PortletHandler(object):

    def __init__(self, manager_name, assignment_path, portlet_id):
        self.manager_name = manager_name
        self.portlet_id = portlet_id
        self.assignment_path = assignment_path

    def __call__(self, context, properties=None):
        properties = properties or {}
        manager = getUtility(IPortletManager, name=self.manager_name)
        assignment_mapping = getMultiAdapter(
            (context, manager), IPortletAssignmentMapping)

        # Set new portlet assignment
        if self.portlet_id in assignment_mapping:
            return

        assignment_mapping[self.portlet_id] = self.get_assignment_object(
            properties)

    def get_assignment_object(self, properties=None):
        """Return the assignment object of the defined portlet
        """
        properties = properties or {}
        assignment_class = self._get_assignment_class(self.assignment_path)

        return assignment_class(**properties)

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

        self.portlet_properties = Expression(
            options.get('portlet-properties', 'python:{}'),
            transmogrifier, name, options)

        self.condition = Condition(options.get('condition', 'python:True'),
            transmogrifier, name, options)

        self.portlet_handler = PortletHandler(
            options.get('manager-name'),
            options.get('assignment-path'),
            options.get('portlet-id')
        )

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

            self.portlet_handler(obj, self.portlet_properties(item))

            self.logger.info(
                "Added portlet at %s" % (item[self.pathkey]))
