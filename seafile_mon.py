#!/usr/bin/env python3
# Script for monitoring Seafile Server 
# Artem Alexandrov <alexandrov@devexperts.com>

import requests
import os
import sys
import argparse
import json
import smtplib
from email.mime.text import MIMEText

SEAFILE_HOST = 'https://seafile.example.com'
SEAFILE_USER = 'username@example.com'
SEAFILE_PASS = 'strong_and_long_pa$$word'
mail_server = '{{ smtp_host }}'
mail_from = 'seafile@bots.example.com'

# Read OS Environment variables they exist
if os.getenv('SEAFILE_HOST') is not None:
    SEAFILE_HOST = os.environ['SEAFILE_HOST']
if os.getenv('SEAFILE_USER') is not None:
    SEAFILE_USER = os.environ['SEAFILE_USER']
if os.getenv('SEAFILE_PASS') is not None:
    SEAFILE_PASS = os.environ['SEAFILE_PASS']

mail_template = '''
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><div style="background:xf2f2f2;padding:40px 0;">
<div style="width:700px;background:xfff;border-style:Solid;border-width:1px;border-color:xeaeaea #cccccc #a6a6a6;border-radius:4px;box-shadow:0 2px 2px #cdcdcd;margin:0 auto;">
    <img src="{seafile_url}/media/custom/logo.png" alt="" style="display:block;margin:20px 0 15px 50px;">
    <div style="padding:30px 55px 40px;min-height:300px;border-top:1px solid #efefef;background:transparent url('https://{seafile_url}/media/img/email_bg.jpg') scroll repeat-x center top;">
        

<p style="color:x121214;font-size:14px;">Hi,</p>
<p style="font-size:14px;color:x434144;">
Space for user <i>{email}</i> on <i>{seafile_url}</i> is running out ({remains}% free). Please take some actions.
</p>


        <p style="font-size:14px;color:x434144;margin:30px 0;">
        Thanks for using Seafile!
        </p>
        <p style="font-size:14px;color:x434144;">
        </p>
    </div>
</div>
</div>
'''


def ClientHttpError(code, message):
        print('ClientHttpError[%s: %s]' % (code, message))
        sys.exit(1)


def sending_email(address, remains):
    receiver = address
    smtp_server = mail_server
    body = mail_template.format(email=address, remains=remains, seafile_url=SEAFILE_HOST)
    msg = MIMEText(body, "html", "utf-8")
    msg['Subject'] = '[Seafile] Free space alert for user {email} ({remains}% left)'.format(email=address,
                                                                                            remains=remains)
    msg['From'] = mail_from
    msg['To'] = receiver
    s = smtplib.SMTP(smtp_server)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()
    return


def check_failed(error=None):
    if args.debug and error:
        print(error)
    print(0)
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
            return check_failed(e)
            # raise ClientHttpError(None, e)
        if r.status_code != 200:
            return check_failed(r.status_code)
            # return ClientHttpError(r.status_code, r.text)
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
            return check_failed(e)
            # raise ClientHttpError(None, e)
        if r.status_code != 200:
            return check_failed(r.status_code)
            # return ClientHttpError(r.status_code, json.loads(r.text)['error_msg'])
        try:
            data = json.loads(r.text)
        except:
            data = r.text
        # TODO: check data
        return data
    
    def get_account_info(self, account):
        # Purpose:  method for getting account's info for specified user
        # Input:    session token, email of user's account
        # Output:   data related to specified account
        # Note:     http://manual.seafile.com/develop/web_api.html
        url = '/accounts/{account}/'.format(account=account)
        data = self._http_get(url)
        return data
    
    def ping(self):
        """
        Ping/Pong
        """
        url = '/ping/'
        data = self._http_get(url)
        if data == 'pong':
            return True
        else:
            return False

if __name__ == '__main__':
    # Parsing arguments
    parser = argparse.ArgumentParser(description='Script for mfonitoring Seafile server')
    parser.add_argument('-c', '--command', type=str, default='ping', help='Command to execute (ping|quota)')
    parser.add_argument('-m', '--email', type=str, help='User each quote to check')
    parser.add_argument('-u', '--user', type=str, help='Auth User')
    parser.add_argument('-p', '--password', type=str, help='Auth User passwrod')
    parser.add_argument('-s', '--server', type=str, required=True, help='Seafile Server')
    parser.add_argument('-n', '--notify', help='Send notification if %% is below 5', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
    args = parser.parse_args()
   
    if args.user:
        SEAFILE_USER = args.user
    if args.password:
        SEAFILE_PASS = args.password
    if args.server:
        SEAFILE_HOST = args.server
    seafile = Seafile(SEAFILE_HOST, SEAFILE_USER, SEAFILE_PASS)
    if args.command == 'ping':
        if not seafile.ping():
            check_failed()
        else:
            print(1)
    elif args.command == 'quota':
        target = args.email
        result = seafile.get_account_info(target)
        remains = ((result['total'] - result['usage']) / result['total']) * 100
        remains = round(remains)
        print(remains)
        if args.notify:
            sending_email(target, remains)
