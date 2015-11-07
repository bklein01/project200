"""`user-signout` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import UserRequestEventHandler
from server import EventServer
from store import DataStore


@UserRequestEventHandler(
    default_data={
        'salt': "user-signout"
    },
    expected_data=(
            'salt',
            'timestamp',
            'token'
    ))
def signout(event):
    user = event.auth
    if not user:
        raise RuntimeError("No user retrieved during logout process!")
    user.save(DataStore)
    user.delete_cache(DataStore)
    EventServer.emit(event.ok_response(), event.client)
