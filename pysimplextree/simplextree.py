import itertools

class Vertex:

    def __init__(self, vid : int, parent, level : int, links : dict, value=None):
        """
        Initializes the Vertex.
        """

        self.id = vid
        self.parent = parent
        self.level = level
        self.links = links
        self.value = value
        self.children = {}

    def __setup_links(self, parent):
        if parent is not None:
            parent.children[self.id] = self
        self.parent = parent
        if self.id not in self.links:
            self.links[self.id] = {}
        if self.level not in self.links[self.id]:
            self.links[self.id][self.level] = {}
        if id(self) not in self.links[self.id][self.level]:
            self.links[self.id][self.level][id(self)] = self

    def add_child(self, vid, value=None):
        if vid in self.children:
            if value is not None:
                self.children[vid].value = value
        else:
            child = Vertex(vid, self, self.level + 1, self.links, value=value)
            child.__setup_links(self)

    def add_simplex(self, simplex : tuple, values=None):
        for i, vid in enumerate(simplex):
            self.add_child(vid, value= None if values is None else values[i])
            self.children[vid].add_simplex(simplex[i + 1:])

    def __contains__(self, simplex : tuple):
        if len(simplex) == 0:
            return True

        head = simplex[0]
        if head in self.children:
            return simplex[1:] in self.children[head]
        else:
            return False

    def is_coface(self, simplex : tuple):
        """
        Determine if the vertex and its parents contain the simplex.
        """
        if self.parent is None:
            result = len(simplex) == 0
        elif self.parent.parent is None:
            result = len(simplex) == 0 or (len(simplex) == 1 and simplex[0] == self.id)
        elif len(simplex) > 0 and self.id == simplex[-1]:
            result = self.parent.is_coface(simplex[:-1])
        else:
            result = self.parent.is_coface(simplex)
        return result

    def collect_upwards(self):
        if self.parent is None:
            return tuple()
        elif self.parent.parent is None:
            return (self.id,)
        else:
            return self.parent.collect_upwards() + (self.id,)

    def collect_downwards(self, limit=-1, maximal=False):
        if maximal and limit == 0:
            return [(self.id,)]
        elif len(self.children) == 0:
            return [] if maximal else [(self.id,)]

        simplices = [child.collect_downwards(limit = limit - 1, maximal=maximal) for child in self.children.values()]
        if self.parent is None:
            simplices = list(itertools.chain.from_iterable(simplices))
        else:
            simplices = [(self.id,) + s for s in list(itertools.chain.from_iterable(simplices))]
            if not maximal:
                simplices.append((self.id,))
        return simplices

    def __remove_links(self):
        if self.parent is not None:
            self.parent.children.pop(self.id)
            self.parent = None
        if self.id in self.links and self.level in self.links[self.id] and id(self) in self.links[self.id][self.level]:
            self.links[self.id][self.level].pop(id(self))
            if len(self.links[self.id][self.level]) == 0:
                self.links[self.id].pop(self.level)
                if len(self.links[self.id]) == 0:
                    self.links.pop(self.id)

    def remove(self):
        self.__remove_links()
        children = list(self.children.values())
        for child in children:
            child.remove()

    def merge(self, vertex):
        vertex.__remove_links()
        self.children = {**vertex.children, **self.children}
        for v in self.children.values():
            v.__update(self, True)

    def __update(self, parent, update_children):
        self.__remove_links()
        self.level = parent.level + 1
        self.__setup_links(parent)

        if update_children:
            for v in self.children.values():
                v.__update(self, update_children)

    def last(self, simplex):
        if len(simplex) == 0:
            return self
        elif simplex[0] in self.children:
            return self.children[simplex[0]].last(simplex[1:])

    def __eq__(self, other):
        return self.id == other.id and self.level == other.level and \
        self.children == other.children and self.value == other.value

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return "Vertex:{id:" + str(self.id) + ",level:" + str(self.level) + \
        ",val:" + str(self.value) + "}"

class MySimplexTree:

    ROOT_PARENT = None
    ROOT_ID = None
    ROOT_LEVEL = 0

    def __init__(self):
        """
        Initialize the empty SimplexTree.
        """
        self.links = {}
        self.root = Vertex(MySimplexTree.ROOT_ID, MySimplexTree.ROOT_PARENT,
                           MySimplexTree.ROOT_LEVEL, self.links)

    def add(self, simplex : tuple, values=None):
        self.root.add_simplex(simplex, values=values)

    def remove(self, simplex : tuple):
        if simplex not in self:
            return
        _, verts = self.locate_cofaces(simplex)
        for vert in verts:
            vert.remove()

    def locate_cofaces(self, simplex : tuple):
        verts = self.links[simplex[-1]].items()
        verts = (v for (k, v) in filter(lambda kv: kv[0] >= len(simplex),verts))
        verts = (list(v.values()) for v in verts)
        verts = list(itertools.chain.from_iterable(verts))
        coface_verts = []

        for vert in verts:
            is_coface = vert.is_coface(simplex)
            if is_coface:
                coface_verts.append(vert)

        cofaces = set()
        for vert in coface_verts:
            front = vert.collect_upwards()
            back  = vert.collect_downwards()
            cofaces.update(map(lambda b : front + b[1:], back))
            cofaces.update((front,))

        return cofaces, coface_verts

    def __is_valid_homotopic_edge(self, v1, v2):
        l1 = self.get_link((v1,))
        l2 = self.get_link((v2,))
        edge = self.get_link((v1, v2))
        return set(edge) == (set(l1) & set(l2))

    def get_link(self, simplex):
        s = set(simplex)
        cofaces, _ = self.locate_cofaces(simplex)
        cofaces = [sorted(set(face) - s) for face in cofaces]
        return [tuple(face) for face in cofaces if face in self and len(face) != 0]

    def edge_contract(self, v1 : int, v2 : int, keep_homotopy=False):
        v1, v2 = min(v1, v2), max(v1, v2)
        if (v1, v2) not in self:
            return False
        if keep_homotopy and not self.__is_valid_homotopic_edge(v1, v2):
            return False

        verts = self.links[v2].values()
        verts = (list(v.values()) for v in verts)
        verts = list(itertools.chain.from_iterable(verts))
        for vert in verts:
            simplex = set(vert.collect_upwards())
            if v1 in simplex:
                vert.remove()
            else:
                simplex.remove(v2)
                simplex.add(v1)
                simplex = tuple(sorted(simplex))
                self.add(simplex)
                last_vertex = self.root.last(simplex)
                last_vertex.merge(vert)

        return True

    def get_simplices(self, j):
        return self.root.collect_downwards(limit=j+1, maximal=True)

    def get_all_simplices(self):
        return self.root.collect_downwards(limit=-1, maximal=False)

    def __contains__(self, simplex):
        simplex = sorted(simplex)
        return simplex in self.root

    def __eq__(self, other):
        return self.root == other.root

    def __repr__(self):
        return "MySimplexTree:{root:" + str(self.root) + ",main:" + \
        str(self.root.children) + "}"
