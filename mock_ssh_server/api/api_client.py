import requests


class ApiClient(object):
    def __init__(self, host, port):
        self._url = 'http://{}:{}'.format(host, port)

    def clear_commands(self):
        response = requests.delete('{}/commands'.format(self._url))
        return response.status_code

    def add_command(self, command):
        response = requests.post(url='{}/commands'.format(self._url), json=command)
        return response.status_code

    def get_commands(self):
        response = requests.get(url='{}/commands'.format(self._url))
        return response.text, response.status_code

    def clear_users(self):
        response = requests.delete('{}/users'.format(self._url))
        return response.status_code

    def add_user(self, user):
        response = requests.post(url='{}/users'.format(self._url), json=user)
        return response.status_code

    def get_users(self):
        response = requests.get(url='{}/users'.format(self._url))
        return response.text, response.status_code

    def clear_keys(self):
        response = requests.delete('{}/keys'.format(self._url))
        return response.status_code

    def add_key(self, key):
        response = requests.post(url='{}/keys'.format(self._url), json=key)
        return response.status_code

    def get_keys(self):
        response = requests.get(url='{}/keys'.format(self._url))
        return response.text, response.status_code
