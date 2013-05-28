from setuptools import setup, find_packages
import os

version = open('ftw/blueprints/version.txt').read().strip()
maintainer = 'Elio Schmutz'

tests_require = [
    'unittest2',
    'ftw.testing',
    'zope.configuration',
    'plone.testing',
    'plone.app.testing',
    ]


setup(name='ftw.blueprints',
      version=version,
      description="Package ftw.blueprints (Maintainer: %s)" % maintainer,
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='',
      maintainer=maintainer,
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.jsonmigrator',
          'collective.blueprint.translationlinker',
          'ftw.inflator'
          # -*- Extra requirements: -*-
      ],
      
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
