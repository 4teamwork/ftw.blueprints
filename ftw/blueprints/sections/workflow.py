from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import Expression
from collective.transmogrifier.utils import defaultMatcher
from zope.interface import classProvides, implements


class ParentWorkflowMapper(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.path_key = options.get('pathkey', '_path')
        self.state_key = options.get('state-key', '_review_state')
        self.wftool = getToolByName(self.context, 'portal_workflow')
        self.condition = Condition(
            options.get('condition'), transmogrifier, name, options)

    def __iter__(self):

        for item in self.previous:
            if self.condition(item):
                path = item[self.path_key]
                path = '/'.join(path.split('/')[:-1])
                parent = self.context.unrestrictedTraverse(
                    str(path).lstrip('/'), None)

                if parent is None:
                    yield item
                    continue

                while not IPloneSiteRoot.providedBy(parent):
                    if len(self.wftool.getWorkflowsFor(parent)):
                        item[self.state_key] = self.wftool.getInfoFor(
                            parent, 'review_state')
                        break

                    parent = aq_parent(aq_inner(parent))

            yield item


class WorkflowUpdater(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, 'portal_workflow')
        self.mtool = getToolByName(self.context, 'portal_membership')

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.statekey = defaultMatcher(options, 'state-key', name,
                                             'state')

    def __iter__(self):
        for item in self.previous:
            current_user_id = self.mtool.getAuthenticatedMember().getId()
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            statekey = self.statekey(*keys)[0]

            if not (pathkey and statekey):  # not enough info
                yield item
                continue

            path, state = item[pathkey], item[statekey]

            obj = self.context.unrestrictedTraverse(path.lstrip('/'), None)
            if obj is None:                      # path doesn't exist
                yield item
                continue

            try:
                wf_ids = self.wftool.getChainFor(obj)
                if wf_ids:
                    wf_id = wf_ids[0]
                    comment = 'Set dossier state upon import.'
                    self.wftool.setStatusOf(wf_id, obj, {
                            'review_state': state,
                            'action': state,
                            'actor': current_user_id,
                            'time': DateTime(),
                            'comments': comment})

                    wfs = {wf_id: self.wftool.getWorkflowById(wf_id)}
                    self.wftool._recursiveUpdateRoleMappings(obj, wfs)
                    obj.reindexObjectSecurity()

            except WorkflowException:
                pass

            yield item


class WorkflowMapper(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.wf_history_key = options.get('wf-history-key')
        self.state_key = options.get('state-key')
        self.state_map = Expression(
            options['state-map'], transmogrifier, name, options)
        self.wf_id = Expression(
            options['wf-id'], transmogrifier, name, options)
        self.previous = previous

    def __iter__(self):
        for item in self.previous:
            state_map = self.state_map(item)
            wf_id = self.wf_id(item)
            wf_history = item.get(self.wf_history_key, [])

            if wf_history and wf_history.get(wf_id):
                last_action = wf_history.get(wf_id)[-1]
                review_state = last_action.get('review_state')
                item[self.state_key] = state_map.get(
                    review_state, review_state)

            yield item
