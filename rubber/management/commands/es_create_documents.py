"""
Management command for rubber.
"""
from tqdm import tqdm

from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = "Create documents."

    def run(self, *args, **options):
        for model in self.rubber_config.indexable_models:
            self.print_info(u"Indexing model: '{0}'.".format(model.__name__))
            queryset = model.get_indexable_queryset()
            progress = tqdm(total=queryset.count(), dynamic_ncols=True)
            for obj in queryset:
                if not self.dry_run:
                    try:
                        obj.es_index(async=False)
                    except Exception as exc:
                        print exc
                progress.update()
