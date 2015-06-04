from DateTime import DateTime
from ftw.blueprints.sections.workflow import map_workflow
from ftw.blueprints.sections.workflow import PlacefulWorkflowImporter
from ftw.blueprints.testing import BLUEPRINT_FUNCTIONAL_TESTING
from ftw.blueprints.tests.base import BlueprintTestCase
from ftw.blueprints.tests.utils import TestTransmogrifier
from ftw.builder import Builder
from ftw.builder import create
from plone.app.testing.helpers import setRoles
from plone.app.testing.interfaces import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


WORKFLOW_HISTORY = {'test-workflow':[
    {'action': 'submit',
     'actor': 'james.bond',
     'comments': 'test-entry',
     'review_state': 'published',
     'time': DateTime(), },
    {'action': 'reject',
     'actor': 'bruce.willis',
     'comments': '',
     'review_state': 'pending',
     'time': DateTime(), }
     ]}


class TestMapWorkflow(TestCase):

    def test_input_and_output_workflows_are_equal_when_no_mapping_is_given(self):
        workflow = map_workflow(
            'test-workflow', 'test-workflow', WORKFLOW_HISTORY)

        self.assertEquals(workflow, WORKFLOW_HISTORY)

    def test_maps_history_to_the_new_workflow_id(self):
        workflow = map_workflow(
            'test-workflow', 'other-workflow', WORKFLOW_HISTORY)

        self.assertEquals(
            workflow,
            {'other-workflow': WORKFLOW_HISTORY.get('test-workflow')})

    def test_all_states_are_mapped_with_the_given_state_map(self):
        workflow = map_workflow(
            'test-workflow', 'test-workflow', WORKFLOW_HISTORY, state_map={
                'pending':'waiting',
                'published':'free',
            })

        self.assertEquals(
            [transition.get('review_state') for transition in \
                workflow.get('test-workflow')],
            ['free', 'waiting'])

    def test_all_transitions_are_mapped_with_the_given_transition_map(self):
        workflow = map_workflow(
            'test-workflow', 'test-workflow', WORKFLOW_HISTORY, transition_map={
                'submit':'send',
                'reject':'delete',
            })

        self.assertEquals(
            [transition.get('action') for transition in \
                workflow.get('test-workflow')],
            ['send', 'delete'])

    def test_returns_only_last_history_item_when_updating_history_is_deactivated(self):
        workflow = map_workflow(
            'test-workflow', 'test-workflow',
            WORKFLOW_HISTORY,
            update_history=False)

        self.assertEquals(
            workflow,
            {'test-workflow': [WORKFLOW_HISTORY.get('test-workflow')[-1]]})

    def test_no_workflow_whith_the_given_workflow_id_found(self):
        workflow = map_workflow(
            'no-workflow', 'no-workflow',
            WORKFLOW_HISTORY, )

        self.assertEquals(workflow, None)


class TestPlacefulWorklfow(BlueprintTestCase):
    layer = BLUEPRINT_FUNCTIONAL_TESTING
    klass = PlacefulWorkflowImporter

    def setUp(self):
        super(TestPlacefulWorklfow, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_placeful_workfow_is_applied(self):
        obj = create(Builder('folder').titled('folder'))

        self.run_transmogrifier([{'_path': 'folder',
                                  '_placeful_workflow_config':
                                  ['test_in', 'test_below']}])

        plc_workflow = getToolByName(obj, 'portal_placeful_workflow')
        config = plc_workflow.getWorkflowPolicyConfig(obj)

        self.assertEquals('test_in', config.workflow_policy_in)
        self.assertEquals('test_below', config.workflow_policy_below)

    def run_transmogrifier(self, items):
        transmogrifier = TestTransmogrifier()
        transmogrifier.context = self.portal
        options = {'blueprint': 'ftw.blueprints.placefulworkflowimporter'}
        source = self.klass(transmogrifier, 'test', options, items)
        return list(source)
