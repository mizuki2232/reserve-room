import logging
import os

import requests

ETCD_URL = os.environ.get('ETCD_URL', 'http://127.0.0.1:4001')
ETCD_URL_VERSION_PATH = os.environ.get('ETCD_URL_VERSION_PATH', '/v2/keys')

LOGGER = logging.getLogger(__name__)


class DiscoveryError(Exception):
    pass


def call(disovery_path, callback, args=None, kwargs=None):
    """
    Attempt to connect to each of the values returned by the disovery_path

    :param disovery_path: dict - the return value of get() below
    :param callback: func - function to call with each value
    :return:
    """
    args = args or ()
    kwargs = kwargs or {}

    for key, value in get(disovery_path).items():
        try:
            connection = callback(value, *args, **kwargs)
        except Exception, exc:
            LOGGER.exception(exc)
            LOGGER.error('unable to connect to discovery path key={}, value={}'.format(key, value))
        else:
            return connection
    else:
        raise DiscoveryError('unable to connect to any urls at disovery_path={}'.format(disovery_path))


def get(discovery_path):
    """
    Get the values at the given discovery path

    :param discovery_path: string - e.g. /zymbit/redis
    :return: dict - e.g. {'redis.service': 'redis://docker.local:49154/0'}
    """
    values = {}

    etcd_url_base = '{}{}'.format(ETCD_URL, ETCD_URL_VERSION_PATH)
    url = '{}{}'.format(etcd_url_base, discovery_path)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.ConnectionError:
        LOGGER.error('unable to connect to url={}'.format(url))

        raise
    except requests.HTTPError:
        LOGGER.error('unable to discover at url={}'.format(url))

        raise

    data = response.json()

    # check if the discovery path is a directory and return one of the entries
    if data['node'].get('dir'):
        for item in data['node']['nodes']:
            name = item['key'][len(discovery_path)+1:]  # add 1 for getting rid of the leading slash in the path
            values[name] = item['value']
    else:
        item = data['node']
        name = item['key'][len(discovery_path):]

        values[name] = item['value']

    return values
