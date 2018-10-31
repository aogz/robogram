import requests
import hashlib
import uuid
import time
import json
import hmac
import urllib
import urllib3

import settings

urllib3.disable_warnings()

class InstagramAPIBase:

    def __init__(self, username, password):
        self.set_user(username, password)
        self.device_id = self._generate_device_id()
        self.is_logged_in = False
        self.last_response = None
        self.session = requests.Session()

    def set_user(self, username, password):
        self.username = username
        self.password = password
        self.uuid = self._generate_uuid(True)

    def _generate_device_id(self):
        m = hashlib.md5()
        m.update(self.username.encode('utf-8') + self.password.encode('utf-8'))
        seed = m.hexdigest()
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    def _generate_uuid(self, type):
        generated_uuid = str(uuid.uuid4())
        if (type):
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

    def _post_login(self, response):
        validated_response = self._validate_response(response)

        self.is_logged_in = True
        self.username_id = validated_response["logged_in_user"]["pk"]
        self.rank_token = "{}_{}".format(self.username_id, self.uuid)
        self.token = response.cookies["csrftoken"]

        self._sync_features()
        self._auto_complete_user_list()
        self._timeline_feed()
        self._get_v2_inbox()
        self.get_recent_activity()
    
    def _send_request(self, endpoint, data=None):
        self.session.headers.update({
            'Connection': 'close',
            'Accept': '*/*',
            'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie2': '$Version=1',
            'Accept-Language': 'en-US',
            'User-Agent': settings.USER_AGENT
        })

        if (data is not None):
            response = self.session.post(settings.API_URL + endpoint, data=data, verify=settings.VERIFY_REQUESTS)
        else:
            response = self.session.get(settings.API_URL + endpoint, verify=settings.VERIFY_REQUESTS)

        return response

    def _validate_response(self, response):
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise Exception("Request return " + str(response.status_code) + " error!")

    def _generate_signature(self, data):
        parsedData = urllib.parse.quote(data)
        signed_body = "{}.{}".format(hmac.new(settings.IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest(), parsedData)
        signature = 'ig_sig_key_version={}&signed_body={}'.format(settings.SIG_KEY_VERSION, signed_body)
        return signature

    def _get_default_request_data(self):
        return {
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        }

    def _sync_features(self):
        data = json.dumps({
            **self._get_default_request_data(),
            'id': self.username_id,
            'experiments': settings.EXPERIMENTS
        })
        return self._send_request('qe/sync/', self._generate_signature(data))

    def _auto_complete_user_list(self):
        return self._send_request('friendships/autocomplete_user_list/')

    def _timeline_feed(self):
        return self._send_request('feed/timeline/')

    def _get_v2_inbox(self):
        return self._send_request('direct_v2/inbox/?')

    def get_recent_activity(self):
        return self._send_request('news/inbox/?')