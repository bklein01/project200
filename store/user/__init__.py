"""Users package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class User

"""

from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum, EnumInt
from store.user.statistics import UserStatistics


class User(DataModelController):

    Access = EnumInt('BASIC', 'PREMIUM', 'MOD', 'ADMIN')
    NotificationOccurrence = Enum('ALWAYS', 'DAILY', 'NEVER')
    NotificationMethod = Enum('ALL', 'EMAIL', 'INAPP')

    DEFAULT_SETTINGS = {
        'receive_promo_emails': True,
        'notification_occurrence': 'ALWAYS',
        'notification_method': 'INAPP',
        'filter_chat': True,
        'show_avatars': True
    }

    MODEL_RULES = {
        'user_id': ('user_id', int, None),
        'username': ('username', str, None),
        'profile_name': ('profile_name', str, None),
        'email': ('email', str, None),
        'pw_hash': ('pw_hash', str, None),
        'account_settings': ('account_settings', Collection.Dict, None),
        'active_games': ('active_games', Collection.List(int), None),
        'friends': ('friends', Collection.List(int), None),
        'blocked': ('blocked', Collection.List(int), None),
        'profile_avatar': ('profile_avatar', None, None),
        'access': ('access', int, None),
        'statistics': ('statistics', DataModel, lambda x: x.model)
    }

    def __init__(self, client, username, email, pw_hash, profile_name=None,
                 settings=None, access=None, refer=None, user_id=None,
                 games=None, friends=None, blocked=None, avatar=None,
                 stats=None):
        if not user_id:
            user_id = id(self)  # TODO: Replace with ID generator
        self.user_id = user_id
        self.client, self.username, self.email, self.pw_hash = (
            client, username, email, pw_hash)
        if not friends:
            friends = []
        if not blocked:
            blocked = []
        if not games:
            games = []
        if not profile_name:
            profile_name = email[:email.index('@')]
        if not access:
            access = User.Access.BASIC
        if not stats:
            stats = UserStatistics()
        if not avatar:
            avatar = ''
        (self.friends, self.blocked, self.active_games, self.profile_name,
         self.access, self.statistics, self.profile_avatar) = (
            friends, blocked, games, profile_name, access, stats, avatar)
        self.account_settings = dict(self.__class__.DEFAULT_SETTINGS)
        if settings:
            self.account_settings.update(settings)
        if refer:
            self.add_friend(refer)
        super(User, self).__init__(self.__class__.MODEL_RULES)

    def add_friend(self, friend_id):
        self.friends.append(friend_id)

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
