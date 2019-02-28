import fire
import random
import time

from robogram.client import InstagramAPIClient
from robogram import settings


class RobogramCLI:

    def __init__(self, username=None, password=None):
        self.username = username or settings.USERNAME
        self.password = password or settings.PASSWORD

        if not all([self.username, self.password]):
            raise Exception('Both username and password are required. Either provide --username --password parameters or set them in config/settings.py')

        self.client = InstagramAPIClient(self.username, self.password)
        self.client.login()


    def __action_by_tag(self, actions, tag, limit=100):
        more_available = True
        posts_processed = 0
        next_max_id = None
        
        # Avoid multiple actions on a single profile
        processed_profiles = []

        if type(actions) is not list:
            actions = [actions]

        while more_available and posts_processed < limit:
            response = self.client.get_hashtag_sections(tag, next_max_id)
            feed = self.client._validate_response(response)

            more_available = feed['more_available']
            next_max_id = feed['next_max_id']

            for section in feed.get('sections', []):
                if section['layout_type'] == 'media_grid':
                    medias = section['layout_content']['medias']
                    for media in medias:
                        action_done = False
                        media_id = media['media']['pk']
                        if all([media['media']['user']['username'] not in processed_profiles, media['media']['user']['username'] not in settings.IGNORE_LIST]):
                            if 'like' in actions:
                                if not media['media']['has_liked']:
                                    self.client.like(media_id)
                                    print('Media #{} from @{} liked.'.format(media['media']['pk'], media['media']['user']['username']))
                                    time.sleep(settings.SLEEP_BETWEEN_ACTIONS)
                                    action_done = True
                                else:
                                    print('Media #{} from @{} NOT liked. (Already liked)'.format(media['media']['pk'], media['media']['user']['username']))

                            if 'comment' in actions:
                                if self.client.username_id not in [comment['user_id'] for comment in media['media'].get('preview_comments', [])]:
                                    comment = random.choice(settings.COMMENTS)
                                    self.client.comment(media_id, comment)
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
                                    self.client.follow(user_id)
                                    print('User @{} followed.'.format(media['media']['user']['username']))
                                    time.sleep(settings.SLEEP_BETWEEN_ACTIONS)
                                    action_done = True
                                else:
                                    print('User @{} NOT followed. (Already followed)'.format(media['media']['user']['username']))
                            
                            processed_profiles.append(media['media']['user']['username'])
                            
                        if action_done:
                            posts_processed += 1

        print('Task finished. {} posts processed.'.format(posts_processed))

    def like_by_tag(self, tag, limit=100):
        return self.__action_by_tag('like', tag, limit)

    def comment_by_tag(self, tag, limit=100):
        return self.__action_by_tag('comment', tag, limit)

    def comment_and_like_by_tag(self, tag, limit=100):
        return self.__action_by_tag(['comment', 'like'], tag, limit)

    def follow_by_tag(self, tag, limit=100, **kwargs):
        return self.__action_by_tag('follow', tag, limit)

    def user_info(self, username):
        try:
            response = self.client._validate_response(self.client.get_username_info(username))
        except Exception as e:
            print('Can not send retrieve user info: {}'.format(e))
        else:
            if response['status'] == 'ok':
                user_id = response['user']['pk']
                user_name = response['user']['full_name']
                user_bio = response['user']['biography']
                user_link = response['user']['external_url']
                is_private = response['user']['is_private']
                is_verified = response['user']['is_verified']
                follower_count = response['user']['follower_count']
                following_count = response['user']['following_count']
                following_tag_count = response['user']['following_tag_count']
                media_count = response['user']['media_count']

                print("User ID: {}".format(user_id))
                print("User Name: {}".format(user_name))
                print("User Bio: {}".format(user_bio))
                print("User Link: {}".format(user_link))
                print("User is private: {}".format('Yes' if is_private else 'No'))
                print("User is verified: {}".format('Yes' if is_verified else 'No'))
                print("User followers: {}".format(follower_count))
                print("User following: {}".format(following_count))
                print("User following tags: {}".format(following_tag_count))
                print("User Media: {}".format(media_count))

            else:
                print('Can not  retrieve user info: {}'.format(response['status']))

    def direct_message(self, username, message):
        try:
            response = self.client._validate_response(self.client.get_username_info(username))
        except Exception as e:
            print('Can not retrieve user info: {}'.format(e))
            return

        if response['status'] == 'ok':
            user_id = response['user']['pk']
            try:
                response = self.client._validate_response(self.client.direct_message(user_id, message))
            except Exception as e:
                print('Can not send message: {}'.format(e))
                return

            if response['status'] == 'ok':
                print('Message sent')
            else:
                print('Can not send message: {}'.format(response['status']))
        else:
            print('Can not retrieve user info: {}'.format(response['status']))


if __name__ == '__main__':
    fire.Fire(RobogramCLI)