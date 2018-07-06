import csv
import json
import os.path

from generate_csv import filter_departures, generate_endpoint, main


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
    with open('departures.json', 'r') as f:
        data = json.load(f)

    filtered_data = filter_departures(data, category, start_date)
    assert len(filtered_data) == 24

    for departure in filtered_data:
        assert departure['category'] == category
        assert departure['start_date'] > start_date


def test_generate_csv():
    filename = 'test_csv.csv'
    main(filename=filename)
    assert os.path.isfile(filename)
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f)
        counter = 1
        for _ in reader:
            counter += 1

    assert counter == 26  # header + rows + empty line at the end
    os.remove(filename)
