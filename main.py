"""

"""

from server.event import (SocketServerEvent,
                          SocketConnectEvent,
                          SocketDisconnectEvent)
from server.router import EventRouter
from server import EventServer
from store import DataStore
from store.user import User
import sys

user_map = {}


def main():

    EventRouter.on('connect')

    try:
        EventRouter.listen_sync(empty=EventServer.is_empty,
                                get=EventServer.get_event)
    except KeyboardInterrupt:
        sys.exit(0)
