import requests
from urllib.parse import urlencode, urljoin
from django.conf import settings


class BaseEVolutionAPI:

    def __init__(self):
        self._BASE_URL = settings.EVOLUTION_API_URL
        self._API_KEY = settings.EVOLUTION_API_KEY
        self._INSTANCE_NAME = settings.EVOLUTION_INSTANCE_NAME
    
    def _send_request(
        self,
        path,
        method='GET',
        body=None,
        headers={},
        params_url={}
    ):
        method = method.upper()
        url = self._mount_url(path, params_url)
        
        if not isinstance(headers, dict):
            headers = {}

        headers.setdefault('Content-Type', 'application/json')
        headers['apikey'] = self._API_KEY

        request = {
            'GET': requests.get,
            'POST': requests.post,
            'PUT': requests.put,
            'DELETE': requests.delete
        }.get(method)

        return request(url, headers=headers, json=body)
        
    def _mount_url(self, path, params_url):
        parameters = ''
        if isinstance(params_url, dict) and params_url:
            parameters = urlencode(params_url)
        
        url = urljoin(self._BASE_URL, path)

        if parameters:
            url = url + '?' + parameters
        return url


class SendMessage(BaseEVolutionAPI):

    def send_message(self, body):
        path = f'/message/sendText/{self._INSTANCE_NAME}/'
        return self._send_request(path, method='POST', body=body)