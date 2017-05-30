"""
Celery tasks for rubber.
"""
import logging

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
