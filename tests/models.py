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

    es_serializer = TokenSerializer

    def __unicode__(self):
        return self.name

    def is_indexable(self):
        if self.name == 'not_indexable':
            return False
        return True

    def get_es_body(self):
        if self.name == 'raise_exception':
            raise RuntimeError
        return super(Token, self).get_es_body()

    @classmethod
    def get_es_doc_type_mapping(self):
        return {
            'properties': {
                'name': {
                    'type': 'string'
                }
            }
        }
