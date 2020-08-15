#!/usr/bin/env python3

def advertise(G, curr, nhop, p):
    if G.node[nhop]['as'].import_filter(p):
        G.node[nhop]['as'].unannounced_rib.append(p)

def bgp_advertise(G):
    for n in G.nodes():
        unannounced_rib = G.node[n]['as'].unannounced_rib
        announced_rib = G.node[n]['as'].announced_rib
        while unannounced_rib:
            p = unannounced_rib.pop()
            for d in G.neighbors(n):
                pp = p + (d,)
                if G.node[n]['as'].export_filter(pp):
                    advertise(G, n, d, pp)
            announced_rib.append(p)

def bgp_sim(G, iter_num=20, verbose=False):
    for i in range(iter_num):
        if verbose:
            print(i)
        bgp_advertise(G)
