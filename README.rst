rapido.core
===========

|travisstatus|_

.. |travisstatus| image:: https://secure.travis-ci.org/plomino/rapido.core.png?branch=master
.. _travisstatus:  http://travis-ci.org/plomino/rapido.core

rapido.core allows to run a Rapido application.

rapido.core can run different ZODB-enabled servers (Zope/Plone or Pyramid).

Database design
---------------

A Rapido application can be built from Plone using rapido.plone or provided from
sources (read from the local file system or downloaded from a remote server).

Anyhow, at the end, the database design is just a set of YAML/HTML/Python files:
i.e. YAML metadata that defines properties about a block but links to separate
layout.html and good naming conventions, making clear the relation between YAML
metadata and layout/formula files.

It's probably better to have one .py file per block, rather than many small ones
per formula. That also makes it tempting for such a .py file to have a shared
section that is global to all the formulas in that file.

Record storage
---------------

Storage is not handled directly by rapido.core.
By default, we use rapido.souper which allows to store records in a soup.
But a different storage could be implemented if needed.

A separate storage mechanism will be needed for attached files.
