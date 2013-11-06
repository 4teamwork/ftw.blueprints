from setuptools import setup, find_packages
import os

version = '1.0.dev0'

tests_require = [
    'unittest2',
    'ftw.testing',
    'zope.configuration',
    'plone.testing',
    'plone.app.testing',
    ]


setup(name='ftw.blueprints',
      version=version,
      description="Provides useful blueprints for migrations with " + \
          "transmogrifier",
      long_description=open('README.rst').read() + '\n' + \
          open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.blueprints',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.jsonmigrator',
          'collective.transmogrifier >= 1.5',
          'collective.blueprint.translationlinker',
          'ftw.inflator',
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
