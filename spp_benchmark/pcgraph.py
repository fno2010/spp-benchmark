#!/usr/bin/env python3

import networkx

TYPE_PREFERENCE = 0
TYPE_CONFLICT_I = 1
TYPE_CONFLICT_II = 2

def prefix_match(path1, path2):
    """
    check if path1 is a prefix of path2
    """
    return path1 == path2[:len(path1)]

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
                for pp in as_paths:
                    self.add_edge(pp, p, type=TYPE_PREFERENCE)
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
            return networkx.algorithms.mis.maximal_independent_set(networkx.Graph(self.pcgraph))
        else:
            return

class GreedyPPGraphSolver(BasePCGraphSolver):

    def solve(self, pcgraph=None):
        import itertools
        _pcgraph = pcgraph or self.pcgraph
        asnum = len(_pcgraph.topo.nodes())
        s = [(_pcgraph.topo.dst,)]
        g = _pcgraph.copy()
        while len(s) < asnum and len(g.nodes()) > 0:
            b = [n for n in g.nodes() if g.out_degree(n) == 0]
            if not b:
                b = [n for n in g.nodes()
                     if any([e[2] != TYPE_PREFERENCE for e in g.out_edges(n, data='type')])
                     and any([e[2] != TYPE_PREFERENCE for e in g.in_edges(n, data)])]
            if not b:
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
    baseline_solver = BasePCGraphSolver(pcg)
    s = baseline_solver.solve()
    print(s)
    greedypp_solver = GreedyPPGraphSolver(pcg)
    s = greedypp_solver.solve()
    print(s)
