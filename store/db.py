"""

"""

from pymongo import MongoClient as DBClient
from pymongo.errors import DuplicateKeyError
import types
import uuid


def db(host='localhost', port=27017, database='zimmed_test',
       model_transform=(lambda rules, data: data)):

    if not hasattr(db, '_database'):
        db._database = DBClient(host, port)[database]
        db._transform = model_transform
        db.__call__ = lambda *args, **kwargs: db

        def generate_uid(self, collection):
            uid = uuid.uuid4().hex
            while self.get_model(collection, uid):
                uid = uuid.uuid4().hex
            return uid

        def model_to_document(self, model):
            return {
                '__rules__': model.json_rules,
                '__data__': dict(model)
            }

        def document_to_model(self, document):
            return self._transform(document['__rules__'], document['__data__'])

        def col(self, collection):
            if collection not in self._database.collection_names():
                self._database[collection].create_index('uid')
            return self._database[collection]

        def insert_model(self, collection, model):
            document = {
                '__rules__': model.json_rules,
                '__data__': dict(model)
            }
            document = dict(model)
            document['__rules__'] = model.json_rules
            collection = self.col(collection)
            collection.insert_one(document)

        def update_model(self, collection, model):
            document = dict(model)
            uid = document['uid']
            del document['uid']
            collection = self.col(collection)
            collection.update_one({'uid': uid}, {
                '$set': document
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
            return collection.find_one({'uid': uid})

        def get_model(self, collection, uid):
            collection = self.col(collection)
            document = collection.find_one({'uid': uid})
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
            collection.delete_one({'uid': uid})

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

    return db