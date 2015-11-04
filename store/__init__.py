"""Store package.

Contains all packages and modules dealing with user metadata.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:


"""

from .db import db
from core.datamodel import DataModelController, DataModel


class ControllerCollection(object):

    MAX_CACHE = 100

    def __init__(self, store, max_cache=None):
        if not max_cache:
            max_cache = self.__class__.MAX_CACHE
        self._max_cache = max_cache
        self._controllers = []
        self._ctrl_map = {}
        self._store = store

    def prune(self):
        while len(self._controllers) > self._max_cache:
            c = self._controllers.pop()
            del self._ctrl_map[c.uid]
            self._store.save(c.__class__, c.model)

    def shift_down(self, index):
        for k in self._ctrl_map.iterkeys():
            if self._ctrl_map[k] > index:
                self._ctrl_map[k] -= 1

    def shift_up(self):
        for k in self._ctrl_map.iterkeys():
            self._ctrl_map[k] += 1

    def insert(self, ctrl):
        if ctrl.uid in self._ctrl_map.iterkeys():
            return
        self._controllers.insert(0, ctrl)
        self.shift_up()
        self._ctrl_map[ctrl.uid] = 0
        self.prune()

    def get(self, uid):
        index = self._ctrl_map[uid]
        return self._controllers[index]

    def remove(self, uid):
        index = self._ctrl_map[uid]
        del self._controllers[index]
        del self._ctrl_map[uid]
        self.shift_down(index)


class DataStore(object):

    _CACHE = {}
    _db = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        return cls

    def __init__(self, db_host='localhsot',
                 db_port='27017',
                 db_name='zimmed-test1',
                 model_transform=(lambda rules, data: DataModel(rules, data))):
        if not self.__class__._db:
            self.__class__._db = db(db_host, db_port, db_name, model_transform)

    @classmethod
    def _key(cls, doc_type):
        if type(doc_type) is str:
            return doc_type
        elif type(doc_type) is type:
            return doc_type.__name__
        else:
            raise ValueError('Invalid doc_type supplied to ModelStore.')

    @classmethod
    def uid(cls, doc_type):
        doc_type = cls._key(doc_type)
        return cls._db.generate_uid(doc_type)

    @classmethod
    def get_controller(cls, doc_type, uid):
        if not issubclass(doc_type, DataModelController):
            raise TypeError("`doc_type` must be a sub class of "
                            "DataModelController.")
        key = cls._key(doc_type)
        ctrl = cls.get_strict_controller(key, uid)
        if not ctrl:
            model = cls.get_strict_model(key, uid)
            if not model:
                raise ValueError("Object does not exist.")
            ctrl = doc_type.restore(cls, model)
        return ctrl

    @classmethod
    def get_model(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        ctrl = cls.get_strict_controller(doc_type, uid)
        if ctrl:
            return ctrl.model
        return cls.get_strict_model(doc_type, uid)

    @classmethod
    def get_model_data(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        ctrl = cls.get_strict_controller(doc_type, uid)
        if ctrl:
            return dict(ctrl.model)
        return cls._db.get_model_data(doc_type, uid)

    @classmethod
    def get_strict_controller(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        try:
            return cls._CACHE[doc_type].get(uid)
        except KeyError:
            return None

    @classmethod
    def set_controller(cls, doc_type, ctrl):
        doc_type = cls._key(doc_type)
        if doc_type not in cls._CACHE:
            cls._CACHE[doc_type] = ControllerCollection(cls)
        return cls._CACHE[doc_type].insert(ctrl)

    @classmethod
    def delete_controller(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        try:
            cls._CACHE[doc_type].remove(uid)
            return True
        except KeyError:
            return False

    @classmethod
    def save(cls, doc_type, model):
        doc_type = cls._key(doc_type)
        cls._db.upsert_model(doc_type, model)

    @classmethod
    def store_model(cls, doc_type, model):
        doc_type = cls._key(doc_type)
        cls._db.insert_model(doc_type, model)

    @classmethod
    def update_model(cls, doc_type, model):
        doc_type = cls._key(doc_type)
        cls._db.update_model(doc_type, model)

    @classmethod
    def delete_model(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        cls._db.remove_model(doc_type, uid)

    @classmethod
    def get_strict_model(cls, doc_type, uid):
        return cls._db.get_model(doc_type, uid)


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
