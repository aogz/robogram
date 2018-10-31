# Robogram
A python library that allows to use instagram directly from your console
Can be used for promoting your account. (mass-like, mass-comment, mass-follow, mass-unfollow, etc)

### Usage example: 
```python
from client import InstagramAPIClient

insta =  InstagramAPIClient('username', 'password')
insta.login()

profile = insta.get_self_username_info()
followings = insta.get_self_users_following()
followers = insta.get_self_users_followers()
```