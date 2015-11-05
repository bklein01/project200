"""Package short description.

Package long description.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:


"""

from . import *
import importlib
import pkgutil
import inspect
from server.exception import BadRequestError
from server.auth import auth_guest


def hook_events(router):
    """Call from main.

    :param router: EventRouter
    """
    _expose_package(__name__, router)


class EventHandler(object):
    """Function decorator for event handlers.

    Usage:
        @EventHandler([value1[, value2[, ...]]])

    Example:
        @EventHandler(10, 'ten')
        def user_action(event, num, name):
            # num == 10, name == 'ten'
    """

    auth = auth_guest

    def __init__(self, *args, **kwargs):
        self.args_list = args
        self.expected_data = kwargs.get('expected_data')

    def __call__(self, handler):
        def wrapped(event, *args):
            if self.expected_data:
                if not hasattr(event, 'data'):
                    raise BadRequestError('SocketEvent data expected but not '
                                          'received.')
                for k in event.data.iterkeys():
                    if k not in self.expected_data:
                        raise BadRequestError('SocketEvent data key `' + k +
                                              '` expected but not received.')
            event.auth = None
            if 'token' in event.data and not event.auth:
                event.auth = self.__class__.auth(event)
            handler(event, *args)
            handler.next(event)
        wrapped.args_list = self.args_list
        wrapped.event_handler = True
        return wrapped


def _add_events(module, name, router):
    event_base = name.replace(__name__ + '.', '').replace('.', '-')
    functions = [item for item in inspect.getmembers(module)
                 if (inspect.isfunction(item[1]) and
                     hasattr(item[1], 'event_handler'))]
    for key, func in functions:
        if key is '__default__' or key is module.__name__:
            event = ''
        else:
            event = '-' + key.replace('_', '-')
        args = func.args_list
        del func.args_list
        del func.event_handler
        router.on(event_base + event, func, *args)


def _expose_package(package_name, router):
    """Recursively traverse package and subpackages to expose modules.

    Based on `Brian Visel's` answer to the StackOverflow.com question:
    http://stackoverflow.com/questions/3365740/how-to-import-all-submodules

    :param package_name: str -- Name of package.
    :param router: EventRouter -- The router to hook into.
    """
    package = importlib.import_module(package_name)
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package_name + '.' + name
        module = importlib.import_module(full_name)
        _add_events(module, full_name, router)
        if is_pkg:
            _expose_package(full_name, router)


# ----------------------------------------------------------------------------
__version__ = 0.2
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
