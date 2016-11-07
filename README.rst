EveryPolitician
===============

A Python library for easy access to EveryPolitician data. This is
essentially a Python port of
`everypolitican-ruby <https://github.com/everypolitician/everypolitician-ruby>`__.

This has been tested with Python 2.7 and Python 3.5.

Installation
============

You can install this package from PyPi with:

.. code:: bash

    pip install everypolitician

Usage
=====

Creating a instance of the ``EveryPolitican`` class allows you to access
information on countries, their legislatures and legislative periods.
Each country and legislature has a slug that can be used to reference
them via the ``country`` and ``legislature`` methods:

.. code:: python

    from everypolitician import EveryPolitician
    ep = EveryPolitician()

    australia = ep.country('Australia')
    senate = australia.legislature('Senate')
    senate # => <Legislature: Senate in Australia>

    united_kingdom = ep.country('UK')
    house_of_commons = united_kingdom.legislature('Commons')

    american_samoa = ep.country('American-Samoa')
    house_of_representatives = american_samoa.legislature('House')

    for country in ep.countries():
        print country.name, 'has', len(country.legislatures()), 'legislatures'

By default this will get the EveryPolitician data and returns the most
recent data. This data is found from the index file, called
``countries.json``, which links to specific versions of other data
files.

If you want want to point to a different ``countries.json`` file, you
can override the default URL by specifying the ``countries_json_url``
keyword argument when creating the ``EveryPolitician`` object, e.g.:

.. code:: python

    EveryPolitician(countries_json_url='https://cdn.rawgit.com/everypolitician/everypolitician-data/080cb46/countries.json')

The example above is using a specific commit (indicated by the hash
``080cb46``). If you want to use a local copy of ``countries.json`` you
can create the object with the ``countries_json_filename`` keyword
argument instead, e.g.:

.. code:: python

    EveryPolitician(countries_json_filename='/home/mark/tmp/countries.json')

For more about ``countries.json``, see `this
description <http://docs.everypolitician.org/repo_structure.html>`__.

Remember that EveryPolitician data is frequently updated — see this
information about `using EveryPolitician
data <http://docs.everypolitician.org/use_the_data.html>`__.

More information on `the EveryPolitician
site <http://docs.everypolitician.org/>`__.

Development
-----------

After cloning the repo, you can run the tests on Python 2.7 and Python
3.5 by running:

.. code:: bash

    tox

Or you can create a virtualenv and install the package's dependencies
with:

.. code:: bash

    pip install -e .

And run the tests on the Python version your virtualenv was based on
with:

pytest

Contributing
------------

Bug reports and pull requests are welcome on GitHub at
https://github.com/everypolitician/everypolitician.

License
-------

The gem is available as open source under the terms of the `MIT
License <http://opensource.org/licenses/MIT>`__.
