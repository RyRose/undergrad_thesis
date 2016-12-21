import pytest
from pysimplextree.simplextree import Vertex, MySimplexTree

def create_root():
    return Vertex(MySimplexTree.ROOT_ID, MySimplexTree.ROOT_PARENT,
                  MySimplexTree.ROOT_LEVEL, {})

def test_initialization():
    t = MySimplexTree()
    assert len(t.links) == 0
    assert t.root == Vertex(MySimplexTree.ROOT_ID, MySimplexTree.ROOT_PARENT,
                            MySimplexTree.ROOT_LEVEL, {})

def test_add():
    t = MySimplexTree()
    t.add((0, 1, 2))
    expected = create_root()
    expected.add_simplex((0, 1, 2))
    assert t.root == expected

def test_locate_cofaces():
    t = MySimplexTree()
    t.add((0, 1, 2))
    cofaces, _ = t.locate_cofaces((0,))
    assert set(cofaces) == set([(0,), (0, 1), (0, 2), (0, 1, 2)])

def test_remove_simplex():
    t = MySimplexTree()
    t.add((0, 1, 2))
    expected = MySimplexTree()
    expected.add((0, 1))
    expected.add((0, 2))
    t.remove((1, 2))
    assert expected == t

def test_edgecontract_nohomotopy():
    t = MySimplexTree()
    t.add((1, 2, 3), values=("1", "2", "3"))
    t.add((2, 3, 4, 5), values=("2", "3", "4", "5"))
    expected = MySimplexTree()
    expected.add((1, 2, 4, 5), values=("1", "2", "4", "5"))
    assert t != expected
    t.edge_contract(1, 3)
    assert t == expected

def compute_euler_characteristic(tree, j):
    return sum([len(tree.get_simplices(i)) * (-1)**i for i in range(j)])


def test_edgecontract_homotopy():
    simplex = tuple(range(3))
    t = MySimplexTree()
    t.add(simplex)
    e1 = compute_euler_characteristic(t, 15)
    print(t.get_all_simplices())
    assert t.edge_contract(0, 2, keep_homotopy=True)
    print(t.get_all_simplices())
    assert t.edge_contract(0, 1, keep_homotopy=True)
    print(t.get_all_simplices())
    e2 = compute_euler_characteristic(t, 15)
    assert e1 == e2

def test_getlink():
    t = MySimplexTree()
    t.add((0, 1, 2))
    assert set([(2,)]) == set(t.get_link((0, 1)))

def test_contains():
    t = MySimplexTree()
    t.add((1, 2, 3))
    assert (1, 2) in t

def test_get_simplices():
    t = MySimplexTree()
    t.add((0, 1, 2))
    assert sum([1 for s in t.get_simplices(0)]) == 3
    assert sum([1 for s in t.get_simplices(1)]) == 3
    assert sum([1 for s in t.get_simplices(2)]) == 1
