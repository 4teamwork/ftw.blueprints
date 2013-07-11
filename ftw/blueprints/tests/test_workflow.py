from ftw.blueprints.sections.workflow import map_workflow
from unittest2 import TestCase
from DateTime import DateTime


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
