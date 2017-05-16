"""
Test management commands for rubber.
"""
from django.conf import settings
from django.core.management import call_command

from tests.base import BaseTestCase
from tests.models import Token


class TestCommands(BaseTestCase):

    def tearDown(self):
        super(TestCommands, self).tearDown()
        # Delete remnants of previous tests.
        self.deleteIndex('index_1')
        self.deleteIndex('index_2')

    def test_es_create_documents(self):
        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.RUBBER['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token, 'index_1')
        self.assertDocDoesntExist(token, 'index_2')

        # Dry run.
        call_command('es_create_documents', dry_run=True)
        self.assertDocDoesntExist(token, 'index_1')
        self.assertDocDoesntExist(token, 'index_2')

        call_command('es_create_documents')
        self.assertDocExists(token, 'index_1')
        self.assertDocExists(token, 'index_2')

        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create(name='raise_exception')
        settings.RUBBER['OPTIONS']['disabled'] = False

        call_command('es_create_documents')
        self.assertDocDoesntExist(token, 'index_1')
        self.assertDocDoesntExist(token, 'index_2')

    # def test_es_create_indices(self):
    #     # Dry run.
    #     call_command('es_create_indices', dry_run=True)
    #     self.assertIndexDoesntExist(Token.get_es_index())
    #
    #     call_command('es_create_indices')
    #     self.assertIndexExists(Token.get_es_index())
    #
    #     # Skip already created indices silently.
    #     call_command('es_create_indices')
