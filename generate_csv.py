import csv
import sys
from typing import Dict, Generator, List

import requests


def filter_departures(departures: List[Dict[str, str]], category: str, start_date: str) -> List[Dict[str, str]]:
    """
    Filter departures by provided category and start_date.
    :param departures:
    :param category: Desired category.
    :param start_date: Desired start date of departure (exclusive) in format `%Y-%m-%d`.
    :return: Filtered list of Departure dicts.
    """
    return [e for e in departures if e['category'] == category and e['start_date'] > start_date]


def get_departures(next_url: str) -> Generator[List[Dict[str, str]], None, None]:
    """
    Get departures from desired url. Will raise requests.RequestException in case of connection problems.
    :param next_url: API URL.
    :return: List of received Departure dicts.
    """
    # We could add a safe stopping condition here if we have suspicion that API could create infinite loop.
    while next_url:
        response = requests.get(next_url).json()
        next_url = response['next']
        yield response['results']


def generate_csv(data: List[Dict[str, str]], filename: str) -> None:
    """
    Create CSV with provided departures list
    :param data: List of Departure dicts.
    :param filename: Desired name of CSV file.
    """
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['Name', 'Start Date', 'Finish Date', 'Category'])
        for departure in data:
            writer.writerow([
                departure['name'],
                departure['start_date'],
                departure['finish_date'],
                departure['category'],
            ])


def generate_endpoint(**kwargs) -> str:
    """
    Generate full endpoint URL from parameters or default ones.
    :param kwargs: Parameters.
    :return: Generated URL.
    """
    protocol = kwargs.get('protocol', 'http')
    hostname = kwargs.get('hostname', '127.0.0.1')
    port = kwargs.get('port', '8000')
    api = kwargs.get('api', 'departures')
    return f'{protocol}://{hostname}:{port}/{api}'


def main(**kwargs) -> None:
    """
    Main function.
    :param kwargs: Parameters.
    """
    endpoint = generate_endpoint(**kwargs)

    category = kwargs.get('category', 'Adventurous')
    start_date = kwargs.get('start_date', '2018-06-01')

    csv_file = kwargs.get('filename', 'filtered_departures.csv')

    result = []

    try:
        for departures in get_departures(endpoint):
            result.extend(filter_departures(departures, category, start_date))
    except requests.RequestException as e:
        sys.stderr.write(str(e))
        sys.exit(2)

    generate_csv(result, csv_file)


if __name__ == '__main__':
    _kwargs = {}
    for arg in sys.argv[1:]:
        split = arg.split('=')
        if len(split) != 2:
            sys.stderr.write("Wrong argument type.")
            sys.exit(1)

        _kwargs[split[0]] = split[1]

    main(**_kwargs)
