rapido.core
===========

.. image:: https://secure.travis-ci.org/collective/rapido.core.png?branch=master
    :target: http://travis-ci.org/collective/rapido.core
    :alt: Tests
.. image:: https://landscape.io/github/collective/rapido.core/master/landscape.svg?style=flat
    :target: https://landscape.io/github/collective/rapido.core/master
    :alt: Code Health
.. image:: https://coveralls.io/repos/collective/rapido.core/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/collective/rapido.core?branch=master
    :alt: Coverage

rapido.core allows to run Rapido applications.

rapido.core can run on Zope or Pyramid. The initial target is Plone (using
`rapido.plone <https://github.com/collective/rapido.plone>`_), but a POC has been
successfully implemented on Substance D.

Database design
---------------

A Rapido application can be built from Plone using rapido.plone or provided from
sources (read from the local file system).

Anyhow, at the end, the database design is just a set of YAML/HTML/Python files.

The `rapido.plone documentation <http://rapidoplone.readthedocs.org/en/latest/>`_
gives a good overview of Rapido features.

Record storage
---------------

Storage is not handled directly by rapido.core.

By default, we use `rapido.souper <https://github.com/collective/rapido.souper>`_
which allows to store records in a `soup <https://pypi.python.org/pypi/souper>`_.

Using ZODB is not mandatory, different storages could be easily implemented
(SQL-based storage, remote storage services, etc.).
