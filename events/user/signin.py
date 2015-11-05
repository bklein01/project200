"""`user-signin` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import UserLoginEventHandler
from server import EventServer


@UserLoginEventHandler(
    expected_data=('username',
                   'timestamp',
                   'token'
                   ))
def signin(event):
    user = event.auth
    if not user:
        raise RuntimeError("No new user created during login!")
    EventServer.emit(event.ok_response(**user.filter('private')))
