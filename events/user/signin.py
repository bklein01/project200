"""`user-signin` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import UserLoginEventHandler
from server import EventServer
from server.event import SocketServerEvent


@UserLoginEventHandler(
    expected_data=('username',
                   'timestamp',
                   'token'
                   ))
def signin(event):
    user, old_client = event.auth
    if not user:
        raise RuntimeError("No new user created during login!")
    if old_client:
        EventServer.emit(SocketServerEvent('force-disconnect'))
    EventServer.emit(event.ok_response(**user.filter('private')))
