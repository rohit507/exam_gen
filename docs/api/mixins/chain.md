# Data Chaining

This is a set of utility functions and a superclass to allowing distribution
and collection of data through a nested object of some sort.

This is for doing things like:
  - Assigning problem numbers
  - Gather Score Information
  - Providing Stable Random Seeds

And a bunch of other really common tasks that will happen repeatedly in
processing.

## Hooks

### Preorder Traverse

Do a preorder fold through all elements

  - `Var` : The variable to be set
  - `Collector` : The intermediate state that's passed

## Collect

  - `Gather` : Gather some value.
  - `Reduce` : Reduce the terms together.
  - `Members` : Members to gather the values from.

```python
from pprint import pprint, pformat
from copy import copy, deepcopy
from exam_gen.mixins.chain.superclass import Chainable
import attr
import itertools

@attr.s
class Member(Chainable):

    name = attr.ib()
    ident = attr.ib(default=None)
    seq = attr.ib(default=None)
    parents = attr.ib(default=None)
    preds = attr.ib(default=None)

@attr.s
class Members(Member):

    members = attr.ib(factory=list)

    def get_members(self):
        if isinstance(self, Members):
            return self.members
        else:
            return []

    @gather
    def name_list(self):
        return self.name

    @name_list.combine
    def name_list(self, item, items):
        return itertools.chain(item, *items)

    @name_list.members
    def name_list(self):
        if isinstance(self, Members):
            return self.members
        else:
            return []

    @distribute(members = get_members)
    def set_idents(self, ident):
        self.ident = ident

    @set_idents.distribute
    def set_idents(self, data):
        if self.name in data:
            self_data = data[self.name]
        else:
            self_data = None

        return (self_data, data)

    @nested_iter(members = get_members)
    def set_seq(self, seq):
        self.seq = seq

    @set_seq.recurse
    def set_seq(self, seq):
        for i in itertools.count():
            yield copy(seq) + [i]

    @depth_iter(members = get_members)
    def parent_list(self, data):
        self.parents = data
        return [self.name] + data

    @tree_iter(members = get_members)
    def pred_list(self, data):
        self.preds = copy(data)
        data.append(self.name)
        return data




tree = Members(
    "1",
    members=[
        Member("1A"),
        Member("1B"),
        Members(
            "1C",
            members=[
                Member("1C1"),
                Member("1C2"),
                Member("1C3"),
            ]),
        Member("1D"),
        Members(
            "1E",
            members=[
                Member("1E1"),
                Member("1E2"),
            ]),
    ])

pprint(attr.asdict(tree))

pprint(list(tree.name_list()))

tree.set_idents({
    "1": "foo",
    "1A" : "bar",
    "1E1" : "buzz",
    })

tree.set_seq([])
tree.parent_list([])
tree.pred_list([])

pprint(attr.asdict(tree))
```

```python
{'ident': 'foo',
 'members': [{'ident': 'bar',
              'name': '1A',
              'parents': ['1'],
              'preds': ['1'],
              'seq': [0]},
             {'ident': None,
              'name': '1B',
              'parents': ['1'],
              'preds': ['1', '1A'],
              'seq': [1]},
             {'ident': None,
              'members': [{'ident': None,
                           'name': '1C1',
                           'parents': ['1C', '1'],
                           'preds': ['1', '1A', '1B', '1C'],
                           'seq': [2, 0]},
                          {'ident': None,
                           'name': '1C2',
                           'parents': ['1C', '1'],
                           'preds': ['1', '1A', '1B', '1C', '1C1'],
                           'seq': [2, 1]},
                          {'ident': None,
                           'name': '1C3',
                           'parents': ['1C', '1'],
                           'preds': ['1', '1A', '1B', '1C', '1C1', '1C2'],
                           'seq': [2, 2]}],
              'name': '1C',
              'parents': ['1'],
              'preds': ['1', '1A', '1B'],
              'seq': [2]},
             {'ident': None,
              'name': '1D',
              'parents': ['1'],
              'preds': ['1', '1A', '1B', '1C'],
              'seq': [3]},
             {'ident': None,
              'members': [{'ident': 'buzz',
                           'name': '1E1',
                           'parents': ['1E', '1'],
                           'preds': ['1', '1A', '1B', '1C', '1D', '1E'],
                           'seq': [4, 0]},
                          {'ident': None,
                           'name': '1E2',
                           'parents': ['1E', '1'],
                           'preds': ['1', '1A', '1B', '1C', '1D', '1E', '1E1'],
                           'seq': [4, 1]}],
              'name': '1E',
              'parents': ['1'],
              'preds': ['1', '1A', '1B', '1C', '1D'],
              'seq': [4]}],
 'name': '1',
 'parents': [],
 'preds': [],
 'seq': []}
```
