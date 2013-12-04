from ftw.blueprints.sections.portlet import PortletHandler
from unittest2 import TestCase


class DummyAssignment(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs


DUMMY_ASSIGNMENT_PATH = 'ftw.blueprints.tests.test_portlet.DummyAssignment'


class TestPortletHandlerAssignmentObject(TestCase):

    def get_handler(self, path=DUMMY_ASSIGNMENT_PATH):
        return PortletHandler(
            'manager_name',
            path,
            'portlet_id')

    def test_get_instance_of_dummyassignment_class(self):
        handler = self.get_handler()
        assignment_obj = handler.get_assignment_object()
        self.assertEquals(DummyAssignment, assignment_obj.__class__)

    def test_get_dummyassignment_without_properties(self):
        handler = self.get_handler()
        assignment_obj = handler.get_assignment_object()
        self.assertEquals(assignment_obj.kwargs, {})

    def test_get_dummyassignent_with_a_property(self):
        handler = self.get_handler()
        assignment_obj = handler.get_assignment_object(dict(title='Test'))
        self.assertEquals(assignment_obj.kwargs, {'title': 'Test'})

    def test_raise_importerror_if_the_path_to_assignment_class_does_not_exist(self):
        handler = self.get_handler('ftw.blueprints.not-existing.path')

        with self.assertRaises(ImportError) as err:
            handler.get_assignment_object()

        self.assertIn('not-existing', str(err.exception))

    def test_raise_attributeerror_if_the_assignment_class_does_not_exist(self):
        handler = self.get_handler(
            'ftw.blueprints.tests.test_portlet.not-existing-class')

        with self.assertRaises(AttributeError) as err:
            handler.get_assignment_object()

        self.assertIn('not-existing-class', str(err.exception))
