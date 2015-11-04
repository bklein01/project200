"""

"""

from pymongo import MongoClient as DBClient
from pymongo.errors import DuplicateKeyError, InvalidDocument
import types
import uuid
from core.datamodel import DataModel


class DBLookupError(ValueError):
    pass


def db(host='localhost', port=27017, database='zimmed_test'):

    if not hasattr(db, '_database'):
        db._database = DBClient(host, port)[database]
        db.__call__ = lambda *args, **kwargs: db

        def generate_uid(self, collection):
            uid = uuid.uuid4().hex
            while self.get_model(collection, uid):
                uid = uuid.uuid4().hex
            return uid

        def unparse_model(self, item):
            if isinstance(item, dict):
                for k, v in item.iteritems():
                    if isinstance(v, (list, tuple, dict, DataModel)):
                        item[k] = self.unparse_model(v)
            elif isinstance(item, (list, set, tuple)):
                for v in item:
                    if isinstance(v, (list, tuple, dict, DataModel)):
                        i = item.index(v)
                        item[i] = self.unparse_model(v)
            elif isinstance(item, DataModel):
                uid = None
                collection = None
                if item is not DataModel.Null:
                    uid = item.uid
                    collection = item['_collection']
                    self.upsert_model(collection, item)
                return {
                    '__sub_document__': True,
                    '__collection__': collection,
                    '__uid__': uid
                }
            return item

        def parse_model(self, doc):
            if isinstance(doc, dict):
                doc = dict(((str(k), v) for k, v in doc.iteritems()))
                if '__sub_document__' in doc:
                    if not doc['__uid__']:
                        doc = DataModel.Null
                    else:
                        doc = self.get_model(doc['__collection__'],
                                             doc['__uid__'])
                else:
                    for k, v in doc.iteritems():
                        if isinstance(v, (unicode, tuple, list, dict)):
                            doc[k] = self.parse_model(v)
            elif isinstance(doc, (tuple, list)):
                for v in doc:
                    if isinstance(v, (unicode, tuple, list, dict)):
                        i = doc.index(v)
                        doc[i] = self.parse_model(v)
            elif isinstance(doc, unicode):
                doc = str(doc)
            return doc

        def model_to_document(self, model):
            doc = self.unparse_model(dict(model))
            return {
                '_id': model.uid,
                '__rules__': model.bson_rules,
                '__data__': doc
            }

        def document_to_model(self, document):
            data = self.parse_model(document['__data__'])
            rules = document['__rules__']
            return DataModel.load(rules, data)

        def col(self, collection):
            # if collection not in self._database.collection_names():
            #     self._database[collection].create_index('uid')
            return self._database[collection]

        def insert_model(self, collection, model):
            document = self.model_to_document(model)
            collection = self.col(collection)
            collection.insert_one(document)

        def update_model(self, collection, model):
            document = self.model_to_document(model)['__data__']
            uid = document['uid']
            del document['uid']
            collection = self.col(collection)
            collection.update_one({'_id': uid}, {
                '$set': {'__data__': document}
            })

        def upsert_model(self, collection, model):
            try:
                self.insert_model(collection, model)
            except DuplicateKeyError:
                self.update_model(collection, model)

        def insert_models(self, collection, models):
            for m in models:
                self.insert_model(collection, m)

        def update_models(self, collection, models):
            for m in models:
                self.update_model(collection, m)

        def upsert_models(self, collection, models):
            for m in models:
                self.upsert_model(collection, m)

        def get_model_data(self, collection, uid):
            collection = self.col(collection)
            return collection.find_one({'_id': uid})['__data__']

        def get_model(self, collection, uid):
            collection = self.col(collection)
            document = collection.find_one({'_id': uid})
            if document:
                return self.document_to_model(document)
            return None

        def get_models(self, collection, **kwargs):
            collection = self.col(collection)
            documents = collection.find(kwargs)
            if documents:
                return [self.document_to_model(d) for d in documents]
            return []

        def remove_model(self, collection, uid):
            collection = self.col(collection)
            collection.delete_one({'_id': uid})

        def remove_models(self, collection, **kwargs):
            collection = self.col(collection)
            collection.delete_many(kwargs)

        db.generate_uid = types.MethodType(generate_uid, db)
        db.document_to_model = types.MethodType(document_to_model, db)
        db.model_to_document = types.MethodType(model_to_document, db)
        db.col = types.MethodType(col, db)
        db.insert_model = types.MethodType(insert_model, db)
        db.upsert_model = types.MethodType(upsert_model, db)
        db.update_model = types.MethodType(update_model, db)
        db.insert_models = types.MethodType(insert_models, db)
        db.upsert_models = types.MethodType(upsert_models, db)
        db.update_models = types.MethodType(update_models, db)
        db.get_model_data = types.MethodType(get_model_data, db)
        db.get_model = types.MethodType(get_model, db)
        db.get_models = types.MethodType(get_models, db)
        db.remove_model = types.MethodType(remove_model, db)
        db.remove_models = types.MethodType(remove_models, db)
        db.parse_model = types.MethodType(parse_model, db)
        db.unparse_model = types.MethodType(unparse_model, db)

    return db
