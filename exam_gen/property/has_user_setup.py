import attr

from .buildable import Buildable
from exam_gen.util.user_setup import UserSetup

import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")


@attr.s
class HasUserSetup(Buildable, UserSetup):

    def setup_build(self, build_info):

        log = super().setup_build(build_info)

        log['user_setup'] = self._run_user_setup()
        return log
