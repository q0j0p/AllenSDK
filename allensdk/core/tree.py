def vectorize(f):
    @functools.wraps(f)
    def wrapper(obj, *args):
        return map(functools.partial(f, obj), args)
    return wrapper


def wrap_across_methods(decorator, *exclude):
    def decorate(cls):
        
        valid_method = lambda attr: (attr not in exclude) and callable(getattr(cls, attr))
        reassign_method = lambda attr: setattr(cls, attr, decorator(getattr(cls, attr)))
        
        method_names = filter(valid_method, cls.__dict__)
        map(reassign_method, method_names)
    
        return cls
    return decorate
        

@wrap_across_methods(vectorize, '__init__')
class SimpleTree( object ):
    def __init__(self, nodes, 
                 node_id_cb, 
                 parent_id_cb):

        self._nodes = { node_id_cb(n):n for n in nodes }
        self._parent_ids = { nid:parent_id_cb(n) for nid,n in self._nodes.iteritems() }
        self._child_ids = { nid:[] for nid in self._nodes }

        for nid in self._parent_ids:
            pid = self._parent_ids[nid]
            if pid:
                self._child_ids[pid].append(nid)


    def node_ids(self):
        return self._nodes.keys()


    def parent_id(self, nid):
        try:
            return self._parent_ids[nid]
        except KeyError:
            raise KeyError("Could not find parent for node %s" % str(nid))


    def child_ids(self, nid):
        try:
            for cid in self._child_ids[nid]:
                yield cid
        except KeyError:
            raise KeyError("Could not find children for node %s" % str(nid))


    def ancestor_ids(self, nid):
        try:
            pid = nid
            while pid:
                yield pid
                pid = self.parent_id(pid)
        except:
            raise KeyError("Could not find ancestors for node %s" % str(nid))
        
        
    def descendant_ids(self, nid):
        ids = [nid]
        try:
            while ids:
                nid = ids.pop()
                yield nid
                ids += self.child_ids(nid)
        except KeyError:
            raise KeyError("Could not find descendants for node %s" % str(nid))


    def node(self, nid):
        return self._nodes[nid]


    def parent(self, nid):
        return self.node(self.parent_id(nid))


    def children(self, nid):
        for node in self.nodes(self.child_ids(nid)):
            yield node


    def descendants(self, nid):
        for node in self.nodes(self.descendant_ids(nid)):
            yield node


    def ancestors(self, nid):
        for node in self.nodes(self.ancestor_ids(nid)):
            yield node
