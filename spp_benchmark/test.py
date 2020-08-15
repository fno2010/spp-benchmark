#!/usr/bin/env python3

import random

from spp_benchmark.reader import TopologyReader, set_dst
from spp_benchmark.pcgraph import PCGraph, GreedySolver, GreedyPlusSolver, GreedyPPGraphSolver
from spp_benchmark.bgp import bgp_sim

def test_country(topo, cc):
    dst = random.choice(list(topo.nodes()))
    set_dst(topo, dst)
    print('[[[ Country: %s, ASes: %d, Edges: %d, Dest: %d ]]]' % (cc, len(topo.nodes), len(topo.edges), dst))
    succ = bgp_sim(topo, anno_num=5000)
    if succ:
        pcg = PCGraph()
        pcg.load(topo)
        pcg.build()
        print('[[ SolverGraph: (Paths: %d, Edges: %d) ]]' % (len(pcg.nodes), len(pcg.edges)))
        s = gsolver.solve()
        print('Greedy:', s)
        s = gpsolver.solve()
        print('Greedy+:', s)
        s = gppsolver.solve()
        print('Greedy++:', s)
    print()


if __name__ == '__main__':
    import sys
    topo_reader = TopologyReader()
    as_rel_f = sys.argv[1]
    as_country_f = sys.argv[2]
    topo_reader.read_topo(as_rel_f, as_country_file=as_country_f)

    gsolver = GreedySolver()
    gpsolver = GreedyPlusSolver()
    gppsolver = GreedyPPGraphSolver()

    countries = [cc for cc, al in reversed(topo_reader.country_stat()) if al < 50]
    for cc in countries:
        topo = topo_reader.get_subtopo_by_country(cc)
        test_country(topo, cc)
