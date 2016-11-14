from pytrie import Trie

class SimplexTree(Trie):

    def add_simplex(self, simplex, locs):
        for i, l in enumerate(simplex):
            if (l,) not in self:
                self[(l,)] = locs[i]
            self.__add_simplex(simplex[i+1:], (l,))

    def __add_simplex(self, simplex, root):
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


    def edge_contract(self, v1, v2):
        v1, v2 = min(v1, v2), max(v1, v2)
        if (v1, v2) not in self:
            return
        
        simplices = self.keys()
        for simplex in simplices:
            if v2 in simplex and simplex in self:
                if v1 in simplex:
                    del self[simplex]
                else:
                    self.__remove_simplex_containing_second(v1, v2, simplex)

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
            if frozenset(p) not in vlocs:
                vlocs[frozenset(p)] = index
                index += 1
        
        for ps in mesh.points:
            x, y, z = ps.reshape(-1, 3)
            d = list((vlocs[frozenset(x)], vlocs[frozenset(y)], vlocs[frozenset(z)]))
            tree.add_simplex(d, locs=(x, y, z))
        
        return tree

    def mesh_simplify(self, n):
        verts = [v[0] for v in self.keys() if len(v) == 1]
        for i in range(n):
            if i % 10 == 0:
                print(i)
            if not self.__contract_an_edge(verts):
                break

    def __contract_an_edge(self, verts):
        for j in verts:
            for k in verts:
                if (j, k) in self:
                    self.edge_contract(j, k)
                    verts.remove(k)
                    return True
        return False

    def plot(self, scale=1):
        fig = plt.figure()
        axes = fig.add_subplot(111, projection='3d')
        triangles = []
        for k in self.iterkeys():
            if len(k) == 3:
                x, y, z = k
                triangles.append([self[(x, )], self[(y, )], self[z, ]])
        
        triangles = np.array(triangles)
        axes.add_collection3d(Poly3DCollection(triangles))
        scale = triangles.flatten(-1) * scale
        axes.auto_scale_xyz(scale, scale, scale)
        return fig, axes
