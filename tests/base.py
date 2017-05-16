"""
Base test case for rubber.
"""
from django.test import TransactionTestCase

from rubber import get_rubber_config

rubber_config = get_rubber_config()


class BaseTestCase(TransactionTestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.rubber_config = rubber_config

    def refresh(self):
        rubber_config.es.indices.refresh('_all')

    def docExists(self, obj, index, doc_id=None):
        doc_type = obj.get_es_doc_type()
        return rubber_config.es.exists(
            index=index,
            doc_type=doc_type,
            id=doc_id or obj.pk
        )

    def aliasExists(self, index, name):
        return rubber_config.es.indices.exists_alias(
            index=index, name=name)

    def indexExists(self, index):
        return rubber_config.es.indices.exists(index=index)

    def typeExists(self, index, doc_type):
        return rubber_config.es.indices.exists_type(
            index=index,
            doc_type=doc_type
        )

    def assertAliasExists(self, index, name):
        self.assertTrue(self.aliasExists(index, name))

    def assertAliasDoesntExist(self, index, name):
        self.assertFalse(self.aliasExists(index, name))

    def assertIndexExists(self, index):
        self.assertTrue(self.indexExists(index))

    def assertIndexDoesntExist(self, index):
        self.assertFalse(self.indexExists(index))

    def assertTypeExists(self, index, doc_type):
        self.assertTrue(self.typeExists(index, doc_type))

    def assertTypeDoesntExist(self, index, doc_type):
        self.assertFalse(self.typeExists(index, doc_type))

    def assertDocExists(self, obj, index, doc_id=None):
        self.assertTrue(self.docExists(obj, index, doc_id))

    def assertDocDoesntExist(self, obj, index, doc_id=None):
        self.assertFalse(self.docExists(obj, index, doc_id))

    def createIndex(self, index):
        rubber_config.es.indices.create(index=index)
        self.refresh()

    def deleteIndex(self, index):
        rubber_config.es.indices.delete(index=index, ignore=404)
        self.refresh()
