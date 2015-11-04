"""Users package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class User

"""

from combomethod import combomethod
from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum, EnumInt
from core.dotdict import DotDict
from core.decorators import classproperty
from store.user.statistics import UserStatistics


class User(DataModelController):

    Access = EnumInt('BASIC', 'PREMIUM', 'MOD', 'ADMIN')
    NotificationOccurrence = Enum('ALWAYS', 'DAILY', 'NEVER')
    NotificationMethod = Enum('ALL', 'EMAIL', 'INAPP')

    @classproperty
    def DEFAULT_SETTINGS(cls):
        return DotDict({
            'receive_promo_emails': True,
            'notification_occurrence': 'ALWAYS',
            'notification_method': 'INAPP',
            'filter_chat': True,
            'show_avatars': True
        })

    @classproperty
    def MODEL_RULES(cls):
        rules = super(User, cls).MODEL_RULES
        rules.update({
            'username': ('username', str, None),
            'profile_name': ('profile_name', str, None),
            'email': ('email', str, None),
            'pw_hash': ('pw_hash', str, None),
            'settings': ('settings', Collection.Dict, None),
            'active_games': ('active_games', Collection.List(str), None),
            'friends': ('friends', Collection.List(str), None),
            'blocked': ('blocked', Collection.List(str), None),
            'profile_avatar': ('profile_avatar', None, None),
            'access': ('access', int, None),
            'statistics': ('statistics', DataModel, lambda x: x.model)
        })
        return rules

    @classproperty
    def INIT_DEFAULTS(cls):
        defaults = super(User, cls).INIT_DEFAULTS
        defaults.update({
            'friends': [],
            'blocked': [],
            'active_games': [],
            'profile_name': 'Newbie',
            'access': User.Access.BASIC,
            'profile_avatar': '',
            'settings': cls.DEFAULT_SETTINGS
        })
        return defaults

    # noinspection PyMethodParameters
    @combomethod
    def delete_cache(rec, data_store, uid=None):
        """Delete controller member cache first."""
        if isinstance(rec, User):
            rec.statistics.delete_cache(data_store)
        super(User, rec).delete_cache(data_store, uid)

    # noinspection PyMethodParameters
    @combomethod
    def delete(rec, data_store, uid=None):
        """Prevent user from being deleted by default."""
        raise RuntimeError("Users should not be deleted. "
                           "If this was intentional, use "
                           "`User.force_delete` or `user."
                           "force_delete`.")

    # noinspection PyMethodParameters
    @combomethod
    def force_delete(rec, data_store, uid=None):
        """Permanently delete User."""
        if isinstance(rec, User):
            rec.statistics.delete(data_store)
        super(User, rec).delete(data_store, uid)

    @classmethod
    def restore(cls, data_store, data_model, **kwargs):
        kwargs.update({
            'client': data_model.client,
            'profile_name': data_model.profile_name,
            'statistics': UserStatistics.restore(data_store,
                                                 data_model.statistics),
            'username': data_model.username,
            'email': data_model.email,
            'pw_hash': data_model.pw_hash,
            'settings': data_model.settings,
            'active_games': data_model.active_games,
            'access': data_model.access,
            'profile_avatar': data_model.profile_avatar,
            'friends': data_model.friends,
            'blocked': data_model.blocked
        })
        return super(User, cls).restore(data_store, data_model, **kwargs)

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, client, username, email, pw_hash, data_store=None, refer=None,
            **kwargs):
        if 'profile_name' not in kwargs:
            kwargs['profile_name'] = email[:email.index('@')]
        if 'statistics' not in kwargs:
            kwargs['statistics'] = UserStatistics.new(data_store)
        if 'settings' in kwargs:
            s = kwargs['settings']
            kwargs['settings'] = cls.DEFAULT_SETTINGS
            kwargs['settings'].update(s)
        kwargs.update({
            'client': client,
            'username': username,
            'email': email,
            'pw_hash': pw_hash
        })
        ctrl = super(User, cls).new(data_store, **kwargs)
        if refer:
            ctrl.add_friend(refer)
        return ctrl

    def add_friend(self, friend_id):
        self.friends.append(friend_id)

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
