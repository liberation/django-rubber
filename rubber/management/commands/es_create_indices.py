"""
Management command for rubber.
"""
from elasticsearch.exceptions import RequestError

from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = "Create indices."

    def run(self, *args, **options):
        for model in self.rubber_config.indexable_models:
            index = model.get_es_index()
            mapping = model.get_es_doc_type_mapping()
            body = {'mapping': mapping}
            if not self.dry_run:
                try:
                    self.rubber_config.es.indices.create(
                        index=index,
                        body=body
                    )
                except RequestError as exc:
                    if exc.error == 'index_already_exists_exception':
                        self.print_warning(
                            u"Index already exists: '{0}'.".format(index)
                        )
                else:
                    self.print_success(
                        u"New index created: '{0}'.".format(index)
                    )
