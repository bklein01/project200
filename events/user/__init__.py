"""`user*` event handlers.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

"""

from .. import EventHandler
from store.user import User
from store import DataStore
from server.exception import ForbiddenError


class UserRequestEventHandler(EventHandler):

    @classmethod
    def auth(cls, event):
        return User.auth_request(DataStore, event.client, event.data.token,
                                 event.timestamp, event.data.salt)


class UserAccountRequestEventHandler(EventHandler):

    @classmethod
    def auth(cls, event):
        return User.auth_user_request(DataStore, event.client,
                                      event.data.token, event.data.timestamp,
                                      event.data.salt)


class UserRegistrationEventHandler(EventHandler):

    @classmethod
    def auth(cls, event):
        if not event.data.get('agree', False):
            raise ForbiddenError("User did not agree to terms.")
        return User.auth_register(DataStore, event.client, event.data.token,
                                  event.data.timestamp, event.data.username,
                                  event.data.pw_hash, event.data.email,
                                  event.data.get('refer', None))


class UserLoginEventHandler(EventHandler):

    @classmethod
    def auth(cls, event):
        return User.auth_login(DataStore, event.client, event.data.token,
                               event.data.timestamp, event.data.username)
