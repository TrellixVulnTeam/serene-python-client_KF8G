import logging

_logger = logging.getLogger()
_logger.setLevel(logging.DEBUG)


class Searchable(object):
    """
    A small object that allows hierarchical search across its properties...
    """
    getters = []

    @classmethod
    def search(cls, container, item, errors=False):
        """
        Finds a DataNode item in a container. The search method enables
        shorthand searches based on uniqueness. e.g. if there is only one
        DataNode with name='id' then it can be referenced with DataNode('id').
        Though if there are two DataNode('id', ClassNode('Person')) and
        DataNode('id', ClassNode('Business')), then the ClassNode would need
        to be provided to remove the ambiguity. Search will use the 'getter'
        objects provided to compare keys.

        The search method is called from a class type on a container and
        target.

        ClassNode.search(class_node_list, class_node)

        The target can be partially complete e.g. Class("Person")

        ClassNode.search(class_node_list, Class("Person")

        :param container: An iterable of objects
        :param item: The target object to find, can be partially complete.
        :return: the item or None or LookupError if ambiguous
        """

        def find(haystack, needle, getter):
            """
            This function will look into the 'haystack' container for the item
            'needle' using the getter function

            Note: None is treated as a wildcard e.g. DataNode(None, 'name') == DataNode('Person', 'name')

            :param haystack:
            :param needle:
            :param getter:
            :return:
            """
            matches = []
            for dn in haystack:
                try:
                    if getter(needle) is None or getter(dn) is None:
                        matches.append(dn)
                    elif getter(needle) == getter(dn):
                        matches.append(dn)
                except AttributeError:
                    # if the getter fails, then we add nothing...
                    pass

            if len(matches) == 0:
                # not found...
                return False, None
            elif len(matches) == 1:
                # item found!
                return True, matches[0]
            else:
                # found ambiguities...
                return False, matches

        # now we iterate over all the getters until we find our match...
        candidates = container
        for get in cls.getters:
            ok, match = find(candidates, item, get)
            if ok:
                return match
            if match is None:
                return None
            else:
                # a match is found, but it is ambiguous
                candidates = match

        msg = "Failed to find item. {} is ambiguous: {}".format(item, candidates)
        _logger.error(msg)
        raise LookupError(msg)