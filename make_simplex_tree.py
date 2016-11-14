from SimplexTree import SimplexTree

def make_simplex_tree():
    t = SimplexTree()
    t.add_simplex((0, 1, 2),((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    return t
