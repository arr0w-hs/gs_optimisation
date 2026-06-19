"""code for foliage partition removal and reconstruction"""
from typing import Optional
import itertools as it
import networkx as nx
# import numpy as np
import graphstate_opt as gso
import matplotlib.pyplot as plt
import numpy as np


def local_comp(in_graph, vert):
    """apply local complementation on a vertex"""
    out_graph = in_graph
    neigh = [ne for ne in out_graph.neighbors(vert)]
    neigh_combinations = it.combinations(neigh, 2)

    for u,v in neigh_combinations:
        if out_graph.has_edge(u,v):
            out_graph.remove_edge(u,v)
        else:
            out_graph.add_edge(u,v)

    return out_graph


def pick_con_node(in_adj, weights, confoliage):
    confoliage = confoliage[0]
    node = confoliage[0]

    if weights is None:
        node = confoliage[0]
    else:
        wnode = np.sum(weights[confoliage] * (in_adj[confoliage] != 0), axis=1)
        node = confoliage[np.argmin(wnode)]
    return node

def remove_duplicates(in_list: list) -> list:
    """remove duplicates from a list"""
    out_list = []
    if len(in_list)>0:
        in_list.sort()

        out_list = list(k for k,_ in it.groupby(in_list))
        out_list = sorted(out_list, key = len, reverse = True)

    return out_list


def leaf_foliage(in_graph: nx.Graph) -> list[tuple]:
    """function to recognize the leaf foliage of a given graph"""
    leaf_fol=[]
    deg_list = in_graph.degree()
    leaf_list = [i for i, deg in deg_list if deg == 1]

    for ele in leaf_list:
        neigh = in_graph.neighbors(ele)
        edge = sorted((ele, list(neigh)[0]))
        leaf_fol.append(tuple(edge))
    leaf_fol = list(set(leaf_fol))
    return leaf_fol


def not_leaf_fol(in_graph: nx.Graph) -> list:
    """list of vertices that are not leaf or axils"""

    leaf_fol = leaf_foliage(in_graph)
    leaf_fol = [item for ele in leaf_fol for item in ele]
    leaf_fol = list(set(leaf_fol))
    rem_list = [node for node in in_graph.nodes() if node not in leaf_fol]

    return rem_list

def same_neighbourhood(in_graph: nx.Graph, node1: int, node2: int) -> bool:
    """flag if two nodes have the same neighbourbood"""

    neighs1 = [node for node in nx.neighbors(in_graph, node1) if node != node2]
    neighs2 = [node for node in nx.neighbors(in_graph, node2) if node != node1]
    # if len(neighs1) or len(neighs2) == 0:
    #     return False
    # else:
    return set(neighs1) == set(neighs2)


def con_discon_foliage(in_graph: nx.Graph) -> tuple[list[list]]:
    """find tree, connected and disconnected foliage"""

    def clean_fol(fol_list):
        fol_list = [list(sorted(ele)) for ele in fol_list if len(ele)>1]
        fol_list = remove_duplicates(fol_list)
        return fol_list

    def nodes_connected(u, v):
        return u in in_graph.neighbors(v)

    discon_foliage = []
    con_foliage = []
    rem_vert = not_leaf_fol(in_graph)

    for node1 in rem_vert:
        discon_list = [node1]
        con_list = [node1]

        for node2 in rem_vert:
            if node2 == node1:
                continue
            if not same_neighbourhood(in_graph, node1, node2):
                continue

            target = con_list if nodes_connected(node1, node2) else discon_list
            target.append(node2)

        discon_foliage.append(discon_list)
        con_foliage.append(con_list)

    discon_foliage = clean_fol(discon_foliage)
    con_foliage = clean_fol(con_foliage)


    return con_foliage, discon_foliage


def remove_leaf_fol(in_graph: nx.Graph) -> tuple[nx.Graph, int, dict[str, list]]:
    """remove leaf foliage"""
    cz_count = 0
    operations = []
    leaf_fol = leaf_foliage(in_graph)
    # print(leaf_fol)
    # for edge in leaf_fol:
    #     # print(edge)

    #     in_graph.remove_edge(edge[0], edge[1])
    #     operations.append(("CZ", edge[0], edge[1]))
    #     cz_count += 1
    # # operations = operations[::-1]

    return in_graph


def convert_con_fol(in_graph: nx.Graph) -> tuple[nx.Graph, int, dict[str, list]]:
    """remove connected foliage"""

    confoliage, _ = con_discon_foliage(in_graph)
    # print(confoliage)

    # for foliage in confoliage:
    if len(confoliage)>0:
        foliage = confoliage[0]
        node = foliage[0]
        in_graph = local_comp(in_graph, node)
        # operations.append(('lcomp', [node]))


    return in_graph


def convert_discon_fol(in_graph: nx.Graph) -> tuple[nx.Graph, int, dict[str, list]]:
    """remove disconnected foliage"""

    _, discon_foliage = con_discon_foliage(in_graph)
    # print(discon_foliage)

    # for foliage in discon_foliage:
    #     print(foliage)
    if len(discon_foliage)>0:
        foliage = discon_foliage[0]
        node = foliage[0]

        if len(list(in_graph.neighbors(node))) == 0:
            return in_graph


        neigh =  list(in_graph.neighbors(node))[0]
        in_graph = local_comp(in_graph, neigh)
        in_graph = local_comp(in_graph, node)
        # operations.append(("lcomp", [neigh]))
        # operations.append(("lcomp", [node]))

    return in_graph


def find_foliage(in_graph: nx.Graph) -> tuple[nx.Graph, int, dict[str, list]]:
    """remove one round of foliage"""

    out_graph = in_graph.copy()

    for _ in range(10):
        out_graph = remove_leaf_fol(in_graph)
        out_graph = convert_con_fol(out_graph)
        out_graph = convert_discon_fol(out_graph)

    return out_graph


if __name__ == "__main__":
    import random
    import cProfile, pstats

    for _ in range(1):

        n = 10
        g = nx.complete_bipartite_graph(5,5)
        # g = nx.erdos_renyi_graph(n, 0.5)
        print("Initial edges", g.number_of_edges())
        g1 = g.copy()


        gout = find_foliage(g.copy())
        plt.figure()
        nx.draw_networkx(gout)


    plt.show()