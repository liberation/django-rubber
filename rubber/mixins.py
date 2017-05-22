"""
Mixins for rubber.
"""
import logging

from django.contrib.contenttypes.models import ContentType

from rubber import get_rubber_config
from rubber.tasks import es_delete_doc
from rubber.tasks import es_index_object

logger = logging.getLogger(__name__)
rubber_config = get_rubber_config()


class ESIndexableMixin(object):
    """
    Provide the required methods and attributes to index django models.
    """
    es_indexers = []

    @classmethod
    def get_indexable_queryset(cls):
        return cls._default_manager.all()

    def get_es_indexers(self):
        return self.es_indexers

    def is_indexable(self):
        return True

    def get_es_doc(self, indexer_index):
        if not self.pk:
            return None
        indexer = self.get_es_indexers()[indexer_index]
        if 'dsl_doc_type' in indexer:
            index = indexer['dsl_doc_type']._doc_type.index
            doc_type = indexer['dsl_doc_type']._doc_type.name
        else:
            index = indexer['index']
            doc_type = indexer['doc_type']
        result = rubber_config.es.get(
            index=index,
            doc_type=doc_type,
            id=self.pk,
            ignore=404
        )
        if 'found' not in result or result['found'] is False:
            return None
        return result

    def es_index(self, async=True, countdown=0):
        if rubber_config.is_disabled or not self.is_indexable():
            return
        content_type = ContentType.objects.get_for_model(self)
        if async:
            es_index_object.apply_async(
                args=(content_type.pk, self.pk),
                countdown=countdown,
                queue=rubber_config.celery_queue
            )
        else:
            if rubber_config.should_fail_silently:
                es_index_object.apply(
                    args=(content_type.pk, self.pk)
                )
            else:
                es_index_object.run(content_type.pk, self.pk)

    def es_delete(self, async=True):
        if rubber_config.is_disabled:
            return
        for indexer in self.get_es_indexers():
            if 'dsl_doc_type' in indexer:
                index = indexer['dsl_doc_type']._doc_type.index
                doc_type = indexer['dsl_doc_type']._doc_type.name
            else:
                index = indexer['index']
                doc_type = indexer['doc_type']
            if async:
                es_delete_doc.apply_async(
                    args=(index, doc_type, self.pk),
                    queue=rubber_config.celery_queue
                )
            else:
                if rubber_config.should_fail_silently:
                    es_delete_doc.apply((index, doc_type, self.pk))
                else:
                    es_delete_doc.run(index, doc_type, self.pk)
