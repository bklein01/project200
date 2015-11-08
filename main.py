"""

"""

import sys
from server import EventServer
from server.router import EventRouter
from events import hook_events
import logging
from store import DataStore


def main():
    DataStore()
    logging.basicConfig(level=logging.DEBUG)
    hook_events(EventRouter)
    EventServer.start()
    EventRouter.listen_sync(EventServer)
    return EventServer.stop()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print 'Standard shutdown failed. Using fail-safe shutdown.'
        sys.exit(1)
