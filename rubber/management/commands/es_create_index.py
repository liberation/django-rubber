"""
Management command for rubber.
"""
import os
import sys

from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):

    def run(self, *args, **options):
        if len(args) == 0:
            self.print_error("Please provide at least one index.")
            sys.exit(1)
        for index in args:
            config_path = os.path.join(
                self.rubber_config.config_root,
                '{0}.json'.format(index)
            )
            self.print_info(u"Using config file : {0}".format(config_path))
            body = None
            try:
                with open(config_path, 'r') as f:
                    body = f.read()
            except IOError:
                self.print_error("Config file does not exist.")
                continue
            self.rubber_config.es.indices.create(index=index, body=body)
            self.print_success(u"Index {0} created.".format(index))
