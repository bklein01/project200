"""Users package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class User

"""

import re
from combomethod import combomethod
from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum, EnumInt
from core.dotdict import DotDict
from core.decorators import classproperty
from store.user.statistics import UserStatistics
from server.auth import hash_values, timeout_check
from server.exception import (ForbiddenError, UnauthorizedError,
                              TokenInvalidError, BadRequestError)
from config.words import has_bad_words


class User(DataModelController):

    Access = EnumInt('BANNED', 'BASIC', 'PREMIUM', 'MOD', 'ADMIN')
    NotificationOccurrence = Enum('ALWAYS', 'DAILY', 'NEVER')
    NotificationMethod = Enum('ALL', 'EMAIL', 'INAPP')

    _client_to_user_map = {}

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
            'statistics': ('statistics', DataModel, lambda x: x.model),
            'activated': ('activated', bool, None)
        })
        return rules

    @classproperty
    def MODEL_FILTER_PUBLIC(cls):
        rules = super(User, cls).MODEL_FILTER_PUBLIC
        rules += ['profile_name', 'profile_avatar']
        return rules

    @classproperty
    def MODEL_FILTER_PROTECTED(cls):
        rules = super(User, cls).MODEL_FILTER_PROTECTED
        rules += ['username', 'active_games', 'friends', 'access',
                  'statistics']
        return rules

    @classproperty
    def MODEL_FILTER_PRIVATE(cls):
        rules = super(User, cls).MODEL_FILTER_PRIVATE
        rules += ['blocked', 'settings', 'email']

    @classproperty
    def INIT_DEFAULTS(cls):
        defaults = super(User, cls).INIT_DEFAULTS
        defaults.update({
            'client': None,
            'friends': [],
            'blocked': [],
            'activated': False,
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
            if rec.client:
                rec.logout()
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
            'client': None,
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
            'blocked': data_model.blocked,
            'activated': data_model.activated
        })
        ctrl = super(User, cls).restore(data_store, data_model, **kwargs)
        for k, v in cls._client_to_user_map.iteritems():
            if ctrl.uid == v:
                ctrl.client = k
        return ctrl

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, username, email, pw_hash, data_store=None, refer=None,
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
            'username': username,
            'email': email,
            'pw_hash': pw_hash,
        })
        ctrl = super(User, cls).new(data_store, **kwargs)
        if refer:
            ctrl.add_friend(refer)
        if data_store:
            ctrl.save(data_store)
        return ctrl

    @classmethod
    def auth_user_request(cls, data_store, client, token, timestamp, *args):
        timeout_check(timestamp)
        user = cls.get_user_by_client(client, data_store)
        if not user:
            raise UnauthorizedError("Client not logged in.")
        if hash_values(user.pw_hash, timestamp, *args) != token:
            raise UnauthorizedError("Incorrect password.")
        return user

    @classmethod
    def auth_request(cls, data_store, client, token, timestamp, *args):
        timeout_check(timestamp)
        user = cls.get_user_by_client(client, data_store)
        if not user:
            raise UnauthorizedError("Client not logged in.")
        if hash_values(client, timestamp, *args) != token:
            raise TokenInvalidError("Incorrect token provided.")

    @classmethod
    def auth_register(cls, data_store, client, token, timestamp, username,
                      pw_hash, email, refer=None):
        timeout_check(timestamp)
        if (not re.match('/[a-zA-Z0-9\._\-]{4,24}/', username) or
                has_bad_words(username)):
            raise BadRequestError("Invalid username.")
        # Remember to send validation link.
        if not re.match('/^.+@.+\..+$/', email):
            raise BadRequestError("Invalid email.")
        if data_store.find_id(cls, username=username):
            raise BadRequestError("Username taken.")
        if data_store.find_id(cls, email=email):
            raise BadRequestError("Email already used.")
        if refer:
            if '@' in refer:
                refer = data_store.find_id(cls, email=refer)
            else:
                refer = data_store.find_id(cls, username=refer)
        if hash_values(client, timestamp, username, email, pw_hash) != token:
            raise TokenInvalidError("Incorrect token provided.")
        return User.new(username, email, pw_hash, data_store, refer)

    @classmethod
    def auth_login(cls, data_store, client, token, timestamp, username):
        timeout_check(timestamp)
        email = False
        if '@' in username:
            email = True
        if client in cls._client_to_user_map:
            raise ForbiddenError("Client already logged in.")
        if email:
            user = cls.find(data_store, email=email)
        else:
            user = cls.find(data_store, username=username)
        if not user:
            raise UnauthorizedError("User by that name/email does not exist.")
        if hash_values(user.pw_hash, timestamp, username) != token:
            raise UnauthorizedError("Incorrect password.")
        return user, user.login(client)

    @classmethod
    def get_user_by_client(cls, data_store, client):
        user = None
        try:
            user = cls._client_to_user_map[client]
            if data_store:
                user = cls.get(data_store, user)
        except KeyError:
            pass
        return user

    def update_settings(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k in self.settings and self.settings[k] == v:
                continue
            self.settings[k] = v
            self._update_model_collection('settings', {'action': 'update',
                                                       'key': k})

    def login(self, client):
        old_client = self.client
        self.client = client
        store = self if self._data_store else self.uid
        self.__class__._client_to_user_map[client] = store
        return old_client

    def logout(self):
        try:
            del self.__class__._client_to_user_map[self.client]
        except KeyError:
            pass
        self.client = None

    def add_friend(self, friend_id):
        self.friends.append(friend_id)
        self._update_model_collection('friends', {'action': 'append'})

    def remove_friend(self, id_or_index):
        if type(id_or_index) is str:
            index = self.friends.index(id_or_index)
        else:
            index = id_or_index
        del self.friends[index]
        self._update_model_collection('friends', {'action': 'remove',
                                                  'index': index})

# ----------------------------------------------------------------------------
__version__ = 0.2
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
