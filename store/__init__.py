"""Store package.

Contains all packages and modules dealing with user metadata.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:


"""

import uuid


class DocumentCollection(object):

    @classmethod
    def generate_id(cls):
        return uuid.uuid4().hex

    def __init__(self):
        self._documents = {}
        self._controllers = {}

    def remove(self, uid):
        del self._documents[uid]
        del self._controllers[uid]

    def new(self, document):
        uid = self.__class__.generate_id()
        while uid in self._documents.iterkeys():
            uid = self.generate_id()
        self._documents[uid] = document
        return uid

    def get(self, uid):
        return self._documents[uid]

    def new_controller(self, uid, ctrl):
        self._controllers[uid] = ctrl

    def get_controller(self, uid):
        return self._controllers[uid]

    def find(self, **kwargs):
        items = []
        for k, v in self._documents.iteritems():
            if 'uid' in kwargs.iterkeys() and k not in kwargs['uid']:
                continue
            del kwargs['uid']
            for attr, val in kwargs.iteritems():
                if isinstance(val, list) and v[attr] not in val:
                    continue
                elif isinstance(val, tuple) and val not in v[attr]:
                    continue
                elif v[attr] != val:
                    continue
            items.append(v)
        return items if items else None


class ModelStore(object):

    _DOCUMENT_COLLECTIONS = {}

    @classmethod
    def _key(cls, doc_type):
        if type(doc_type) is str:
            return doc_type
        elif type(doc_type) is type:
            return doc_type.__name__
        else:
            raise ValueError('Invalid doc_type supplied to ModelStore.')

    @classmethod
    def get_controller(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        try:
            return cls._DOCUMENT_COLLECTIONS[doc_type].get_controller(uid)
        except KeyError:
            return None

    @classmethod
    def set_controller(cls, doc_type, uid, ctrl):
        doc_type = cls._key(doc_type)
        if doc_type not in cls._DOCUMENT_COLLECTIONS:
            cls._DOCUMENT_COLLECTIONS[doc_type] = DocumentCollection()
        return cls._DOCUMENT_COLLECTIONS[doc_type].new_controller(uid, ctrl)

    @classmethod
    def insert(cls, doc_type, model):
        doc_type = cls._key(doc_type)
        if doc_type not in cls._DOCUMENT_COLLECTIONS:
            cls._DOCUMENT_COLLECTIONS[doc_type] = DocumentCollection()
        return cls._DOCUMENT_COLLECTIONS[doc_type].new(model)

    @classmethod
    def delete(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        try:
            cls._DOCUMENT_COLLECTIONS[doc_type].remove(uid)
        except KeyError:
            pass

    @classmethod
    def get(cls, doc_type, uid):
        doc_type = cls._key(doc_type)
        try:
            return cls._DOCUMENT_COLLECTIONS[doc_type].get(uid)
        except KeyError:
            return None

    @classmethod
    def find(cls, **kwargs):
        if 'doc_type' not in kwargs.iterkeys():
            raise ValueError('ModelStore.find expected `doc_type` parameter.')
        doc_type = cls._key(kwargs['doc_type'])
        del kwargs['doc_type']
        try:
            return cls._DOCUMENT_COLLECTIONS[doc_type].find(**kwargs)
        except KeyError:
            return None


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
