"""
Management command for rubber.
"""
from rubber.management.base import ESBaseCommand


class Command(ESBaseCommand):
    help = (
        "Create alias from {0}{1}INDEX{2} to {0}{1}TARGET{2}."
    ).format(ESBaseCommand.BOLD, ESBaseCommand.UNDERLINE, ESBaseCommand.RESET)

    option_list = ESBaseCommand.option_list + (
        ESBaseCommand.options['index'],
        ESBaseCommand.options['target'],
    )
    required_options = ('index', 'target')

    def run(self, *args, **options):
        if not self.dry_run:
            self.rubber_config.es.indices.put_alias(
                index=self.target,
                name=self.index
            )
        self.print_success(
            u"Created alias from '{0}' to '{1}'.".format(
                self.index,
                self.target
            )
        )
