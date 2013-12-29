from Testing.ZopeTestCase.utils import setupCoreSessions
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class BlueprintLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        import ftw.blueprints
        xmlconfig.file('configure.zcml', ftw.blueprints,
                       context=configurationContext)

        import plone.dexterity
        xmlconfig.file('configure.zcml', plone.dexterity,
                       context=configurationContext)

        import plone.app.dexterity
        xmlconfig.file('configure.zcml', plone.app.dexterity,
                       context=configurationContext)

        import plone.app.multilingual
        xmlconfig.file('configure.zcml', plone.app.multilingual,
                       context=configurationContext)

        setupCoreSessions(app)


BLUEPRINT_FIXTURE = BlueprintLayer()
BLUEPRINT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BLUEPRINT_FIXTURE, ), name="ftw.blueprints:Integration")
BLUEPRINT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BLUEPRINT_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.blueprints:Functional")
