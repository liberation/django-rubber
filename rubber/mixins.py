"""
Mixins for rubber.
"""
import logging
import json

from elasticsearch_dsl.serializer import serializer as dsl_serializer

from rubber import get_rubber_config
from rubber.tasks import es_bulk

logger = logging.getLogger(__name__)
rubber_config = get_rubber_config()


class ESIndexableMixin(object):
    """
    Provide the required methods and attributes to index django models.
    """
    es_indexers = {}
    es_reference_date = 'modified_at'

    @classmethod
    def get_indexable_queryset(cls):
        return cls._default_manager.all()

    def get_es_indexers(self):
        return self.es_indexers

    def is_indexable(self):
        return True

    def get_es_doc(self, indexer_key):
        if not self.pk:
            return None
        indexer = self.get_es_indexers()[indexer_key]
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

    def get_es_index_body(self):
        requests = []
        for _, indexer in self.get_es_indexers().iteritems():
            if 'dsl_doc_type' in indexer:
                doc = indexer['dsl_doc_type_mapping']()
                requests.append({
                    'index': {
                        '_index': doc._doc_type.index,
                        '_type': doc._doc_type.name,
                        '_id': self.pk
                    }
                })
                requests.append(doc)
            else:
                index = indexer['index']
                doc_type = indexer['doc_type']
                body = indexer['serializer'](self).data
                requests.append({
                    'index': {
                        '_index': index,
                        '_type': doc_type,
                        '_id': self.pk
                    }
                })
                requests.append(body)
        return u"\n".join([
            dsl_serializer.dumps(request) for request in requests
        ])

    def get_es_delete_body(self):
        requests = []
        for _, indexer in self.get_es_indexers().iteritems():
            if 'dsl_doc_type' in indexer:
                index = indexer['dsl_doc_type']._doc_type.index
                doc_type = indexer['dsl_doc_type']._doc_type.name
            else:
                index = indexer['index']
                doc_type = indexer['doc_type']
            requests.append({
                'delete': {
                    '_index': index,
                    '_type': doc_type,
                    '_id': self.pk
                }
            })
        return u"\n".join([json.dumps(request) for request in requests])

    def es_index(self, async=True, countdown=0):
        if rubber_config.is_disabled or not self.is_indexable():
            return
        try:
            body = self.get_es_index_body()
        except:
            if rubber_config.should_fail_silently:
                logger.error(
                    "Exception occured in es_index.",
                    exc_info=True,
                )
                return False
            else:
                raise
        if async:
            es_bulk.apply_async(
                args=(body,),
                countdown=countdown,
                queue=rubber_config.celery_queue
            )
        else:
            if rubber_config.should_fail_silently:
                es_bulk.apply(args=(body,))
            else:
                es_bulk.run(body)
        return True

    def es_delete(self, async=True):
        if rubber_config.is_disabled:
            return
        body = self.get_es_delete_body()
        if async:
            es_bulk.apply_async(
                args=(body,),
                queue=rubber_config.celery_queue
            )
        else:
            if rubber_config.should_fail_silently:
                es_bulk.apply((body,))
            else:
                es_bulk.run(body)
