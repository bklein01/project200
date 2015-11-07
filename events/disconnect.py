"""`disconnect` event handler(s).

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>
"""

from . import EventHandler
from store import DataStore
from store.user import User


@EventHandler()
def disconnect(event):
    user = User.get_user_by_client(DataStore, event.client)
    if user:
        user.save_session(event.client_ip)
        user.save(DataStore)
        user.delete_cache(DataStore)
    # No response for disconnect.
