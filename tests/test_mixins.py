"""
Test mixins for rubber.
"""
from django.conf import settings

from rubber.mixins import ESIndexableMixin
from rubber import get_rubber_config

from tests.base import BaseTestCase
from tests.models import Token

rubber_config = get_rubber_config()


class TestMixins(BaseTestCase):

    def setUp(self):
        super(TestMixins, self).setUp()
        self.createIndex('index_1')
        self.createIndex('index_2')
        self.refresh()

    def tearDown(self):
        super(TestMixins, self).tearDown()
        self.deleteIndex('index_1')
        self.deleteIndex('index_2')

    def test_is_indexable(self):
        self.assertTrue(ESIndexableMixin().is_indexable())

    def test_get_indexable_queryset(self):
        self.assertEqual(
            str(Token.get_indexable_queryset().query),
            str(Token.objects.all().query)
        )

    def test_get_es_doc(self):
        token = Token()
        self.assertIsNone(token.get_es_doc(0))
        self.assertIsNone(token.get_es_doc(1))
        token.save()
        self.assertIsNotNone(token.get_es_doc(0))
        self.assertIsNotNone(token.get_es_doc(1))

    def test_es_index(self):
        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create()
        settings.RUBBER['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        # Async
        token.es_index()
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)

        token.es_delete()
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        # Sync
        token.es_index(async=True)
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)

        token = Token.objects.create(name='not_indexable')
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        settings.RUBBER['OPTIONS']['disabled'] = True
        token = Token.objects.create(name='raise_exception')
        settings.RUBBER['OPTIONS']['disabled'] = False
        # Async silent fail.
        token.es_index()
        # Sync silent fail.
        token.es_index(async=False)
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        settings.RUBBER['OPTIONS']['fail_silently'] = False
        # Async hard fail.
        with self.assertRaises(RuntimeError):
            token.es_index()
        # Sync hard fail.
        with self.assertRaises(RuntimeError):
            token.es_index(async=False)
        settings.RUBBER['OPTIONS']['fail_silently'] = True

    def test_es_delete(self):
        # Async call.
        token = Token.objects.create(name='token')
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)
        token.es_delete()
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        # Sync call.
        token = Token.objects.create(name='token')
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)
        token.es_delete(async=False)
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        # Async soft fail if document doesn't exist.
        token.es_delete()

        # Sync soft fail.
        token.es_delete(async=False)

        # Async hard fail.
        settings.RUBBER['OPTIONS']['fail_silently'] = False
        token.es_delete(async=False)
        settings.RUBBER['OPTIONS']['fail_silently'] = True

    def test_save(self):
        token = Token(name='token')

        settings.RUBBER['OPTIONS']['disabled'] = True
        token.save()
        settings.RUBBER['OPTIONS']['disabled'] = False
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

        token.save()
        doc = token.get_es_doc(0)
        self.assertEqual(doc['_source']['name'], 'token')
        self.assertEqual(doc['_id'], str(token.pk))

        # Update model and synchronise doc.
        token.name = 'kento'
        token.save()
        self.refresh()
        doc = token.get_es_doc(0)
        self.assertEqual(doc['_source']['name'], 'kento')

        # Instance is not indexable.
        token = Token.objects.create(name='not_indexable')
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)

    def test_delete(self):
        token = Token.objects.create(name='token')
        token_id = token.pk
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)

        settings.RUBBER['OPTIONS']['disabled'] = True
        token.delete()
        settings.RUBBER['OPTIONS']['disabled'] = False
        token.id = token_id
        self.assertDocExists(token, 0)
        self.assertDocExists(token, 1)

        token.save()
        token_id = token.pk
        token.delete()
        token.id = token_id
        self.assertDocDoesntExist(token, 0)
        self.assertDocDoesntExist(token, 1)
