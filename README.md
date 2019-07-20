# Robogram
A python library that allows to use instagram directly from your console
Can be used for promoting your account. (mass-like, mass-comment, mass-follow, mass-unfollow, etc)

## Installation
```python
git clone git@github.com:aogz/robogram.git
cd robogram
mkvirtualenv robogram  # Alternatively, virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
```

You can specify your instagram login and password in `robogram/settings.py`, so you won't need to pass --username and --password parameters each time you run robogram. Check other settings to make your robogram work even better.


## Usage examples

Please note: tags should be provided without `#` character. Limit parameter is optional in all methods. To avoid banning, keep limit parameter in between 100-300.


Like latest 100 posts with **#dogs** tag
```
python robogram-cli.py like-by-tag dogs
```

Like latest 200 posts with **#nature** tag. Comments are stored in `robogram/settings.py`, and will be commented randomly.
```
python robogram-cli.py comment-by-tag nature 200
```

Comment and like latest 100 posts with **#happy** tag.
```
python robogram-cli.py comment-and-like-by-tag happy
```

Follow latest 100 profiles, which uploaded a post with **#cats** tag.
```
python robogram-cli.py follow-by-tag cats
```

Get full user info of `zuck` account.
```
python robogram-cli.py user-info zuck
```

Send `zuck` a direct message.
```
python robogram-cli.py direct-message zuck 'Hi, how are you?'
```


```

### API Usage example: 
```
from client import InstagramAPIClient

insta =  InstagramAPIClient('username', 'password')
insta.login()

profile = insta.get_self_user_id_info()
followings = insta.get_self_users_following()
followers = insta.get_self_users_followers()
```
