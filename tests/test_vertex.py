import pytest
from pysimplextree.simplextree import Vertex, MySimplexTree

def create_root():
    return Vertex(MySimplexTree.ROOT_ID, MySimplexTree.ROOT_PARENT,
                  MySimplexTree.ROOT_LEVEL, {})

def test_initialize():
    root = create_root()
    assert root.id == MySimplexTree.ROOT_ID
    assert root.parent == MySimplexTree.ROOT_PARENT
    assert root.level == MySimplexTree.ROOT_LEVEL
    assert len(root.links) == 0
    assert len(root.children) == 0

def test_addchilddne():
    root = create_root()
    root.add_child(0)
    assert 0 in root.children
    assert len(root.children) == 1

    child = root.children[0]
    expected = Vertex(0, root, root.level + 1, {0 : {1 : {id(child) : child} } })
    assert child == expected

def test_addsimplex():
    root = create_root()
    simplex = (0, 1, 2)
    root.add_simplex(simplex)
    expected = create_root()
    expected.add_child(0)
    expected.add_child(1)
    expected.add_child(2)
    expected.children.get(0).add_child(1)
    expected.children.get(0).add_child(2)
    expected.children.get(1).add_child(2)
    expected.children.get(0).children.get(1).add_child(2)
    assert root == expected

def test_contains():
    root = create_root()
    simplex = (1, 2, 3, 4)
    assert simplex not in root
    root.add_simplex(simplex)
    assert simplex in root
    assert (3,5) not in root

def test_coface():
    root = create_root()
    simplex = (0, 1, 2, 3)
    root.add_simplex(simplex)
    v = root.last((1, 2, 3))
    assert not v.is_coface((0, 1, 2, 3))
    assert v.is_coface((1, 2))

def test_collectupwards():
    root = create_root()
    simplex = tuple(range(10))
    root.add_simplex(simplex)
    v = root
    for i in range(len(simplex)):
        assert v.collect_upwards() == simplex[:i]
        v = v.children[i]

def test_remove():
    root = create_root()
    root.add_simplex((0, 1, 2))
    expected = create_root()
    expected.add_simplex((1, 2))
    root.children[0].remove()
    assert root == expected

def test_merge():
    root = create_root()
    other = create_root()
    other.add_simplex((1, 2, 3))
    expected = create_root()
    expected.add_simplex((1, 2, 3))
    root.merge(other)
    assert root == expected

def test_update():
    v1 = create_root()
    v2 = Vertex(1, None, 5, {})
    v2.links[1] = { 5 : {id(v2) : v2} }
    expected = Vertex(1, v1, v1.level + 1, {})
    expected.links[1] = {1 : {id(expected) : expected}}
    assert v1 != expected
    v2._Vertex__update(v1, False)
    assert v2 == expected
    assert v2.parent == expected.parent

def test_last():
    root = create_root()
    simplex = (0, 1, 2, 3, 4)
    root.add_simplex(simplex)
    v = root
    for i, s in enumerate(simplex):
        assert v == root.last(simplex[:i])
        v = v.children[s]
