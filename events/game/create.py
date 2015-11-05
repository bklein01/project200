"""`user-register` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import GameActionEventHandler
from server import EventServer
from store import DataStore
from game import Game


@GameActionEventHandler(
    expected_data=('options',
                   'salt',
                   'timestamp',
                   'token'
                   ))
def register(event):
    user = event.auth
    if not user:
        raise RuntimeError("No new user created during registration!")
    game = Game.new(user, DataStore, event.data.get('options', None))

