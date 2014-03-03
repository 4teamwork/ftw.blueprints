from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from collective.transmogrifier.utils import traverse
from DateTime import DateTime
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from zope.interface import classProvides, implements


def map_workflow(old_workflow_id, new_workflow_id,
    workflow_history,
    state_map={},
    transition_map={},
    update_history=True):

    old_workflow = workflow_history.get(old_workflow_id, [])

    if not old_workflow:
        return None

    if not update_history:
        # The last element of the wf-history contains the current
        # review-state informations.
        old_workflow = [old_workflow[-1]]

    new_workflow = {new_workflow_id: []}
    for transition in old_workflow:

        action = transition_map.get(
            transition.get('action'), transition.get('action'))

        review_state = state_map.get(
            transition.get('review_state'),
            transition.get('review_state'))

        new_workflow[new_workflow_id].append(
            dict(
                action=action,
                actor=transition.get('actor'),
                comments=transition.get('comments'),
                review_state=review_state,
                time=DateTime(transition.get('time'))
            )
        )

    return new_workflow


class WorkflowManager(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, 'portal_workflow')

        self.pathkey = options.get('path-key', '_path')
        self.history_key = options.get('history-key', '_workflow_history')
        self.state_key = options.get('state-key', '_review_state')

        self.update_history = options.get('update-history', True)

        self.old_workflow_id = options.get('old-workflow-id')
        self.new_workflow_id = options.get(
            'new-workflow-id', self.old_workflow_id)

        self.state_map = Expression(
            options.get('state-map', 'python:{}'),
            transmogrifier, name, options)
        self.transition_map = Expression(
            options.get('transition-map', 'python:{}'),
            transmogrifier, name, options)

        self.condition = Condition(options.get('condition', 'python:True'),
            transmogrifier, name, options)

    def __iter__(self):
        for item in self.previous:
            if not self.condition(item):
                yield item
                continue

            obj = traverse(self.context, item.get(self.pathkey, ''))
            if not obj or not IBaseObject.providedBy(obj) or not hasattr(
                obj, 'workflow_history'):
                yield item
                continue

            new_workflow_history = map_workflow(
                self.old_workflow_id,
                self.new_workflow_id,
                item.get(self.history_key, {}),
                self.state_map(item),
                self.transition_map(item),
                self.update_history)

            if new_workflow_history:
                self.set_workflow_on_obj(obj, new_workflow_history)

            yield item

    def set_workflow_on_obj(self, obj, workflow_history):
        obj.workflow_history.clear()
        obj.workflow_history.update(workflow_history)
        workflows = self.wftool.getWorkflowsFor(obj)
        if workflows:
            workflows[0].updateRoleMappingsFor(obj)
