import csv
import json
import os.path
from unittest import mock

import pytest
import requests

from generate_csv import filter_departures, generate_endpoint, get_departures, main


class Dummy:
    pass


def load_departures():
    with open('departures.json', 'r') as f:
        data = json.load(f)

    return data


def generate_mock_response():
    mock_response = Dummy()
    departures = load_departures()

    mock_response.json = lambda: {
        'next': None,
        'results': departures,
    }
    return mock_response


def test_generate_endpoint():
    custom_kwargs = {
        'hostname': 'example.com',
        'port': '8080',
        'api': 'test',
        'protocol': 'https',
    }
    assert generate_endpoint() == 'http://127.0.0.1:8000/departures'
    assert generate_endpoint(**custom_kwargs) == 'https://example.com:8080/test'


def test_filter_departures():
    category = 'Adventurous'
    start_date = '2018-06-01'
    data = load_departures()

    filtered_data = filter_departures(data, category, start_date)
    assert len(filtered_data) == 24

    for departure in filtered_data:
        assert departure['category'] == category
        assert departure['start_date'] > start_date


@mock.patch('requests.get')
def test_get_departures(mock_get):
    departures = load_departures()
    mock_get.return_value = generate_mock_response()

    get = get_departures('test')
    assert next(get) == departures
    with pytest.raises(StopIteration):
        next(get)


def test_get_departures_server_unavailable():
    with pytest.raises(requests.RequestException):
        next(get_departures('test'))


@mock.patch('requests.get')
def test_generate_csv(mock_get):
    filename = 'test_csv.csv'
    mock_get.return_value = generate_mock_response()

    main(filename=filename)
    assert os.path.isfile(filename)
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f)
        counter = 1
        for _ in reader:
            counter += 1

    assert counter == 26  # header + rows + empty line at the end
    os.remove(filename)
