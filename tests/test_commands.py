"""
Test management commands for rubber.
"""
from django.conf import settings
from django.core.management import call_command

from tests.base import BaseTestCase
from tests.models import Token


class TestCommands(BaseTestCase):

    def setUp(self):
        super(TestCommands, self).setUp()
        self.createIndex('index_1')
        self.createIndex('index_2')
        self.refresh()

    def tearDown(self):
        super(TestCommands, self).tearDown()
        # Delete remnants of previous tests.
        self.deleteIndex('index_1')
        self.deleteIndex('index_2')

    def test_es_create_documents_models(self):
        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.RUBBER['OPTIONS']['disabled'] = False

        call_command('es_create_documents', models='YOLO')
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        call_command('es_create_documents', models='tests.models.Token')
        self.assertDocExists(token, 1)
        self.assertDocExists(token, 1)

    def test_es_create_documents_from(self):
        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.RUBBER['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        with self.assertRaises(SystemExit):
            call_command('es_create_documents', from_date='foobar')

        call_command('es_create_documents', from_date='2008-09-03T20:56:35')

    def test_es_create_documents(self):
        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.RUBBER['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        # Dry run.
        call_command('es_create_documents', dry_run=True)
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        call_command('es_create_documents')
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)

        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create(name='raise_exception')
        settings.RUBBER['OPTIONS']['disabled'] = False

        call_command('es_create_documents')
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

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
