"""
These tests use the following arrangement of nodes::

          o --- o --- o --- o
         /     /     /     /
       o --- o --- o --- o
      /     /     /    /
    o --- o --- o --- o

This result in two bound voronoi polygons (12 total) centered on points
5 and 6.
"""

from nose.tools import (assert_true, assert_false, assert_equal)
try:
    from nose.tools import assert_tuple_equal, assert_is_instance
except ImportError:
    from landlab.testing.tools import assert_tuple_equal, assert_is_instance
from numpy.testing import assert_array_equal, assert_array_almost_equal
from scipy.spatial import Voronoi
import numpy as np

from landlab.graph.voronoi.voronoi_helpers import VoronoiConverter

#     get_finite_regions, is_patch, is_link, get_patch_at_region,
#     get_link_at_ridge, get_node_at_vertex, get_patches_at_link,
#     get_nodes_at_link, get_nodes, get_ridges_at_region,
#     get_links_at_patch, get_corner_at_patch)


NODE_X = (0. , 1. , 2. , 3. ,
           .1, 1.1, 2.1, 3.1,
           .2, 1.2, 2.2, 3.2)
NODE_Y = (0. , 0. , 0. , 0. ,
          1. , 1. , 1. , 1. ,
          2. , 2. , 2. , 2.)
POINTS = list(zip(NODE_X, NODE_Y))


def test_get_finite_regions():
    """Test the regions that are bound."""
    converter = VoronoiConverter(Voronoi(POINTS))

    regions = converter.get_finite_regions()

    assert_equal(len(regions), 13) # There's one extra "empty" region
    assert_equal(len(regions[regions == 0]), 11)
    assert_equal(len(regions[regions == 1]), 2)


def test_is_patch():
    """Test if a region is a patch."""
    converter = VoronoiConverter(None)

    assert_true(converter.is_patch([1, 2, 3]))
    assert_false(converter.is_patch([1, 2, 3, -1]))
    assert_false(converter.is_patch([]))


def test_is_link():
    """Test if a ridge is a link."""
    v = Voronoi(POINTS)
    converter = VoronoiConverter(v)

    links = [converter.is_link(r) for r in range(len(v.ridge_vertices))]

    assert_equal(sum(links), 11)


def test_patch_at_region():
    """Test mapping voronoi regions to patches."""
    v = Voronoi(POINTS)
    converter = VoronoiConverter(v)

    patch_at_region = converter.get_patch_at_region()

    assert_equal(patch_at_region.shape, (len(v.regions), ))
    assert_equal(sum(patch_at_region >= 0), 2)


def test_link_at_ridge():
    """Test mapping voronoi ridges to links."""
    v = Voronoi(POINTS)
    converter = VoronoiConverter(v)

    link_at_ridge = converter.get_link_at_ridge()

    assert_equal(link_at_ridge.shape, (len(v.ridge_vertices), ))
    assert_equal(sum(link_at_ridge >= 0), 11)


def test_patches_at_link():
    """Test getting link patches."""
    converter = VoronoiConverter(Voronoi(POINTS))

    patches_at_link = converter.get_patches_at_link()

    assert_tuple_equal(patches_at_link.shape, (11, 2))
    for patches in patches_at_link:
        assert_true(patches[0] != -1 or patches[1] != -1)


def test_node_at_vertex():
    """Test mapping voronoi vertices to nodes."""
    v = Voronoi(POINTS)
    converter = VoronoiConverter(v)

    node_at_vertex = converter.get_node_at_vertex()

    assert_tuple_equal(node_at_vertex.shape, (len(v.vertices), ))
    assert_equal(sum(node_at_vertex >= 0), 10)

    node_at_vertex = node_at_vertex[node_at_vertex >= 0]
    node_at_vertex.sort()
    assert_array_equal(node_at_vertex, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_nodes_at_link():
    """Test getting nodes at links from a voronoi."""
    converter = VoronoiConverter(Voronoi(POINTS))

    nodes_at_link = converter.get_nodes_at_link()

    assert_tuple_equal(nodes_at_link.shape, (11, 2))
    assert_true(np.all(nodes_at_link >= 0))
    assert_true(np.all(nodes_at_link < 10))

    assert_array_equal(np.unique(nodes_at_link),
                       [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_nodes():
    """Test getting nodes at links from a voronoi."""
    converter = VoronoiConverter(Voronoi(POINTS))

    nodes = converter.get_nodes()

    assert_tuple_equal(nodes.shape, (10, 2))
    assert_is_instance(nodes[0, 0], float)


def test_ridges_at_region():
    """Test getting ridges that bound regions."""
    v = Voronoi(POINTS)
    converter = VoronoiConverter(v)

    ridges_at_region = converter.get_ridges_at_region()

    assert_tuple_equal(ridges_at_region.shape, (len(v.regions), 6))
    assert_is_instance(ridges_at_region[0, 0], np.int_)
    assert_array_equal(ridges_at_region[0], [-1] * 6)


def test_links_at_patch():
    """Test getting links that bound patches from a voronoi."""
    converter = VoronoiConverter(Voronoi(POINTS))

    links_at_patch = converter.get_links_at_patch()

    assert_tuple_equal(links_at_patch.shape, (2, 6))
    assert_true(np.all(links_at_patch >= 0))
    assert_true(np.all(links_at_patch < 11))


def test_corner_at_patch():
    """Test getting corners for each patch."""
    v = Voronoi(POINTS)
    converter = VoronoiConverter(v)

    corner_at_patch = converter.get_corner_at_patch()

    assert_tuple_equal(corner_at_patch.shape, (2, ))
    assert_true(np.all(corner_at_patch >= 0))
    assert_true(np.all(corner_at_patch < len(v.points)))
