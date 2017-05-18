"""
Models for rubber tests.
"""
from django.db import models

from rubber.mixins import ESIndexableMixin


class TokenSerializer(object):

    def __init__(self, token, *args, **kwargs):
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
            'index_2': self.serializer_as_method
        }

    def serializer_as_method(self):
        return {
            'name': self.name,
            'number': self.number,
        }

    def is_indexable(self):
        if self.name == 'not_indexable':
            return False
        return True

    def get_es_body(self, index):
        if self.name == 'raise_exception':
            raise RuntimeError
        return super(Token, self).get_es_body(index)
