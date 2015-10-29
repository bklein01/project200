"""Users package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:


"""

from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum, EnumInt


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
                 settings=None, access=None, refer=None):
        self.user_id = id(self)  # TODO: Replace with ID generator
        self.client, self.username, self.email, self.pw_hash = (
            client, username, email, pw_hash)
        self.friends, self.blocked, self.active_games = [], [], []
        if refer:
            self.friends.append(refer)
        if not profile_name:
            profile_name = email[:email.index('@')]
        if not access:
            access = User.Access.BASIC
        self.profile_name, self.access = profile_name, access
        self.account_settings = self.__class__.DEFAULT_SETTINGS.update(settings)
        self.profile_avatar = ''
        super(User, self).__init__(self.__class__.MODEL_RULES)



# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
