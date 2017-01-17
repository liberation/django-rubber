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
    es_serializer = None

    @classmethod
    def get_indexable_queryset(cls):
        return cls._default_manager.all()

    @classmethod
    def get_es_index(cls):
        return cls.__name__.lower()

    @classmethod
    def get_es_doc_type(cls):
        return cls.__name__.lower()

    @classmethod
    def get_es_doc_type_mapping(self):
        return {}

    def get_es_serializer(self):
        return self.es_serializer

    def get_es_body(self):
        serializer = self.get_es_serializer()
        return serializer(self).data

    def is_indexable(self):
        return True

    def get_es_doc(self):
        if not self.pk:
            return None
        return rubber_config.es.get(
            index=self.get_es_index(),
            doc_type=self.get_es_doc_type(),
            id=self.pk
        )

    def es_index(self, async=True, countdown=0, index=None, queue=None):
        if rubber_config.is_disabled or not self.is_indexable():
            return

        index = index or self.get_es_index()
        queue = queue or rubber_config.celery_queue
        content_type = ContentType.objects.get_for_model(self)

        if async:
            result = es_index_object.apply_async(
                args=(index, content_type.pk, self.pk),
                countdown=countdown,
                queue=queue
            )
        else:
            if rubber_config.should_fail_silently:
                result = es_index_object.apply(
                    args=(index, content_type.pk, self.pk)
                )
            else:
                result = es_index_object.run(index, content_type.pk, self.pk)
        return result

    def es_delete(self, async=True, index=None, queue=None):
        if rubber_config.is_disabled:
            return

        doc_type = self.get_es_doc_type()
        index = index or self.get_es_index()
        queue = queue or rubber_config.celery_queue

        if async:
            result = es_delete_doc.apply_async(
                args=(index, doc_type, self.pk),
                queue=queue
            )
        else:
            if rubber_config.should_fail_silently:
                result = es_delete_doc.apply((index, doc_type, self.pk))
            else:
                result = es_delete_doc.run(index, doc_type, self.pk)
        return result
