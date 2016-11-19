## Old SimplexTree Definition

import matplotlib.pyplot as plt
from pytrie import Trie
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class SimplexTree(Trie):
    
    def __init__(self):
        super().__init__()
        self.vertices = set()
    
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
        
    '''
    O(2^j D_m) where we insert a j-simplex with D_m = O(1)
    ''' 
    def add_simplex(self, simplex : set, locs=None, root=None):
        if len(simplex) == 0:
            return 
        
        if root:
            for i, l in enumerate(simplex):
                self[root + (l,)] = 0
                self.add_simplex(simplex[i+1:], root=(root + (l,)))
        else:
            for i, l in enumerate(simplex):
                self.vertices.add(l)
                if (l,) not in self:
                    self[(l,)] = locs[i]
                self.add_simplex(simplex[i+1:], root=(l,))
    
    def simplify(self, num : int):
        so_far = 0
        while num >= so_far:
            for i in np.random.shuffle(vertices):
                for j in np.random.shuffle(vertices):
                    its = self.items((i, j))
                    if len(its) == 2:
                        self.collapse(i, j)
                        so_far += 1

            break
        v1, v2 = min(v1, v2), max(v1, v2)  

    def edge_contract(self, v1, v2):
        v1, v2 = min(v1, ttv2), max(v1, v2)
        
        if (v1, v2) not in self:
            return False
        
    def plot(self, scale=1):
        fig = plt.figure()
        axes = fig.add_subplot(111, projection='3d')
        
        points = []
        lines = []
        triangles = []
        for k in self.iterkeys():
            if len(k) == 1:
                (x, ) = k
                points.append(self[(x,)])
            elif len(k) == 2:
                x, y = k
                lines.append([self[(x, )], self[(y, )]])
            elif len(k) == 3:
                x, y, z = k
                triangles.append([self[(x, )], self[(y, )], self[z, ]])
        
        triangles = np.array(triangles)
        axes.add_collection3d(Poly3DCollection(triangles))
        scale = triangles.flatten(-1) * scale
        axes.auto_scale_xyz(scale, scale, scale)
        return fig, axes


## Loading a 3D Mesh as normal.

# Create a new plot
figure = plt.figure()
axes = Axes3D(figure)

# Load the STL files and add the vectors to the plot
your_mesh = Mesh.from_file('models/Dalek.stl')
axes.add_collection3d(Poly3DCollection(your_mesh.vectors))
scale = your_mesh.points.flatten(-1) / 1.8
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
plt.show()

## IPython Notebook Show Simplices

# blah
t = SimplexTree()
t.add_simplex((0, 1, 2, 3), locs=((1, 0, 0), (0, 1, 0), (.5, .5, 1), (0, 0, 0)))
fig, ax = t.plot(.8)
ax.view_init(15, 0)
plt.axis("off")
fig.savefig("pres2/tetrahedron.png")
plt.show()

# blah
t = SimplexTree()
t.add_simplex((0, 1, 2, 3),((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)))
t.add_simplex((2, 3, 4), (0, 0, (-1, 0, 0)))
t.add_simplex((2, 3, 5), (0, 0, (0, -1, 0)))
fig, ax = t.plot()
