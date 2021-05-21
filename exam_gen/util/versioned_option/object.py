import attr

import exam_gen.util.logging as logging

import functools

log = logging.new(__name__, level="DEBUG")

__all__ = ["VersionedObj"]

VersionKey = attr.make_class(
    "VersionKey",
    ["depth", "name"],
    hash=True)

@attr.s
class VersionedObj():
    """
    A proxy object that makes it a little nicer to work with a number of
    different options at once.
    """


    var_name = attr.ib()
    _parent = attr.ib(default = None, kw_only=True)
    _parent_key = attr.ib(default = None, kw_only=True)
    _stored_entries = attr.ib(factory=dict, init=None)
    _format_spec = attr.ib(factory = list)

    def __setitem__(self, key_str, val):
        raise RuntimeError("Cannot directly set '{}[{}]'".format(
            self.var_name, key))

    def __getitem__(self, key):

        if len(self.format_spec) == 0:
            raise RuntimeError(("This object has no sub-versions, there is "
                                "no valid term like '{}[...]'."
            ).format(self.var_name))

        error = None

        for depth, fmt in enumerate(self.format_spec):
            try:
                new_key = fmt['key_func'](self, key)
            except RuntimeError as err:
                error = err.with_traceback(error)
            else:
                return self.get_sub_version(VersionKey(depth, new_key))

        raise RuntimeError(
            ("Could not find subtype '{}' for '{}' in  `{}[{}]`."
            ).format(key, self.var_name, self.var_name, key)
        ).with_traceback(error)

    def __contains__(self, key):

        if len(self.format_spec) == 0:
            return False

        for depth, fmt in enumerate(self.format_spec):
            try:
                fmt['key_func'](self, key)
            except RuntimeError as err:
                pass
            else:
                return True

        return False

    @property
    def root(self):
        return self if self._parent == None else self._parent

    def prop_child_func(self, func, *,
                        key_list=None,
                        apply_self=True,
                        apply_direct_child=True,
                        apply_child=True,
                        apply_parent=False,
                        supress_parent=False):
        """
        One of our children had a set value, propagate that application
        around as needed.

        You should use this to implement getattr and setattr for child classes.

        By default this will apply some function to self and its logical
        children.

        Params:

            func: the function to call, takes self as only parameter

            apply_self: should this call apply the function to self?

            apply_child: should this call apply to children?

            apply_parent: should this call apply to parent elems?

            key_list: a list of links that defines a valid child, used mainly
               to propagate parents.
        """

        if (key_list != None) and (len(key_list) == 0):
            raise RuntimeError("List should always have at least 1 element.")

        if apply_self:
            func(self)

        child_key = None
        succ_list = None

        if (key_list != None) and apply_child:
            child_key = key_list[0]

        if (child_key != None) and (len(key_list) > 1):
            succ_list = key_list[1:]

        # Are we applying the function as we walk directly back up the
        # keylist or should we just propagate things out to other possible
        # children.
        if apply_direct_child and child_key != None:

            self.get_sub_version(child_key).prop_child_func(
                func,
                key_list = succ_list,
                apply_self = succ_list == None,
                apply_direct_child = True,
                apply_child = apply_child,
                supress_parent = True)

        if apply_child:
            for (key, entry) in self._stored_entries.items():

                # No key_list means we're not trying to filter so we apply the
                # function to all children.
                if key_list == None:

                    entry.prop_child_func(
                        func,
                        apply_self = True,
                        apply_child = True,
                        supress_parent = True)

                # If there is a key_list we only want to apply to relevant
                # children, relevant children (which can have entries that
                # match the list) must be strictly less deep than the child
                # key.
                elif key.depth < child_key.depth:

                    adjusted_list = deepcopy(
                        [VersionKey(child_key.depth - key.depth,
                                    child_key.name)]
                        + key_list[1:])

                    entry.prop_child_func(
                        func,
                        key_list=adjusted_list,
                        apply_self=False,
                        apply_direct_child=True,
                        apply_child=True,
                        supress_parent= True)

        # if we're applying parent we need to make a call to parent.
        # if we're applying to children then we need to propagate to parents
        # anyway in order to use other matching child trees.

        if ((not supress_parent) # no other step has taken care of this
            and (apply_parent or apply_child) # we need to do this
            and (self._parent != None)): # we have a parent

            new_list = [self._parent_key]
            new_list += [] if key_list == None else key_list

            self.parent.prop_child_func(
                func,
                key_list = new_list,
                apply_self = apply_parent,
                apply_direct_child = False,
                apply_child = apply_child,
                apply_parent = apply_parent,
                supress_parent = False
                )

    def get_sub_version(self, key):

        if key in self._stored_entries:
            return self._stored_entries[key]

        new_entry = type(self)("{}[{}]".format(self.var_name, key.name),
                               parent=self,
                               parent_key=key)

        self._stored_entries[key] = new_entry

        return new_entry

    def version_tree(self):

        tree = dict()
        tree[None] = self
        for (key, entry) in self._stored_entries.items():
            tree[key.name] = entry.version_tree

        return tree

    def mk_apply_tree_func(self, merge_func):
        """
        Creates a way to recursively apply a version tree to a VersionObj
        with some combination function
        """

        def apply_tree(self, tree, *, merge_f):
            for (key, entry) in tree.items():
                if key == None:
                    merge_f(self, entry)
                elif 'key' in self:
                    apply_tree(self[key], entry, merge_f=merge_f)

        return functools.partial(
            apply_tree,
            merge_f=merge_func
        )
