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
        self.deleteIndex('foobar_target')
        self.deleteIndex('foobar')
        self.deleteIndex(Token.get_es_index())

    def test_es_create_documents(self):
        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.RUBBER['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token)

        # Dry run.
        call_command('es_create_documents', dry_run=True)
        self.assertDocDoesntExist(token)

        call_command('es_create_documents')
        self.assertDocExists(token)

        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create(name='raise_exception')
        settings.RUBBER['OPTIONS']['disabled'] = False

        call_command('es_create_documents')
        self.assertDocDoesntExist(token)

    def test_es_create_indices(self):
        # Dry run.
        call_command('es_create_indices', dry_run=True)
        self.assertIndexDoesntExist(Token.get_es_index())

        call_command('es_create_indices')
        self.assertIndexExists(Token.get_es_index())

        # Skip already created indices silently.
        call_command('es_create_indices')
