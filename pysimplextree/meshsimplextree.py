import numpy as np
from stl.mesh import Mesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from .simplextree import MySimplexTree

class MyMeshSimplexTree(MySimplexTree):

    @classmethod
    def from_mesh(cls, mesh : Mesh):
        tree = cls()
        vlocs = {}
        index = 0
        for ps in mesh.vectors:
            for p in ps:
                q = frozenset(p)
                if q not in vlocs:
                    vlocs[q] = index
                    index += 1

        for x, y, z in mesh.vectors:
            xi = frozenset(x)
            yi = frozenset(y)
            zi = frozenset(z)
            d = [(vlocs[xi], x), (vlocs[yi], y), (vlocs[zi], z)]
            d.sort()
            tree.add((d[0][0], d[1][0], d[2][0]), values=(d[0][1], d[1][1],
                                                        d[2][1]))
        return tree

    def mesh_simplify(self, n, keep_homotopy=True, verbose=False ):
       i = 0
       failed = True
       edges = iter(self.get_simplices(1))
       while i < n:
           if verbose and i % (n//10) == 0:
               print("edges so far:", i)
           try:
               v1, v2 = next(edges)
               if self.edge_contract(v1, v2, keep_homotopy=keep_homotopy):
                   failed = False
                   i += 1
           except StopIteration:
               if failed:
                   return
               failed = True
               edges = iter(self.get_simplices(1))

    def plot(self, scale=1):
        fig = plt.figure()
        axes = fig.add_subplot(111, projection='3d')

        triangles = []
        for (x, y, z) in self.get_simplices(2):
            triangles.append((self.root.children[x].value,
                              self.root.children[y].value,
                              self.root.children[z].value))
        triangles = np.array(triangles)
        axes.add_collection3d(Poly3DCollection(triangles))
        scale = triangles.flatten(-1) * scale
        axes.auto_scale_xyz(scale, scale, scale)
        return axes, fig
