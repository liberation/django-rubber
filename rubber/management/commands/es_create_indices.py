"""
Management command for rubber.
"""
from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):

    def run(self, *args, **options):
        for model in self.rubber_config.indexable_models:
            index = model.get_es_index()
            doc_type = model.get_es_doc_type()
            mapping = model.get_es_doc_type_mapping()
            body = {'mappings': {}}
            body['mappings'][doc_type] = mapping
            if not self.dry_run:
                try:
                    self.rubber_config.es.indices.create(
                        index=index,
                        body=body
                    )
                except Exception as exc:
                    self.print_error(exc)
                else:
                    self.print_success(
                        "New index created: '{0}'.".format(index)
                    )
