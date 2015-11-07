"""`user-register` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import UserRegistrationEventHandler
from server import EventServer
from store import DataStore


@UserRegistrationEventHandler(
    expected_data=('username',
                   'pw_hash',
                   'email',
                   'timestamp',
                   'token'
                   ))
def register(event):
    user = event.auth
    if not user:
        raise RuntimeError("No new user created during registration!")
    user.update_settings(
        receive_promo_emails=event.data.get('promotion', False))
    EventServer.emit(event.ok_response(username=user.username), event.client)
    user.delete_cache(DataStore)
