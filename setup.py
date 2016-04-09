from setuptools import setup, find_packages
import os

version = '1.0.6.dev0'

setup(name='rapido.core',
      version=version,
      description="Rapid application builder",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='rapido',
      author='Eric BREHAULT',
      author_email='ebrehault@gmail.com',
      url='https://github.com/plomino/rapido.core',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rapido'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyaml',
          'zope.security',
          'zope.configuration',
          'zope.untrustedpython',
      ],
      extras_require={
        'test': [
            'plone.app.testing',
            'rapido.souper',
        ],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
