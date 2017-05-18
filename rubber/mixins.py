"""
Mixins for rubber.
"""
import logging
import inspect

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
    es_serializers = None

    @classmethod
    def get_indexable_queryset(cls):
        return cls._default_manager.all()

    @classmethod
    def get_es_doc_type(cls):
        return cls.__name__.lower()

    def get_es_serializers(self):
        return self.es_serializers

    def get_es_indices(self):
        return self.get_es_serializers().keys()

    def get_es_body(self, index):
        serializer = self.get_es_serializers().get(index)
        if inspect.ismethod(serializer):
            return serializer()
        return serializer(self).data

    def is_indexable(self):
        return True

    def get_es_doc(self, index):
        if not self.pk:
            return None
        return rubber_config.es.get(
            index=index,
            doc_type=self.get_es_doc_type(),
            id=self.pk
        )

    def es_index(self, async=True, countdown=0, indices=None, queue=None):
        if rubber_config.is_disabled or not self.is_indexable():
            return

        queue = queue or rubber_config.celery_queue
        content_type = ContentType.objects.get_for_model(self)
        indices = indices or self.get_es_indices()

        for index in indices:
            if async:
                es_index_object.apply_async(
                    args=(index, content_type.pk, self.pk),
                    countdown=countdown,
                    queue=queue
                )
            else:
                if rubber_config.should_fail_silently:
                    es_index_object.apply(
                        args=(index, content_type.pk, self.pk)
                    )
                else:
                    es_index_object.run(index, content_type.pk, self.pk)

    def es_delete(self, async=True, indices=None, queue=None):
        if rubber_config.is_disabled:
            return

        doc_type = self.get_es_doc_type()
        queue = queue or rubber_config.celery_queue
        indices = indices or self.get_es_indices()

        for index in indices:
            if async:
                es_delete_doc.apply_async(
                    args=(index, doc_type, self.pk),
                    queue=queue
                )
            else:
                if rubber_config.should_fail_silently:
                    es_delete_doc.apply((index, doc_type, self.pk))
                else:
                    es_delete_doc.run(index, doc_type, self.pk)
