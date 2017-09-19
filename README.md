<p align="center">
  <img src="https://user-images.githubusercontent.com/1875772/30591968-42b837e8-9d45-11e7-9e86-3ded06fd896e.png">
</p>

Rubber provides you with tools to easily setup, manage and index your Django models in ElasticSearch. It relies on **celery** and **elasticsearch_dsl** (for backward compatibility purposes).

It is designed to allow simultaneous indexing of an object on different indices.

This project is a mutation of [django-trampoline](https://github.com/liberation/django-trampoline).

## Settings

Add `rubber` to your `INSTALLED_APPS`.

Define the following setting:
```python
RUBBER = {
    'HOSTS': ['localhost:9200'],
    'MODELS': [
        'tests.models.Token'
    ],
    'CONFIG_ROOT': os.path.join(SITE_ROOT, 'es_configs'),
    'OPTIONS': {
        'disabled': False,
        'fail_silently': True,
        'celery_queue': None
    },
}
```

### OPTIONS

#### celery_queue

`None` by default.

Specify which Celery queue should handle your indexation tasks.

#### fail_silently

`True` by default.

If `fail_silently` is `True` exceptions raised while indexing are caught and logged without being re-raised.

#### disabled

`False` by default.

## ESIndexableMixin

```python
from rubber.mixins import ESIndexableMixin
```

In order to make your model indexable you must make it inherit from `ESIndexableMixin` and implement a few things.

#### get_es_indexers() (required)

Return a dictionnary of indexers to be used for this model.

```python
def get_es_indexers(self):
    return {
        'INDEX_1': {
            'version': 1,
            'index': 'index_1',
            'serializer': Serializer,
            'doc_type': 'token'
        },
        'INDEX_2': {
            'version': 1,
            'dsl_doc_type': DocType,
            'dsl_doc_type_mapping': self.dsl_doc_type_mapping
        },
    }
```

Whenever an object is saved it will be indexed in both **index_1_v1** and **index_2_v1**.

- **INDEX_1** uses a serializer class to map the object's properties to a JSON serializable dictionnary.
It takes the object instance as its first argument and implements the `data` property.

For example:
```python
class Serializer(object):

    def __init__(self, token, *args, **kwargs):
        self.token = token

    @property
    def data(self):
        return {
            'name': self.token.name,
            'number': self.token.number,
            'multi': ['item_1', 'item_2']
        }
```

- **INDEX_2** uses a DocType from `elasticsearch_dsl` and a method returning a mapped instance of it.
This solution is only there for backward compatibility with the older system.

#### is_indexable() (optional)

```python
def is_indexable(self):
    return True
```

Tell whether a particular instance of the model should be indexed or skipped (defaults to true).

#### get_indexable_queryset() (optional)

```python
@classmethod
def get_indexable_queryset(cls):
    return []
```

Return the list of contents that should be indexed for this model using the command `es_create_documents()` defined bellow. Remember to use the `classmethod` decorator.

#### es_reference_date (optional)

Reference date used by the command `es_create_documents --from` option. Defaults to `modified_at`.

## Mapping

## Management commands

All management commands accept the following arguments:
- **--help**: Display an help message and the available arguments for the command.

### es_create_index

Create the indices passed as arguments using the mappings defined inside `CONFIG_ROOT`.

Following the previous example for `get_es_serializers` you would need to create two files `index_1_v1.json` and `index_2_v1` inside `CONFIG_ROOT`. Remember to include the version in your index name.

You would then run the command: `es_create_index index_1_v1 index_2_v1`.

### es_create_documents

Create documents based on the method `get_es_indexers()` on the related models.

Arguments:
- **--models** *(optional)*: Comma separated list of models to be indexed. It must match at least one of the models defined in RUBBER settings. Defaults to all.
- **--from** *(optional)*: Filter queryset by date. Must be formatted as YYYY-MM-DDTHH:MM:SS.
- **--show-tqdm** *(optional)*: Show the tqdm progress bar.
- **--dry-run** *(optional)*: Run the command in dry run mode without actually commiting anything.

