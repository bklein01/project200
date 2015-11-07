"""`connect` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import EventHandler
from server import EventServer
from server.exception import UnauthorizedError
from store import DataStore
from store.user import User


@EventHandler()
def connect(event):
    EventServer.emit(event.ok_response(client_token=event.client), event.client)


@EventHandler(
    expected_data=(
        'uid',
        'session_token'
    ))
def restore(event):
    user = User.restore_session(event.client, event.client_ip,
                                event.data.uid, event.data.session_token,
                                DataStore)
    if not user:
        raise UnauthorizedError("Invalid/Expired Session.")
    EventServer.emit(event.ok_response(**user.filter('private')), event.client)
