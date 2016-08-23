from __future__ import unicode_literals

import csv
from datetime import datetime
import io

import requests
import six


DEFAULT_COUNTRIES_JSON_URL = \
    'https://raw.githubusercontent.com/everypolitician/' \
    'everypolitician-data/master/countries.json'


class NotFound(Exception):
    pass


@six.python_2_unicode_compatible
class EveryPolitician(object):

    def __init__(self, countries_json_url=None):
        if countries_json_url is None:
            countries_json_url = DEFAULT_COUNTRIES_JSON_URL
        self.countries_json_url = countries_json_url
        self._countries_json_data = None

    def countries_json_data(self):
        if self._countries_json_data is not None:
            return self._countries_json_data
        r = requests.get(self.countries_json_url)
        r.raise_for_status()
        self._countries_json_data = r.json()
        return self._countries_json_data

    def countries(self):
        return [
            Country(country_data) for country_data
            in self.countries_json_data()
        ]

    def country(self, country_slug):
        for c in self.countries():
            if c.slug == country_slug:
                return c
        raise NotFound("Couldn't find the country with slug '{0}'".format(
            country_slug))

    def country_legislature(self, country_slug, legislature_slug):
        country = self.country(country_slug)
        legislature = country.legislature(legislature_slug)
        return country, legislature

    def __repr__(self):
        if self.countries_json_url == DEFAULT_COUNTRIES_JSON_URL:
            return str('EveryPolitician()')
        fmt = str('EveryPolitician(countries_json_url="{}")')
        return fmt.format(self.countries_json_url)

    def __str__(self):
        return '<EveryPolitician: {0}>'.format(self.countries_json_url)


@six.python_2_unicode_compatible
class Country(object):

    def __init__(self, country_data):
        for k in ('name', 'code', 'slug'):
            setattr(self, k, country_data[k])
        self.country_data = country_data

    def legislatures(self):
        return [
            Legislature(legislature_data, self) for legislature_data
            in self.country_data['legislatures']
        ]

    def legislature(self, legislature_slug):
        for l in self.legislatures():
            if l.slug == legislature_slug:
                return l
        raise NotFound("Couldn't find the legislature with slug '{0}'".format(
            legislature_slug))

    def __repr__(self):
        fmt = str('<Country: {}>')
        if six.PY2:
            return fmt.format(self.name.encode('utf-8'))
        return fmt.format(self.name)

    def __str__(self):
        return '<Country: {0}>'.format(self.name)


@six.python_2_unicode_compatible
class Legislature(object):

    def __init__(self, legislature_data, country):
        for k in ('name', 'slug', 'person_count', 'sha', 'statement_count',
                  'popolo_url'):
            setattr(self, k, legislature_data[k])
        self.lastmod = datetime.utcfromtimestamp(
            float(legislature_data['lastmod']))
        self.legislature_data = legislature_data
        self.country = country

    # TODO: when we've done everypolitician-popolo, add a 'popolo'
    # method to return data parsed from self.popolo_url.

    def directory(self):
        split_path = self.legislature_data['sources_directory'].split('/')
        return '/'.join(split_path[1:3])

    def legislative_periods(self):
        return [
            LegislativePeriod(lp_data, self, self.country)
            for lp_data in self.legislature_data['legislative_periods']
        ]

    def __repr__(self):
        fmt = str('<Legislature: {0} in {1}>')
        if six.PY2:
            return fmt.format(
                self.name.encode('utf-8'), self.country.name.encode('utf-8'))
        return fmt.format(self.name, self.country.name)

    def __str__(self):
        return '<Legislature: {0} in {1}>' \
            .format(self.name, self.country.name)


def unicode_dict(d):
    return { k.decode('utf-8'): v.decode('utf-8') for k, v in d.items() }


class LegislativePeriod(object):

    def __init__(self, legislative_period_data, legislature, country):
        for k in ('id', 'name', 'slug'):
            setattr(self, k, legislative_period_data[k])
        self.legislature = legislature
        self.country = country
        self.legislative_period_data = legislative_period_data

    @property
    def start_date(self):
        return self.legislative_period_data.get('start_date')

    @property
    def end_date(self):
        return self.legislative_period_data.get('end_date')

    @property
    def csv_url(self):
        return 'https://raw.githubusercontent.com/everypolitician' \
            '/everypolitician-data/{0}/{1}'.format(
                self.legislature.sha,
                self.legislative_period_data['csv']
            )

    def csv(self):
        r = requests.get(self.csv_url)
        r.raise_for_status()
        if six.PY2:
            f = io.BytesIO(r.text.encode('utf-8'))
            reader = csv.DictReader(f)
            return [
                unicode_dict(d) for d in reader
            ]
        else:
            f = io.StringIO(r.text)
            reader = csv.DictReader(f)
            return [d for d in reader]