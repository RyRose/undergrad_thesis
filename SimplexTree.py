from pytrie import Trie

class SimplexTree(Trie):

    def __init__(self):
        super().__init__()
        self.edges = set()

    def add_simplex(self, simplex, locs):

        if len(simplex) == 2:
            self.edges.add(simplex)

        for i, l in enumerate(simplex):
            if (l,) not in self:
                self[(l,)] = locs[i]
            self.__add_simplex(simplex[i+1:], (l,))

    def __add_simplex(self, simplex, root):
        if len(simplex) == 2:
            self.edges.add(simplex)

        for i, l in enumerate(simplex):
            self[root + (l,)] = 0
            self.__add_simplex(simplex[i+1:], root + (l,))

    def remove_simplex(self, simplex):
        if simplex not in self:
            return

        cofaces = self.locate_cofaces(simplex)
        for face in cofaces:
            del self[face]

        del self[simplex]
    
    def locate_cofaces(self, simplex):
        if len(simplex) <= 0:
            return self.keys()

        simplex = sorted(simplex)
        keys = self.keys()
        return [key for key in keys if len(key) > len(simplex) and simplex[-1] in key[len(simplex)-1:]]

    def is_valid_homotopic_edge(self, v1, v2):
        if (v1, v2) not in self:
            return False

        l1 = self.get_link((v1,))
        l2 = self.get_link((v2,))
        edge = self.get_link((v1, v2))
        return set(edge) == (set(l1) & set(l2))

    def get_link(self, simplex):
        s = set(simplex)
        cofaces = self.locate_cofaces(simplex)
        cofaces = [sorted(set(face) - s) for face in cofaces]
        return [frozenset(face) for face in cofaces if face in self]

    def edge_contract(self, v1, v2):
        v1, v2 = min(v1, v2), max(v1, v2)

        if not self.is_valid_homotopic_edge(v1, v2):
            return False
        
        simplices = self.keys()
        for simplex in simplices:
            if v2 in simplex and simplex in self:
                if v1 in simplex:
                    del self[simplex]
                else:
                    self.__remove_simplex_containing_second(v1, v2, simplex)

        return True

    def __remove_simplex_containing_second(self, v1, v2, simplex):
        stored = self[(v1,)]
        to_be_added = list(simplex)
        to_be_added.remove(v2)
        verts = [self[(v,)] for v in to_be_added]
        self.remove_simplex(simplex)
        self.add_simplex(to_be_added, verts)
        self[(v1,)] = stored

import numpy as np
from stl.mesh import Mesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class MeshSimplexTree(SimplexTree):

    @classmethod
    def from_mesh(cls, mesh : Mesh):
        tree = cls()
        vlocs = {}
        index = 0
        for p in mesh.points.reshape(-1, 3):
            q = frozenset(p)
            if q not in vlocs:
                vlocs[q] = index
                index += 1
        
        for x, y, z in mesh.points.reshape(-1, 3, 3):
            xi = frozenset(x)
            yi = frozenset(y)
            zi = frozenset(z)
            d = (vlocs[xi], vlocs[yi], vlocs[zi])
            tree.add_simplex(d, locs=(x, y, z))
        
        return tree

    def mesh_simplify(self, n):
        invalid = set()
        for i in range(n):
            if i % 10 == 0:
                print("main for loop: ", i, len(self.edges))
            while len(self.edges) != 0:
                (v1, v2) = self.edges.pop()
                if self.edge_contract(v1, v2):
                    break
                else:
                    invalid.add((v1, v2))
            if len(self.edges) == 0:
                self.edges = invalid
                invalid = set()

        self.edges = self.edges.union(invalid)

    def plot(self, scale=1):
        fig = plt.figure()
        axes = fig.add_subplot(111, projection='3d')
        triangles = []

        for k in self.iterkeys():
            if len(k) == 3:
                x, y, z = k
                triangles.append([self[(x, )], self[(y, )], self[(z, )]])
        
        triangles = np.array(triangles)
        axes.add_collection3d(Poly3DCollection(triangles))
        scale = triangles.flatten(-1) * scale
        axes.auto_scale_xyz(scale, scale, scale)
        return axes, fig
