from ftw.blueprints.sections.portlet import PortletHandler
from unittest2 import TestCase


class DummyAssignment(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs


DUMMY_ASSIGNMENT_PATH = 'ftw.blueprints.tests.test_portlet.DummyAssignment'

def properties(data=None, path=DUMMY_ASSIGNMENT_PATH):
    return {
        'class': path,
        '__dict__': data or {}}


class TestPortletHandlerAssignmentObject(TestCase):

    def test_get_instance_of_dummyassignment_class(self):
        assignment_obj = PortletHandler().get_assignment_object(properties())
        self.assertEquals(DummyAssignment, assignment_obj.__class__)

    def test_get_dummyassignment_without_properties(self):
        assignment_obj = PortletHandler().get_assignment_object(properties())
        self.assertEquals(assignment_obj.kwargs, {})

    def test_get_dummyassignent_with_a_property(self):
        assignment_obj = PortletHandler().get_assignment_object(
            properties(dict(title='Test')))
        self.assertEquals(assignment_obj.kwargs, {'title': 'Test'})

    def test_raise_importerror_if_the_path_to_assignment_class_does_not_exist(self):
        with self.assertRaises(ImportError) as err:
            PortletHandler().get_assignment_object(
                properties(path='ftw.blueprints.not-existing.path'))

        self.assertIn('not-existing', str(err.exception))
