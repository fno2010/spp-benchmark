#!/usr/bin/env python3

import igraph
import networkx

TYPE_PREFERENCE = 0
TYPE_CONFLICT_I = 1
TYPE_CONFLICT_II = 2

def prefix_match(path1, path2):
    """
    check if path1 is a prefix of path2
    """
    return path1 == path2[:len(path1)]

def compatible_with_path_assign(p, pi):
    """
    check if path p is compatible with the path assignment pi
    """
    for _, pv in pi.items():
        if prefix_match(pv, p) and pi.keys().isdisjoint(p[len(pv):]):
            return True
    return False

def consistent_path(p, pset):
    """
    check if p is consistent with pset
    """
    if len(p) < 2:
        return True
    if (p in pset) and consistent_path(p[:-1], pset):
        return True
    return False

class PCGraph(networkx.MultiDiGraph):

    def __init__(self):
        self.topo = None
        networkx.MultiDiGraph.__init__(self)

    def load(self, topo):
        self.topo = topo

    def build(self):
        if not self.topo:
            return
        all_paths = []
        for asn in self.topo.nodes():
            as_paths = []
            for p in self.topo.node[asn]['as'].ranked_permitted_paths():
                self.add_node(p)
                for pp in as_paths:
                    self.add_edge(p, pp, type=TYPE_PREFERENCE)
                as_paths.append(p)
            for p in as_paths:
                for pp in all_paths:
                    if prefix_match(pp, p):
                        for cp in self.successors(pp):
                            self.add_edge(p, cp, type=TYPE_CONFLICT_I)
                        for cp in self.predecessors(pp):
                            self.add_edge(p, cp, type=TYPE_CONFLICT_I)
                        if pp == p[:-1]:
                            for cp in self.predecessors(p):
                                self.add_edge(cp, pp, type=TYPE_CONFLICT_II)
                    elif prefix_match(p, pp):
                        for cp in self.successors(p):
                            self.add_edge(pp, cp, type=TYPE_CONFLICT_I)
                        for cp in self.predecessors(p):
                            self.add_edge(pp, cp, type=TYPE_CONFLICT_I)
                        if p == pp[:-1]:
                            for cp in self.predecessors(pp):
                                self.add_edge(cp, p, type=TYPE_CONFLICT_II)
            all_paths.extend(as_paths)

class BasePCGraphSolver(object):

    def __init__(self, pcgraph=None):
        self.pcgraph = pcgraph
    
    def solve(self, pcgraph=None):
        """
        Find a max independent set.

        Override this method by your own implementation.
        """
        _pcgraph = pcgraph or self.pcgraph
        if isinstance(_pcgraph, networkx.Graph):
            _pg = networkx.Graph(_pcgraph)
            _g = networkx.relabel.convert_node_labels_to_integers(_pg, label_attribute='path')
            ig = igraph.Graph(len(_g), list(_g.edges()))
            mis = ig.largest_independent_vertex_sets()
            if mis:
                return [(0,)] + [_g.node[v]['path'] for v in mis[0]]
        else:
            return

class GreedySolver(BasePCGraphSolver):

    def solve(self, pcgraph=None):
        _pcgraph = pcgraph or self.pcgraph
        _topo = _pcgraph.topo
        P = {v:_topo.node[v]['as'].ranked_permitted_paths() for v in _topo.nodes()}
        pi = {_topo.dst: (_topo.dst,)}
        found = True
        while len(pi) < len(P) and found:
            found = False
            for v in P.keys():
                if v in pi.keys():
                    continue
                pv = None
                for p in P[v]:
                    if compatible_with_path_assign(p, pi):
                        pv = p
                        break
                if len(pv) > 1 and (pv[-2] in pi.keys()):
                    pi[v] = pv
                    found = True
        return list(pi.values())

class GreedyPlusSolver(BasePCGraphSolver):

    def solve(self, pcgraph=None):
        _pcgraph = pcgraph or self.pcgraph
        _topo = _pcgraph.topo
        P = {v:_topo.node[v]['as'].ranked_permitted_paths() for v in _topo.nodes()}
        V = list(P.keys())
        V.remove(_topo.dst)
        Vi = [_topo.dst]
        while V:
            for v in V:
                for u in Vi:
                    if len(P[u]) == 1:
                        p = P[u][0]
                        try:
                            idx = P[v].index(p+(v,))
                            P[v][idx+1:] = []
                        except ValueError:
                            pass
            Pall = sum(P.values(), [])
            for v in V:
                Pv = P[v]
                P[v] = [p for p in Pv if consistent_path(p, Pall)]
            c = None
            for v in V:
                if not P[v] or (len(P[v][0]) > 1 and (P[v][0][-2] in Vi)):
                    P[v] = P[v][:1]
                    c = v
                    break
            if c:
                V.remove(c)
                Vi.append(c)
            else:
                break
        return [P[v][0] for v in Vi if P[v]]

class GreedyPPGraphSolver(BasePCGraphSolver):

    def solve(self, pcgraph=None):
        import itertools
        _pcgraph = pcgraph or self.pcgraph
        asnum = len(_pcgraph.topo.nodes())
        s = []
        g = _pcgraph.copy()
        while len(s) < asnum and len(g.nodes()) > 0:
            # nodes with zero out degree
            b = [n for n in g.nodes() if g.out_degree(n) == 0]
            if not b:
                # nodes with no preference edge
                b = [n for n in g.nodes()
                     if all([e[2] != TYPE_PREFERENCE for e in g.out_edges(n, data='type')])
                     and all([e[2] != TYPE_PREFERENCE for e in g.in_edges(n, data='type')])]
            if not b:
                # nodes with lowest out degree
                b = min([(k[0], [n[0] for n in k[1]])
                         for k in itertools.groupby(dict(g.out_degree()).items(),
                                                    key=lambda d: d[1])],
                        key=lambda d: d[0])[1]
            g_old = g
            g = g_old.copy()
            for n in b:
                neighs = g_old.neighbors(n)
                g.remove_node(n)
                g.remove_nodes_from(neighs)
            s.extend(b)
        return s

if __name__ == '__main__':
    from spp_benchmark.reader import example_topology
    from spp_benchmark.bgp import bgp_sim
    topo = example_topology()
    bgp_sim(topo)
    pcg = PCGraph()
    pcg.load(topo)
    pcg.build()
    # baseline_solver = BasePCGraphSolver(pcg)
    # s = baseline_solver.solve()
    # print(s)
    greedy_solver = GreedySolver(pcg)
    s = greedy_solver.solve()
    print(s)
    greedyp_solver = GreedyPlusSolver(pcg)
    s = greedyp_solver.solve()
    print(s)
    greedypp_solver = GreedyPPGraphSolver(pcg)
    s = greedypp_solver.solve()
    print(s)
