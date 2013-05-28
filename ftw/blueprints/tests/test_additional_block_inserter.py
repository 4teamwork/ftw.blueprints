from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from ftw.blueprints.sections import inserter
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class TestChildInserter(TestCase):

    def setUp(self):
        self.klass = inserter.ChildInserter
        
    def test_implements_interface(self):
        
        
        check_implements_on_class(self, self.klass, ISection)
        check_provides_on_class(self, self.klass, ISectionBlueprint)
    
    def test_default(self):
        expected = [
            self.get_expected_output(),
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {},
            },
        ]
        
        check_result(self, self.klass, 'default', expected)
        
    def test_condition(self):
        expected = [
            self.get_expected_output(),
        ]
        
        check_result(self, self.klass, 'condition_false', expected)
        
        
    def test_interfaces(self):
        expected = [
            self.get_expected_output(),
            {'_interfaces': ["ITest1", "ITest2"],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {},
            },
        ]
        
        check_result(self, self.klass, 'with_interfaces', expected)
        
    def test_annotations(self):
        expected = [
            self.get_expected_output(),
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_id': 'item',
             '_annotations': {"viewname": "portlet"},
            },
        ]
        
        check_result(self, self.klass, 'with_annotations', expected)
        
        
    def test_metadata(self):
        expected = [
            self.get_expected_output(),
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/bar/item',
             '_annotations': {},
             '_id': 'item',
             'title': 'bar',
            },
        ]
        
        check_result(self, self.klass, 'with_metadata', expected)

    def get_expected_output(self):
    
        return get_input()


class TestParentInserter(TestCase):
    
    def setUp(self):
        self.klass = inserter.ParentInserter
    
    def test_implements_interface(self):

        check_implements_on_class(self, self.klass, ISection)
        check_provides_on_class(self, self.klass, ISectionBlueprint)
    
    def test_default(self):
        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/item',
             '_id': 'item',
             '_annotations': {},
            },
            self.get_expected_output(),
        ]
        
        check_result(self, self.klass, 'default', expected)
        
    def test_condition(self):
        expected = [
            get_input(),
        ]
        
        check_result(self, self.klass, 'condition_false', expected)
        
        
    def test_interfaces(self):
        expected = [
            {'_interfaces': ["ITest1", "ITest2"],
             '_type': 'Page',
             '_path': '/foo/item',
             '_id': 'item',
             '_annotations': {},
            },
            self.get_expected_output(),
        ]
        
        check_result(self, self.klass, 'with_interfaces', expected)
        
    def test_annotations(self):
        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/item',
             '_id': 'item',
             '_annotations': {"viewname": "portlet"},
            },
            self.get_expected_output(),
        ]
        
        check_result(self, self.klass, 'with_annotations', expected)
        
        
    def test_metadata(self):
        expected = [
            {'_interfaces': [],
             '_type': 'Page',
             '_path': '/foo/item',
             '_annotations': {},
             '_id': 'item',
             'title': 'bar',
            },
            self.get_expected_output(),
        ]
        
        check_result(self, self.klass, 'with_metadata', expected)

    def get_expected_output(self):
        
        input_ = get_input()
        input_['_path'] = '/foo/item/bar'       
        return input_

def check_implements_on_class(context, klass, interface):

    context.assertTrue(interface.implementedBy(klass),
                    'Class %s does not implement %s.' % (
                        str(klass), str(interface)))

    verifyClass(interface, klass)
    
    
def check_provides_on_class(context, klass, interface):

    context.assertTrue(interface.providedBy(klass),
                    'Class %s does not provide %s.' % (
                        str(klass), str(interface)))

    verifyObject(interface, klass)

def check_result(context, inserter, options_name, expected):

    source = inserter(None, 'test', get_options(options_name), [get_input()])
    output = list(source)

    context.maxDiff = None
    context.assertEqual(output, expected)
    

def get_input():

    return {
        '_path': '/foo/bar',
        '_type': 'Folder',
        '_id': 'bar',
    }

    
def get_options(name):
    
    base_options = {
            'condition':'python:True',
            'content-type':'Page',
            'additional_id':'item',
            '_interfaces':'python:[]',
            '_annotations':'python:{}',
            'metadata-key':'python:{}'
        }
        
    if name is 'default':        
        return base_options
        
    elif name is 'condition_false':
        base_options.update({'condition': 'python:False'})
        return base_options
        
    elif name is 'with_interfaces':
        base_options.update(
            {'_interfaces': 'python:["ITest1", "ITest2"]'})
        return base_options
        
    elif name is 'with_annotations':
        base_options.update(
            {'_annotations': 'python:{"viewname": "portlet"}'})
        return base_options
        
    elif name is 'with_metadata':
        base_options.update(
            {'metadata-key': 'python:{"title": lambda item: item["_id"]}'})        
        return base_options

