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

    class Meta:
        doc_type = 'token'


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
        }


class Token(ESIndexableMixin, models.Model):
    name = models.CharField(default='token', max_length=200)
    number = models.IntegerField(default=42)

    def __unicode__(self):
        return self.name

    def get_es_serializers(self):
        return {
            'index_1': TokenSerializer,
            'index_2': self.to_doc_type
        }

    def to_doc_type(self):
        if self.name == 'raise_exception':
            raise RuntimeError
        doc = TokenDocType()
        doc.name = self.name
        doc.number = self.number
        return doc

    def is_indexable(self):
        if self.name == 'not_indexable':
            return False
        return True
