import json

from robogram import settings
from . import base


class InstagramAPIClient(base.InstagramAPIBase):

    def login(self):
        if not self.is_logged_in:
            response = self._send_request('si/fetch_headers/?challenge_type=signup&guid={}'.format(self._generate_uuid(False)))
            if self._validate_response(response):
                data = {
                    'phone_id': self._generate_uuid(True),
                    '_csrftoken': response.cookies['csrftoken'],
                    'username': self.username,
                    'guid': self.uuid,
                    'device_id': self.device_id,
                    'password': self.password,
                    'login_attempt_count': '0'
                }

                response = self._send_request('accounts/login/', self._generate_signature(json.dumps(data)))
                if self._validate_response(response):
                    print('Logged in!')
                    self._post_login(response)

    def get_user_id_info(self, user_id):
        return self._send_request('users/{}/info/'.format(user_id))

    def get_username_info(self, username):
        return self._send_request('users/{}/usernameinfo/'.format(username))

    def get_self_user_id_info(self):
        return self.get_user_id_info(self.username_id)

    def like(self, media_id):
        data = json.dumps({'media_id': media_id, **self._get_default_request_data()})
        return self._send_request('media/{}/like/'.format(media_id), self._generate_signature(data))

    def unlike(self, media_id):
        data = json.dumps({'media_id': media_id, **self._get_default_request_data()})
        return self._send_request('media/{}/unlike/'.format(media_id), self._generate_signature(data))

    def follow(self, user_id):
        data = json.dumps({'user_id': user_id, **self._get_default_request_data()})
        return self._send_request('friendships/create/{}/'.format(user_id), self._generate_signature(data))

    def unfollow(self, user_id):
        data = json.dumps({'user_id': user_id, **self._get_default_request_data()})
        return self._send_request('friendships/destroy/{}/'.format(user_id), self._generate_signature(data))

    def comment(self, media_id, text):
        data = json.dumps({'comment_text': text, **self._get_default_request_data()})
        return self._send_request('media/{}/comment/'.format(media_id), self._generate_signature(data))

    def stories(self, user_id):
        return self._send_request("feed/user/{}/story/".format(user_id))

    def get_user_followings(self, username_id, max_id=None):
        url = 'friendships/{}/following/?ig_sig_key_version={}&rank_token={}'.format(username_id, settings.SIG_KEY_VERSION, self.rank_token)
        if max_id:
            url += '&max_id={}'.format(max_id)

        return self._send_request(url)

    def get_self_users_following(self, max_id=None):
        return self.get_user_followings(self.username_id, max_id=None)

    def get_user_followers(self, username_id, max_id=None):
        url = 'friendships/{}/followers/?rank_token={}'.format(username_id, self.rank_token)
        if max_id:
            url += '&max_id={}'.format(max_id)

        return self._send_request(url)

    def get_self_user_followers(self):
        return self.get_user_followers(self.username_id)

    def get_hashtag_feed(self, hashtag_string, max_id=None):
        url = 'feed/tag/{}/?max_id={}&rank_token={}&ranked_content=true'.format(hashtag_string, max_id, self.rank_token)
        return self._send_request(url, {'tab': 'recent'})

    def get_hashtag_sections(self, hashtag_string, max_id=None):
        url = 'tags/{}/sections/?max_id={}&rank_token={}&ranked_content=true'.format(hashtag_string, max_id or '', self.rank_token)
        return self._send_request(url, {'tab': 'recent', 'supported_tabs': "['top','recent','places']"})

    def get_media_info(self, media_id):
        data = json.dumps({'media_id': media_id, **self._get_default_request_data()})
        return self._send_request('media/{}/info/'.format(media_id), self._generate_signature(data))

    def get_user_feed(self, username_id, max_id=''):
        url = 'feed/user/{}/?max_id={}&rank_token={}&ranked_content=true'.format(username_id, max_id, self.rank_token)
        return self._send_request(url)

    # def get_user_info(self, username):
    #     return self.session.get('https://instagram.com/{}/?__a=1'.format(username))

    def direct_message(self, recipients, message):
        if not isinstance(recipients, list):
            recipients = [recipients]

        recipient_users = '"",""'.join(map(str, recipients))

        url = 'direct_v2/threads/broadcast/text/'
        bodies = [
            {
                'type': 'form-data',
                'name': 'recipient_users',
                'data': '[["{}"]]'.format(recipient_users),
            },
            {
                'type': 'form-data',
                'name': 'client_context',
                'data': self.uuid,
            },
            {
                'type': 'form-data',
                'name': 'thread',
                'data': '["0"]',
            },
            {
                'type': 'form-data',
                'name': 'text',
                'data': message,
            },
        ]

        data = self._build_body(bodies, self.uuid)

        self.session.headers.update(
            {
                'User-Agent': settings.USER_AGENT,
                'Proxy-Connection': 'keep-alive',
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Content-Type': 'multipart/form-data; boundary={}'.format(self.uuid),
                'Accept-Language': 'en-en',
            }
        )

        return self.session.post(settings.API_URL + url, data=data.encode())
