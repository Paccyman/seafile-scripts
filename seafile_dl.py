#!/usr/bin/env python
# Script for simply download files/folders from Seafile
# Artem Alexandrov <alexandrov@devexperts.com>

import requests
import os
import sys
import cgi
import argparse
import json

SEAFILE_HOST = 'https://seafile.example.com'
SEAFILE_USER = 'username@example.com'
SEAFILE_PASS = 'strong_and_long_pa$$word'

# Read OS Environment variables they exist
if os.getenv('SEAFILE_HOST') is not None:
    SEAFILE_HOST = os.environ['SEAFILE_HOST']
if os.getenv('SEAFILE_USER') is not None:
    SEAFILE_USER = os.environ['SEAFILE_USER']
if os.getenv('SEAFILE_PASS') is not None:
    SEAFILE_PASS = os.environ['SEAFILE_PASS']


def ClientHttpError(code, message):
        print('ClientHttpError[%s: %s]' % (code, message))
        sys.exit(1)


def DoesNotExist(msg):
        print('DoesNotExist: {}'.format(msg))
        sys.exit(1)


class Seafile:
    def __init__(self, server, username, password):
        self.server = server
        self.token = None
        self.credentials = {'username': username, 'password': password}

    def get_token(self):
        """
        obtaining token from server
        :return: None
        """
        url = '/auth-token/'
        data = self._http_post(url, self.credentials)
        token = data['token']
        assert len(token) == 40, 'The length of seahub api auth token should be 40'
        self.token = 'Token ' + token

    def _http_post(self, url, params={}):
        """
        Make POST and return json response
        :param url: str
        :param params: dict
        :return: json
        """
        url = self.server + '/api2' + url
        try:
            r = requests.post(url=url, data=params)
        except requests.exceptions.RequestException as e:
            raise ClientHttpError(None, e)
        if r.status_code != 200:
            return ClientHttpError(r.status_code, r.text)
        data = json.loads(r.text)
        # TODO: check data
        return data

    def _http_get(self, url, params={}):
        """
        Helper for HTTP GET request
        :param: url: str
        :param: params:
        :return: json data
        """
        if not self.token:
            self.get_token()
        headers = {'Authorization': self.token, 'Accept': 'application/json; indent=4'}
        url = self.server + '/api2' + url
        try:
            r = requests.get(url=url, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            raise ClientHttpError(None, e)
        if r.status_code != 200:
            return ClientHttpError(r.status_code, json.loads(r.text)['error_msg'])
        data = json.loads(r.text)
        # TODO: check data
        return data

    def get_repos(self):
        """
        Get all available repos for user
        :return: json
        """
        url = '/repos/'
        data = self._http_get(url)
        return data

    def get_repo_id(self, repo_name):
        """
        Get id for library with desc name
        :param repo_name: str
        :return: str
        """
        libraries = self.get_repos()
        repo_id = ''
        for library in libraries:
            if library['name'] == repo_name:
                repo_id = library['id']
                break
        if not repo_id:
            raise DoesNotExist('Repo "{repo_desc}"'.format(repo_desc=repo_name))
        return repo_id

    def get_download_link(self, repo_name, p):
        """
        Get download link for file or dir
        If f endswtih '/' a link to folder will be generated
        :param repo_name: Library Name
        :param p: path to file or dir
        :return: str
        """
        repo_id = self.get_repo_id(repo_name)
        if p.endswith('/'):
            p = p[:-1]
            url = '/repos/{repo_id}/dir/download/'.format(repo_id=repo_id)
        else:
            url = '/repos/{repo_id}/file/'.format(repo_id=repo_id)
        params = {'p': p}
        data = self._http_get(url, params)
        return data

    def download_file(self, url, folder='./'):
        r = requests.get(url, stream=True)
        # Get Attachment filename and parse it
        value, params = cgi.parse_header(r.headers['content-disposition'])
        filename = params['filename']
        output = folder + '/' + filename
        with open(output, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return output


if __name__ == '__main__':
    seafile = Seafile(SEAFILE_HOST, SEAFILE_USER, SEAFILE_PASS)
    # Parsing arguments
    parser = argparse.ArgumentParser(description='Download file/folder from Seafile server')
    parser.add_argument('-o', '--output', type=str, default='./', help='Folder to save downloaded file')
    parser.add_argument('-l', '--library', type=str, required=True, help='Library name')
    parser.add_argument('-p', '--path', type=str, required=True,
                        help='Path to folder or file inside Library (ex: buildXX/ )')
    args = parser.parse_args()

    # Check if output dir exist and create if needed
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    download_link = seafile.get_download_link(args.library, args.path)
    print(seafile.download_file(download_link, args.output))
