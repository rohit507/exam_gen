import logging
import coloredlogs

log = logging.getLogger(__name__)
field_styles = coloredlogs.DEFAULT_FIELD_STYLES
field_styles.update({ 'levelname': {'bold': True, 'color':'yellow'}})
coloredlogs.install(
    level='DEBUG',
    logger=log,
    fmt='%(levelname)s@%(name)s:%(lineno)s:\n%(message)s\n',
    field_styles = field_styles
)


__all__ = []
