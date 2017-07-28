"""
Models for rubber tests.
"""
from django.db import models

from elasticsearch_dsl import DocType
from elasticsearch_dsl import String

from rubber.mixins import ESIndexableMixin


class TokenDocType(DocType):
    name = String()
    number = String()
    multi = String(multi=True)

    class Meta:
        doc_type = 'token'
        index = 'index_2'


class TokenSerializer(object):

    def __init__(self, token, *args, **kwargs):
        if token.name == 'raise_exception':
            raise RuntimeError
        self.token = token

    @property
    def data(self):
        return {
            'name': self.token.name,
            'number': self.token.number,
            'multi': ['item_1', 'item_2']
        }


class Token(ESIndexableMixin, models.Model):
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(default='token', max_length=200)
    number = models.IntegerField(default=42)

    def __unicode__(self):
        return self.name

    def get_es_indexers(self):
        return {
            'INDEX_1': {
                'version': 1,
                'index': 'index_1',
                'serializer': TokenSerializer,
                'doc_type': 'token'
            },
            'INDEX_2': {
                'version': 1,
                'dsl_doc_type': TokenDocType,
                'dsl_doc_type_mapping': self.dsl_doc_type_mapping
            },
        }

    def dsl_doc_type_mapping(self):
        if self.name == 'raise_exception':
            raise RuntimeError
        doc = TokenDocType()
        doc.name = self.name
        doc.number = self.number
        doc.multi.append('item_1')
        doc.multi.append('item_2')
        return doc

    def is_indexable(self):
        if self.name == 'not_indexable':
            return False
        return True
