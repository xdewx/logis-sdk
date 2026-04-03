import networkx as nx

from logis.data_type import Point


def test_remove_edge():
    graph = nx.DiGraph()
    graph.add_edge(Point(0, 0), Point(1, 1))
    graph.add_edge(Point(1, 1), Point(0, 0))
    graph.add_edge(Point(1, 1), Point(2, 2))
    graph.add_edge(Point(1, 1), Point(3, 3))
    graph.remove_edge(Point(1, 1), Point(0, 0))
    assert len(graph.edges) == 3
