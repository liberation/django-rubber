"""
Celery tasks for rubber.
"""
import logging

from django.contrib.contenttypes.models import ContentType

from celery import shared_task

from rubber import get_rubber_config


logger = logging.getLogger(__name__)
rubber_config = get_rubber_config()


@shared_task
def es_bulk(body, fail_silently=None):
    if fail_silently is None:
        fail_silently = rubber_config.should_fail_silently
    try:
        rubber_config.es.bulk(body=body)
    except:
        if fail_silently:
            logger.error(
                "Exception occured in es_bulk.",
                exc_info=True,
                extra={'body': body}
            )
        else:
            raise


@shared_task
def es_index_object(content_type_id, object_id, fail_silently=None):
    if fail_silently is None:
        fail_silently = rubber_config.should_fail_silently
    try:
        content_type = ContentType.objects.get_for_id(content_type_id)
        obj = content_type.model_class()._default_manager.get(pk=object_id)
        if not obj.is_indexable():
            return
        rubber_config.es.bulk(body=obj.get_es_index_body())
    except:
        if fail_silently:
            logger.error(
                "Exception occured while indexing object.",
                exc_info=True,
                extra={
                    'content_type_id': content_type_id,
                    'object_id': object_id,
                }
            )
        else:
            raise
