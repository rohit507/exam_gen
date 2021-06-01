import attr

from .document import Document
from .has_user_setup import HasUserSetup
from exam_gen.util.user_setup import setup_arg
from random import Random
from exam_gen.util.stable_hash import stable_hash
import exam_gen.util.logging as logging

log = logging.new(__name__, level="DEBUG")

@attr.s
class HasRNG(HasUserSetup,Document):

    root_seed = attr.ib(default = None, kw_only=True)
    """
    The seed that the different RNGs for this document will derive from
    """

    _rng_source = attr.ib(default = None, init=False)
    """
    The rng source object that we're going to be using
    """

    def init_root_seed(self):
        from exam_gen.property.personalized import Personalized

        if isinstance(self, Personalized):
            return self.student.root_seed

        raise RuntimeError("No method to get root seed")

    def get_keyed_rng(self, *keys):
        if self.root_seed == None:
            self.root_seed = self.init_root_seed()
        return Random(stable_hash(self.root_seed,*keys))

    @setup_arg
    def rng(self) -> Random:
        """
        A repeatable random number generator that will always produce the same
        sequence of outputs for any given student, exam pair.
        """
        return self.get_keyed_rng('user_setup')

    def setup_build(self, build_info):

        log = super(HasRNG, self).setup_build(build_info)

        if self.root_seed == None:
            self.root_seed = self.init_root_seed()

        for (name, memb) in self.questions.items():
            memb.root_seed = stable_hash(self.root_seed, name)

        log['root_seed'] = self.root_seed

        return log
