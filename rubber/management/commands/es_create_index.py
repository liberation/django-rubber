"""
Management command for rubber.
"""
from optparse import make_option
import os
import sys

from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):
    required_options = ['index']
    option_list = ESBaseCommand.option_list + (
        make_option(
            '--index',
            action='store',
            type='string',
            dest='index',
            help=(
                "Create an index using the corresponding config file stored "
                "in CONFIG_ROOT."
            )
        ),
    )

    def run(self, *args, **options):
        config_path = os.path.join(
            self.rubber_config.config_root,
            '{0}.json'.format(self.index)
        )
        self.print_info(u"Using config file : {0}".format(config_path))
        body = None
        try:
            with open(config_path, 'r') as f:
                body = f.read()
        except IOError:
            self.print_error("Config file does not exist.")
            sys.exit(1)
        self.rubber_config.es.indices.create(index=self.index, body=body)
        self.print_success("Index created.")
