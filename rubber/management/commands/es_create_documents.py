"""
Management command for rubber.
"""
from datetime import datetime
from optparse import make_option
import concurrent.futures as futures
import sys

from django.core.paginator import Paginator

from tqdm import tqdm

from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):
    option_list = ESBaseCommand.option_list + (
        make_option(
            '--show-tqdm',
            action='store_true',
            dest='show_tqdm',
            default=False,
            help="Show tqdm progress bar."
        ),
        make_option(
            '--from',
            action='store',
            type='string',
            dest='from_date',
            help=(
                "Filter queryset by date. "
                "Must be formatted as YYYY-MM-DDTHH:MM:SS."
            )
        ),
        make_option(
            '--models',
            action='store',
            type='string',
            dest='models',
            help=(
                "Comma separated list of models to be indexed. It must match "
                "at least one of the models defined in RUBBER settings."
            )
        ),
    )

    def get_models_paths(self):
        if not self.models:
            return self.rubber_config.models_paths
        models_paths = [
            model_path for model_path in self.rubber_config.models_paths
            if model_path in self.models.split(',')
        ]
        return models_paths

    def get_from_date(self):
        if not self.from_date:
            return None
        try:
            from_date = datetime.strptime(
                self.from_date,
                '%Y-%m-%dT%H:%M:%S'
            )
        except Exception as exc:
            self.print_error(exc)
            sys.exit(1)
        else:
            return from_date
        return None

    def run(self, *args, **options):
        from_date = self.get_from_date()
        if from_date is not None:
            self.print_info(u"Reference date : {0}".format(from_date))

        models_paths = self.get_models_paths()
        indexable_models = self.rubber_config.get_models_from_paths(
            models_paths)
        self.print_info(u"Models : {0}".format(indexable_models))

        for model in indexable_models:
            self.print_success(
                u"Indexing model: '{0}'.".format(model.__name__))
            queryset = model.get_indexable_queryset()

            if from_date is not None and model.es_reference_date is not None:
                filter_dict = {}
                filter_name = '{0}__gt'.format(model.es_reference_date)
                filter_dict[filter_name] = from_date
                queryset = queryset.filter(**filter_dict)

            max_bulk_size = 200
            paginator = Paginator(queryset, max_bulk_size)
            if self.show_tqdm:
                pbar = tqdm(total=paginator.count)
            else:
                total = 0
            executor = futures.ThreadPoolExecutor(max_workers=8)
            for page_number in paginator.page_range:
                page = paginator.page(page_number)
                tasks = [
                    executor.submit(lambda obj: obj.get_es_index_body(), obj)
                    for obj in page.object_list
                ]
                requests = []
                for task in futures.as_completed(tasks):
                    requests.append(task.result())
                    if self.show_tqdm:
                        pbar.update(1)
                try:
                    body = u"\n".join(requests)
                    if not self.dry_run:
                        self.rubber_config.es.bulk(body=body)
                except Exception as exc:
                    self.print_error(exc)
                if not self.show_tqdm:
                    total += len(page.object_list)
                    self.print_info(total)
            executor.shutdown()
            if self.show_tqdm:
                pbar.close()
