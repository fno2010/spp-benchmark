#!/usr/bin/env python3
import networkx as nx

def advertise(G, curr, nhop, p):
    if G._node[nhop]['as'].import_filter(p):
        G._node[nhop]['as'].unannounced_rib.append(p)
        return True
    return False

def bgp_advertise(G, anno_cnt=0, anno_num=None):
    new_anno_cnt = anno_cnt
    stop = False
    for n in G.nodes():
        unannounced_rib = G._node[n]['as'].unannounced_rib
        announced_rib = G._node[n]['as'].announced_rib
        while unannounced_rib:
            p = unannounced_rib.pop()
            received = False
            for d in G.neighbors(n):
                pp = p + (d,)
                if G._node[n]['as'].export_filter(pp):
                    received = advertise(G, n, d, pp)
            announced_rib.append(p)
            if received:
                new_anno_cnt += 1
                if (anno_num is not None) and (new_anno_cnt >= anno_num):
                    stop = True
                    break
        if stop:
            break
    return new_anno_cnt, stop, (anno_cnt == new_anno_cnt)

def bgp_sim(G, iter_num=None, anno_num=None, verbose=False):
    if iter_num is None:
        iter_num = nx.algorithms.distance_measures.diameter(G)
    anno_cnt = 0
    stop = False
    conv = False
    for i in range(iter_num):
        if verbose:
            print('[Debug] round %d' % i)
        anno_cnt, stop, conv = bgp_advertise(G, anno_cnt=anno_cnt, anno_num=anno_num)
        if stop:
            print('[Warn] reach maximum announcement limit')
            return False
        if conv and verbose:
            print('[Debug] permitted path set converged')
    return True
