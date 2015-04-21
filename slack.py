__author__ = 'Eshin Kunishima'
__license__ = 'MIT License'

import urllib.parse
import urllib.request
import json


class Slack:
    @staticmethod
    def notice(url, text):
        request = urllib.request.Request(url, data=json.dumps({'text': text}).encode('UTF-8'))
        response = urllib.request.urlopen(request)
        response.read()