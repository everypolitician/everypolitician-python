# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from os.path import dirname, join
import re
from unittest import TestCase

from mock import patch
import pytest
import six
from six import text_type

from everypolitician import EveryPolitician, NotFound
from popolo_data.importer import Popolo


class FakeResponse(object):

    def __init__(self, json_data, text, status_code):
        self.json_data = json_data
        self.text = text
        self.status_code = status_code

    def json(self):
        return self.json_data

    def text(self):
        return self.text

    def raise_for_status(self):
        pass


URL_DATA = {
    'https://raw.githubusercontent.com/everypolitician/everypolitician-data/master/countries.json':
    'example-countries.json',
    'https://raw.githubusercontent.com/everypolitician/everypolitician-data/ba00071/data/Argentina/Diputados/term-133.csv':
    'example-period.csv'
}


def fake_requests_get(url):
    leafname = URL_DATA.get(url)
    if not leafname:
        raise Exception("The URL {0} hasn't been faked".format(url))
    filename = join(dirname(__file__), 'test-data', leafname)
    if leafname.endswith('.json'):
        with open(filename) as f:
            return FakeResponse(json.load(f), None, 200)
    else:
        with open(filename, 'rb') as f:
            return FakeResponse(None, f.read().decode('utf-8'), 200)


@patch('everypolitician.lib.requests.get', side_effect=fake_requests_get)
class TestDataLoading(TestCase):

    def test_create_ep(self, patched_requests_get):
        ep = EveryPolitician()
        assert str(ep) == \
            '<EveryPolitician: https://raw.githubusercontent.com/everypolitician/everypolitician-data/master/countries.json>'

    def test_ep_repr(self, patched_requests_get):
        ep = EveryPolitician()
        assert repr(ep) == 'EveryPolitician()'

    def test_ep_repr_custom_url(self, patched_requests_get):
        ep = EveryPolitician(countries_json_url='foobar')
        assert repr(ep) == 'EveryPolitician(countries_json_url="foobar")'

    def test_ep_from_local_file(self, patched_requests_get):
        filename = join(
            dirname(__file__), 'test-data', 'example-countries.json')
        ep = EveryPolitician(countries_json_filename=filename)
        assert re.search(
            r'EveryPolitician\(countries_json_filename=".*example-countries.json"\)',
            repr(ep))

    def test_countries_from_local_file(self, patched_requests_get):
        filename = join(
            dirname(__file__), 'test-data', 'example-countries.json')
        ep = EveryPolitician(countries_json_filename=filename)
        countries = ep.countries()
        assert len(countries) == 2

    def test_countries(self, patched_requests_get):
        ep = EveryPolitician()
        countries = ep.countries()
        assert len(countries) == 2
        assert text_type(countries[0]) == '<Country: Åland>'
        assert text_type(countries[1]) == '<Country: Argentina>'

    def test_json_only_fetched_once(self, patched_requests_get):
        ep = EveryPolitician()
        ep.countries()
        ep.countries()
        assert patched_requests_get.call_count == 1

    def test_get_a_single_country_bad_case(self, patched_requests_get):
        ep = EveryPolitician()
        with pytest.raises(NotFound):
            ep.country('argentina')

    def test_get_a_single_country(self, patched_requests_get):
        ep = EveryPolitician()
        country = ep.country('Argentina')
        assert country.name == 'Argentina'

    def test_get_a_country_and_legislature(self, patched_requests_get):
        ep = EveryPolitician()
        country, legislature = ep.country_legislature('Argentina', 'Diputados')
        assert country.name == 'Argentina'
        assert legislature.name == 'Cámara de Diputados'

    def test_get_a_country_legislature_c_not_found(self, patched_requests_get):
        ep = EveryPolitician()
        with pytest.raises(NotFound):
            ep.country_legislature('Argentina', 'FOO')

    def test_get_a_country_legislature_l_not_found(self, patched_requests_get):
        ep = EveryPolitician()
        with pytest.raises(NotFound):
            ep.country_legislature('FOO', 'Diputados')

    def test_get_a_country_legislature_neither_found(self, patched_requests_get):
        ep = EveryPolitician()
        with pytest.raises(NotFound):
            ep.country_legislature('FOO', 'FOO')


class TestCountryMethods(TestCase):

    def setUp(self):
        with patch('everypolitician.lib.requests.get', side_effect=fake_requests_get):
            self.ep = EveryPolitician()
            self.country = self.ep.country('Aland')

    def test_country_repr(self):
        if six.PY2:
            assert repr(self.country) == b'<Country: \xc3\x85land>'
        else:
            assert repr(self.country) == '<Country: \xc5land>'

    def test_get_legislatures(self):
        ls = self.country.legislatures()
        assert len(ls) == 1


class TestLeglislatureMethods(TestCase):

    def setUp(self):
        with patch('everypolitician.lib.requests.get', side_effect=fake_requests_get):
            self.ep = EveryPolitician()
            self.country = self.ep.country('Argentina')
        self.legislatures = self.country.legislatures()

    def test_legislature_repr(self):
        if six.PY2:
            assert repr(self.legislatures[0]) == b'<Legislature: C\xc3\xa1mara de Diputados in Argentina>'
        else:
            assert repr(self.legislatures[1]) == '<Legislature: Cámara de Senadores in Argentina>'

    def test_legislature_str(self):
        assert text_type(self.legislatures[1]) == '<Legislature: Cámara de Senadores in Argentina>'

    def test_legislature_popolo_url(self):
        l = self.legislatures[1]
        assert l.popolo_url == 'https://cdn.rawgit.com/everypolitician/' \
            'everypolitician-data/25257c4/' \
            'data/Argentina/Senado/ep-popolo-v1.0.json'

    def test_directory(self):
        l = self.legislatures[0]
        assert l.directory() == 'Argentina/Diputados'

    @patch('everypolitician.lib.Popolo')
    def test_popolo_call(self, mocked_popolo_class):
        mocked_popolo_class.from_url.return_value = Popolo({
            'persons': [
                {'name': 'Joe Bloggs'}
            ]
        })
        l = self.legislatures[0]
        popolo = l.popolo()
        mocked_popolo_class.from_url.assert_called_with(
            u'https://cdn.rawgit.com/everypolitician/everypolitician-data/ba00071/data/Argentina/Diputados/ep-popolo-v1.0.json')
        assert len(popolo.persons) == 1
        assert popolo.persons.first.name == 'Joe Bloggs'


@patch('everypolitician.lib.requests.get', side_effect=fake_requests_get)
class TestLegislativePeriod(TestCase):

    def setUp(self):
        with patch('everypolitician.lib.requests.get', side_effect=fake_requests_get):
            self.ep = EveryPolitician()
            self.country = self.ep.country('Argentina')
            self.legislature = self.country.legislature('Diputados')
            self.period = self.legislature.legislative_periods()[0]

    def test_start_date(self, patched_requests_get):
        assert self.period.start_date == "2015"

    def test_end_date(self, patched_requests_get):
        assert self.period.end_date is None

    def test_csv(self, patched_requests_get):
        assert self.period.csv() == \
            [{u'area': u'BUENOS AIRES',
              u'area_id': u'area/buenos_aires',
              u'chamber': u'C\xe1mara de Diputados',
              u'email': u'asegarra@diputados.gob.ar',
              u'end_date': u'2015-12-09',
              u'facebook': u'',
              u'gender': u'female',
              u'group': u'FRENTE PARA LA VICTORIA - PJ',
              u'group_id': u'frente_para_la_victoria_-_pj',
              u'id': u'b882751f-4014-4f6f-b3cf-e0a5d6d3c605',
              u'image': u'http://www4.hcdn.gob.ar/fotos/asegarra.jpg',
              u'name': u'ADELA ROSA SEGARRA',
              u'sort_name': u'SEGARRA, ADELA ROSA',
              u'start_date': u'',
              u'term': u'133',
              u'twitter': u''},
             {u'area': u'BUENOS AIRES',
              u'area_id': u'area/buenos_aires',
              u'chamber': u'C\xe1mara de Diputados',
              u'email': u'aperez@diputados.gob.ar',
              u'end_date': u'',
              u'facebook': u'',
              u'gender': u'male',
              u'group': u'FRENTE RENOVADOR',
              u'group_id': u'frente_renovador',
              u'id': u'8efb1e0e-8454-4c6b-9f87-0d4fef875fd2',
              u'image': u'http://www4.hcdn.gob.ar/fotos/aperez.jpg',
              u'name': u'ADRIAN PEREZ',
              u'sort_name': u'PEREZ, ADRIAN',
              u'start_date': u'',
              u'term': u'133',
              u'twitter': u'adrianperezARG'}]
