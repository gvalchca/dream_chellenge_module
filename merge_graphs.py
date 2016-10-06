"""
Functions for merging a dictionary of netoworks into meta-network: an igraph
graph with list of attributes on edges named after the keys in the dictionary.
"""
# from operator import itemgetter
import itertools
import igraph
import operator


def merge_graphs(graphs, node_id='name', weight_attr='weight'):
    """
    Merges multiple igraph graphs into a single graph, preserving edge
    attributes.

    Note
    ----
    igraph contains a 'merge' function which achieves this functionality,
    however there currently appears to be a bug which prevents this from
    working in some cases. Once the issue has been fixed, this function will no
    longer be needed.

    Parameters
    ----------
    graphs: list
        list containing two or more igraph.Graph instances.
    node_id: str
        Node attribute containing vertex ids (default: 'name')
    weight_attr: str
        Edge attribute containing edge weights (default: 'weight')

    Return
    ------
    out: igraph.Graph
        A combined igraph object.
    """
    # create a new graph to store result of merge
    merged_graph = igraph.Graph()

    # get a list of all vertex ids
    vertex_ids = []

    for g in graphs:
        vertex_ids = vertex_ids + [vertex[node_id] for vertex in graphs[g].vs]

    vertex_ids = list(set(vertex_ids))

    # add the vertices to the network
    merged_graph.add_vertices(vertex_ids)

    # get a list of all edge IDs
    all_edges = []

    for g in graphs.keys():
        all_edges = all_edges + edges_to_tuple_list(graphs[g], g, weight_attr)

    # add the edges to the network
    add_edges_with_attr(merged_graph, merge_edge_list(all_edges))
    return merged_graph


def edges_to_tuple_list(g, attr_name, edge_attr='weight'):
    """
    Generates a list of edge tuples with metadata

    Parameters
    ----------
    g: igraph.Graph
        Graph to extract and edge tuple list for
    attr_name: str
        Name to use as key for storing edge weights in the tuples
    edge_attr: str
        Name of edge attribute to extract for each edge (default: weight)

    Return
    ------
    out: list
        List of two-element tuples containin the igraph edge tuple, plus
        associated metadata.
    """
    result = []

    for e in igraph.EdgeSeq(g):
        result.append((e.tuple, {attr_name: e[edge_attr]},))

    return result


def group_into_edge(edge_groups):
    """
    Collapse a set of edges connecting the same two vertices into a single
    edge with one attribute for each of the original edges

    Parameters
    ----------
    edge_groups: list
        List of lists where each sublist corresponds to one edge in the
        collapsed graph.

    Return
    ------
    out: tuple
        Tuple edge representation
    """
    tt = edge_groups[0][0]
    attr = {}

    for g in edge_groups:
        attr.update(g[1])

    return (tt, attr)


def merge_edge_list(all_edges):
    """
    Takes a list of edges for a multigraph and collapses each set of multiple
    edges between two nodes into a single edge with multiple attributes.

    Parameters
    ----------
    all_edges: list
        List of all of the edges for the multigraph.

    Return
    ------
    out: list
        Collapsed edgelist representation of the original multigraph.
    """
    # sort edges by first value in tuple
    all_edges.sort(key=lambda tup: tup[0])

    # get a list of edge lists grouped by the first value in tuple
    edge_groups = [list(group) for key, group in
                   itertools.groupby(all_edges, operator.itemgetter(0))]

    # collapse multiple edges between the same vertices into single edges
    # and return it
    return [group_into_edge(group) for group in edge_groups]


def add_edges_with_attr(g, edges):
    """
    Adds one or more edges, includig their attributes, to an existing graph

    Parameters
    ----------
    g: igraph.Graph
        Graph to add edges to
    edges: list
        List of edges to be added.
    """
    for e in edges:
        g.add_edge(e[0][0], e[0][1], **e[1])

