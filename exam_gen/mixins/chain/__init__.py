from exam_gen.mixins.chain.superclass import *

gather = Gatherer.decorate
distribute = Distributor.decorate
nested_iter = NestedIterator.decorate
depth_iter = PropagateDown.decorate
tree_iter = TreeTraverse.decorate

__all__ = ['gather','distribute','nested_iter','depth_iter','tree_iter']
