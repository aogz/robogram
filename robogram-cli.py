import fire
import json 
import random 
import time

from api.client import InstagramAPIClient
from config import settings


class RobogramCLI:

    def __login(self, username=None, password=None):
        username = username or settings.USERNAME
        password = password or settings.PASSWORD

        if not all([username, password]):
            raise Exception('Both username and password are required. Either provide --username --password parameters or set them in config/settings.py')

        client = InstagramAPIClient(username, password)
        client.login()
        return client

    def __action_by_tag(self, actions, tag, limit=100, username=None, password=None):
        client = self.__login()
        more_available = True
        posts_processed = 0
        next_max_id = None
        
        # Avoid multiple actions on a single profile
        processed_profiles = []

        if type(actions) is not list:
            actions = [actions]

        while more_available and posts_processed < limit:
            response = client.get_hashtag_sections(tag, next_max_id)
            feed = client._validate_response(response)

            more_available = feed['more_available']
            next_max_id = feed['next_max_id']

            for section in feed.get('sections', []):
                if section['layout_type'] == 'media_grid':
                    medias = section['layout_content']['medias']
                    for media in medias:
                        action_done = False
                        media_id = media['media']['pk']
                        if media['media']['user']['username'] not in processed_profiles:
                            if 'like' in actions:
                                if not media['media']['has_liked']:
                                    client.like(media_id)
                                    print('Media #{} from @{} liked.'.format(media['media']['pk'], media['media']['user']['username']))
                                    time.sleep(settings.SLEEP_BETWEEN_ACTIONS)
                                    action_done = True
                                else:
                                    print('Media #{} from @{} NOT liked. (Already liked)'.format(media['media']['pk'], media['media']['user']['username']))

                            if 'comment' in actions:
                                if client.username_id not in [comment['user_id'] for comment in media['media'].get('preview_comments', [])]:
                                    comment = random.choice(settings.COMMENTS)
                                    client.comment(media_id, comment)
                                    print('Media #{} from @{} commented: {}.'.format(media['media']['pk'], media['media']['user']['username'], comment))
                                    time.sleep(settings.SLEEP_BETWEEN_ACTIONS)
                                    action_done = True
                                else:
                                    print('Media #{} from @{} NOT commented. (Already commented)'.format(media['media']['pk'], media['media']['user']['username']))

                            if 'follow' in actions:
                                user_id = media['media']['user']['pk']
                                following = media['media']['user']['friendship_status']['following']
                                outgoing_request = media['media']['user']['friendship_status']['outgoing_request']
                                if not following and not outgoing_request:
                                    client.follow(user_id)
                                    print('User @{} followed.'.format(media['media']['user']['username']))
                                    time.sleep(settings.SLEEP_BETWEEN_ACTIONS)
                                    action_done = True
                                else:
                                    print('User @{} NOT followed. (Already followed)'.format(media['media']['user']['username']))
                            
                            processed_profiles.append(media['media']['user']['username'])
                            
                        if action_done:
                            posts_processed += 1

        print('Task finished. {} posts processed.'.format(posts_processed))

    def like_by_tag(self, tag, limit=100, username=None, password=None):
        return self.__action_by_tag('like', tag, limit, username, password)

    def comment_by_tag(self, tag, limit=100, username=None, password=None):
        return self.__action_by_tag('comment', tag, limit, username, password)

    def comment_and_like_by_tag(self, tag, limit=100, username=None, password=None):
        return self.__action_by_tag(['comment', 'like'], tag, limit, username, password)

    def follow_by_tag(self, tag, limit=100, username=None, password=None, **kwargs):
        return self.__action_by_tag('follow', tag, limit, username, password)


if __name__ == '__main__':
    fire.Fire(RobogramCLI)