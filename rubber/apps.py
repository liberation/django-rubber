"""
App config for rubber.
"""
from copy import deepcopy
import collections

import logging
import six

from elasticsearch import Elasticsearch

from django.conf import settings
from django.db import transaction
from django.db.models.signals import class_prepared
from django.db.models.signals import post_delete
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)

try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object


DEFAULT_RUBBER = {
    'HOSTS': ['localhost:9200'],
    'MODELS': [],
    'CONFIG_ROOT': None,
    'OPTIONS': {
        'fail_silently': True,
        'disabled': False,
        'celery_queue': None
    },
}


def recursive_update(d, u):
    for k, v in six.iteritems(u):
        if isinstance(v, collections.Mapping):
            r = recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def post_save_es_index(sender, instance, **kwargs):
    if instance.is_indexable():
        try:
            # post_save fires after the save occurs but before the transaction
            # is commited.
            transaction.on_commit(lambda: instance.es_index())
        except AttributeError:
            # 1s countdown waiting for the transaction to complete.
            instance.es_index(countdown=1)


def post_delete_es_delete(sender, instance, **kwargs):
    instance.es_delete()


def class_prepared_check_indexable(sender, **kwargs):
    rubber_config = get_rubber_config()

    # Only register indexation signals for models defined in the settings.
    sender_path = '{0}.{1}'.format(sender.__module__, sender.__name__)
    if sender_path not in rubber_config.models_paths:
        return

    post_save.connect(
        post_save_es_index,
        sender=sender,
        weak=False,
        dispatch_uid='rubber_post_save_{0}'.format(sender.__name__)
    )
    post_delete.connect(
        post_delete_es_delete,
        sender=sender,
        weak=False,
        dispatch_uid='rubber_post_delete_{0}'.format(sender.__name__)
    )


class RubberConfig(AppConfig):
    name = 'rubber'
    verbose_name = "Rubber"

    def __init__(self, *args, **kwargs):
        class_prepared.connect(class_prepared_check_indexable)
        super(RubberConfig, self).__init__(*args, **kwargs)

    def ready(self):
        self._es = Elasticsearch(hosts=self.hosts)

    @property
    def settings(self):
        USER_RUBBER = getattr(settings, 'RUBBER', {})
        RUBBER = deepcopy(DEFAULT_RUBBER)
        return recursive_update(RUBBER, USER_RUBBER)

    @property
    def es(self):
        return self._es

    def get_models_from_paths(self, models_paths):
        models = []
        for model_path in models_paths:
            module_path, model_name = model_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[''])
            model = getattr(module, model_name)
            if model not in models:
                models.append(model)
        return models

    @property
    def indexable_models(self):
        return self.get_models_from_paths(self.models_paths)

    @property
    def hosts(self):
        return self.settings['HOSTS']

    @property
    def models_paths(self):
        return self.settings['MODELS']

    @property
    def should_fail_silently(self):
        return self.settings['OPTIONS']['fail_silently']

    @property
    def is_disabled(self):
        return self.settings['OPTIONS']['disabled']

    @property
    def celery_queue(self):
        return self.settings['OPTIONS']['celery_queue']

    @property
    def config_root(self):
        return self.settings['CONFIG_ROOT']

try:
    # Try to import AppConfig to check if this feature is available.
    from django.apps import AppConfig  # noqa
except ImportError:
    app_config = RubberConfig()
    app_config.ready()

    def get_rubber_config():
        return app_config
else:
    def get_rubber_config():
        from django.apps import apps
        return apps.get_app_config('rubber')
