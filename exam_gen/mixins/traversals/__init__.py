from exam_gen.mixins.traversals.gatherer import Gatherer
from exam_gen.mixins.traversals.distributor import Distributor
from exam_gen.mixins.traversals.nested_iterator import NestedIterator
from exam_gen.mixins.traversals.depth_iterator import DepthIterator
from exam_gen.mixins.traversals.sibling_iterator import SiblingIterator

gather = Gatherer.decorate
distribute = Distributor.decorate
nested_iter = NestedIterator.decorate
depth_iter = DepthIterator.decorate
sibling_iter = SiblingIterator.decorate

__all__ = ['gather', 'distribute', 'nested_iter', 'depth_iter', 'sibling_iter']
